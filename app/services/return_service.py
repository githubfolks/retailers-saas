from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.order import Order
from app.models.return_refund import OrderReturn, Refund, ReturnPickup, ReturnShipment, ReturnInspection
from app.models.inventory import StockLocation, StockMovement
from app.core.logger import get_logger

logger = get_logger(__name__)


class ReturnService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    # ── Request & Approval ────────────────────────────────────────────────────

    def process_return(
        self,
        order_id: int,
        quantity: int,
        reason: str,
        condition: str = "resellable",
        pickup_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a return request. Status starts at return_requested."""
        order = self.db.query(Order).filter(
            Order.id == order_id,
            Order.tenant_id == self.tenant_id,
        ).first()
        if not order:
            raise ValueError("Order not found")
        if quantity > order.quantity:
            raise ValueError("Return quantity exceeds original order quantity")

        from app.models.product import Product
        product = self.db.query(Product).filter(
            Product.tenant_id == self.tenant_id,
            Product.sku == order.sku,
        ).first()

        db_return = OrderReturn(
            tenant_id=self.tenant_id,
            order_id=order_id,
            product_id=product.id if product else None,
            quantity=quantity,
            reason=reason,
            condition=condition,
            status="return_requested",
            pickup_address=pickup_address or order.shipping_address,
        )
        self.db.add(db_return)
        self.db.commit()
        self.db.refresh(db_return)

        self._notify_customer(order, "return_requested", db_return)

        return {"status": "success", "return_id": db_return.id, "return_status": db_return.status}

    def approve_return(self, return_id: int, approved_by: str, approved: bool = True) -> Dict[str, Any]:
        """Approve or reject a return request."""
        db_return = self._get_return(return_id)

        if db_return.status != "return_requested":
            raise ValueError(f"Cannot approve a return in status '{db_return.status}'")

        db_return.status = "approved" if approved else "rejected"
        db_return.approved_by = approved_by
        db_return.approved_at = datetime.utcnow()

        order = self.db.query(Order).filter(Order.id == db_return.order_id).first()
        self.db.commit()

        self._notify_customer(order, db_return.status, db_return)

        return {"status": "success", "return_status": db_return.status}

    # ── Pickup Scheduling ─────────────────────────────────────────────────────

    def schedule_pickup(
        self,
        return_id: int,
        scheduled_date: datetime,
        pickup_address: Optional[str] = None,
        pickup_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Schedule a pickup agent to collect the item from the customer."""
        db_return = self._get_return(return_id)

        if db_return.status != "approved":
            raise ValueError("Return must be approved before scheduling a pickup")
        if db_return.pickup:
            raise ValueError("Pickup already scheduled for this return")

        address = pickup_address or db_return.pickup_address
        if not address:
            raise ValueError("Pickup address is required")

        pickup = ReturnPickup(
            tenant_id=self.tenant_id,
            return_id=return_id,
            pickup_address=address,
            scheduled_date=scheduled_date,
            pickup_agent=pickup_agent,
            status="scheduled",
        )
        self.db.add(pickup)
        db_return.status = "pickup_scheduled"
        self.db.commit()

        order = self.db.query(Order).filter(Order.id == db_return.order_id).first()
        self._notify_customer(order, "pickup_scheduled", db_return, extra={
            "scheduled_date": scheduled_date.strftime("%d %b %Y"),
            "pickup_agent": pickup_agent or "our team",
        })

        return {"status": "success", "return_status": db_return.status, "scheduled_date": scheduled_date}

    def update_pickup_status(
        self,
        return_id: int,
        status: str,
        failure_reason: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update pickup to: attempted, picked_up, failed."""
        db_return = self._get_return(return_id)
        pickup = db_return.pickup
        if not pickup:
            raise ValueError("No pickup scheduled for this return")

        valid = {"attempted", "picked_up", "failed"}
        if status not in valid:
            raise ValueError(f"Invalid pickup status. Must be one of: {valid}")

        pickup.status = status
        pickup.notes = notes

        if status == "picked_up":
            pickup.picked_up_at = datetime.utcnow()
            db_return.status = "picked_up"
        elif status == "attempted":
            pickup.attempt_count += 1
        elif status == "failed":
            pickup.failure_reason = failure_reason

        self.db.commit()

        if status == "picked_up":
            order = self.db.query(Order).filter(Order.id == db_return.order_id).first()
            self._notify_customer(order, "picked_up", db_return)

        return {"status": "success", "pickup_status": status}

    # ── Return Shipment Tracking ──────────────────────────────────────────────

    def create_return_shipment(
        self,
        return_id: int,
        carrier: str,
        tracking_number: Optional[str] = None,
        label_url: Optional[str] = None,
        receiving_warehouse_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Register the carrier and tracking details for the return journey."""
        db_return = self._get_return(return_id)

        if db_return.status not in ("picked_up", "pickup_scheduled"):
            raise ValueError("Shipment can only be created after item is picked up")
        if db_return.shipment:
            raise ValueError("Shipment already registered for this return")

        shipment = ReturnShipment(
            tenant_id=self.tenant_id,
            return_id=return_id,
            carrier=carrier,
            tracking_number=tracking_number,
            label_url=label_url,
            receiving_warehouse_id=receiving_warehouse_id,
            status="in_transit",
            shipped_at=datetime.utcnow(),
        )
        self.db.add(shipment)
        db_return.status = "in_transit"
        self.db.commit()

        order = self.db.query(Order).filter(Order.id == db_return.order_id).first()
        self._notify_customer(order, "in_transit", db_return, extra={
            "carrier": carrier,
            "tracking_number": tracking_number or "N/A",
        })

        return {"status": "success", "return_status": db_return.status, "tracking_number": tracking_number}

    def update_shipment_status(self, return_id: int, status: str) -> Dict[str, Any]:
        """Update shipment to: in_transit, received, lost."""
        db_return = self._get_return(return_id)
        shipment = db_return.shipment
        if not shipment:
            raise ValueError("No shipment found for this return")

        valid = {"in_transit", "received", "lost"}
        if status not in valid:
            raise ValueError(f"Invalid shipment status. Must be one of: {valid}")

        shipment.status = status

        if status == "received":
            shipment.received_at = datetime.utcnow()
            db_return.status = "received"

        self.db.commit()
        return {"status": "success", "shipment_status": status}

    # ── Inspection ────────────────────────────────────────────────────────────

    def record_inspection(
        self,
        return_id: int,
        condition: str,
        inspected_by: str,
        approved_for_refund: bool = True,
        refund_deduction_pct: float = 0.0,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record the warehouse inspection result and restock if resellable."""
        db_return = self._get_return(return_id)

        if db_return.status != "received":
            raise ValueError("Item must be received before inspection")
        if db_return.inspection:
            raise ValueError("Inspection already recorded for this return")

        if condition not in ("resellable", "damaged", "destroyed"):
            raise ValueError("condition must be resellable, damaged, or destroyed")

        inspection = ReturnInspection(
            tenant_id=self.tenant_id,
            return_id=return_id,
            inspected_by=inspected_by,
            condition=condition,
            approved_for_refund=approved_for_refund,
            refund_deduction_pct=refund_deduction_pct,
            notes=notes,
        )
        self.db.add(inspection)

        # Restock if resellable
        if condition == "resellable" and db_return.product_id:
            location = self.db.query(StockLocation).filter(
                StockLocation.tenant_id == self.tenant_id,
                StockLocation.product_id == db_return.product_id,
            ).first()
            if location:
                location.quantity += db_return.quantity
                self.db.add(StockMovement(
                    tenant_id=self.tenant_id,
                    product_id=db_return.product_id,
                    location_id=location.id,
                    movement_type="in",
                    quantity=db_return.quantity,
                    reason="return",
                    reference_id=str(db_return.order_id),
                    reference_type="return",
                    created_by=inspected_by,
                ))

        db_return.status = "inspected"
        self.db.commit()

        return {
            "status": "success",
            "condition": condition,
            "approved_for_refund": approved_for_refund,
            "refund_deduction_pct": refund_deduction_pct,
        }

    # ── Refund ────────────────────────────────────────────────────────────────

    def process_refund(self, return_id: int, amount: Optional[float] = None) -> Dict[str, Any]:
        """Process financial refund after inspection approval."""
        db_return = self._get_return(return_id)

        if db_return.status != "inspected":
            raise ValueError("Return must be inspected before processing refund")

        inspection = db_return.inspection
        if inspection and not inspection.approved_for_refund:
            raise ValueError("Refund was not approved during inspection")

        order = self.db.query(Order).filter(Order.id == db_return.order_id).first()
        base_amount = amount or (order.unit_price * db_return.quantity)

        if inspection and inspection.refund_deduction_pct > 0:
            base_amount = base_amount * (1 - inspection.refund_deduction_pct / 100)

        db_refund = Refund(
            tenant_id=self.tenant_id,
            order_id=order.id,
            amount=round(base_amount, 2),
            refund_method="original_payment",
            status="completed",
            processed_at=datetime.utcnow(),
        )
        self.db.add(db_refund)

        db_return.refund_id = db_refund.id
        db_return.status = "completed"
        db_return.completed_at = datetime.utcnow()

        if db_return.quantity == order.quantity:
            order.status = "returned"
        else:
            order.status = "partially_returned"

        self.db.commit()
        self.db.refresh(db_refund)

        self._notify_customer(order, "completed", db_return, extra={"amount": round(base_amount, 2)})

        return {"status": "success", "refund_id": db_refund.id, "amount": db_refund.amount}

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_return(self, return_id: int) -> OrderReturn:
        db_return = self.db.query(OrderReturn).filter(
            OrderReturn.id == return_id,
            OrderReturn.tenant_id == self.tenant_id,
        ).first()
        if not db_return:
            raise ValueError("Return not found")
        return db_return

    def _notify_customer(
        self,
        order: Order,
        event: str,
        db_return: OrderReturn,
        extra: Optional[Dict] = None,
    ) -> None:
        """Send email to customer at key return milestones."""
        try:
            from app.models.customer import Customer
            from app.integrations.email_sender import send_email

            customer = self.db.query(Customer).filter(
                Customer.id == order.customer_id
            ).first() if order.customer_id else None

            to_email = getattr(customer, "email", None)
            if not to_email:
                return

            subjects = {
                "return_requested": "Return Request Received",
                "approved":         "Your Return Has Been Approved",
                "rejected":         "Return Request Update",
                "pickup_scheduled": "Pickup Scheduled for Your Return",
                "picked_up":        "Your Return Has Been Picked Up",
                "in_transit":       "Return Shipment In Transit",
                "completed":        "Refund Processed for Your Return",
            }
            subject = f"Order #{order.id} — {subjects.get(event, 'Return Update')}"
            html_body = self._build_email_body(order, event, db_return, extra or {})
            send_email(to_email=to_email, subject=subject, html_body=html_body)

        except Exception as e:
            logger.error(f"Failed to send return notification for order {order.id}: {e}")

    def _build_email_body(
        self,
        order: Order,
        event: str,
        db_return: OrderReturn,
        extra: Dict,
    ) -> str:
        messages = {
            "return_requested": "We have received your return request and will review it shortly.",
            "approved":         "Great news! Your return request has been approved. We will schedule a pickup soon.",
            "rejected":         "Unfortunately, your return request could not be approved. Please contact support for more details.",
            "pickup_scheduled": (
                f"A pickup has been scheduled for <strong>{extra.get('scheduled_date', '')}</strong> "
                f"by <strong>{extra.get('pickup_agent', 'our team')}</strong>. Please keep the item ready."
            ),
            "picked_up":        "Your item has been picked up and is on its way back to us.",
            "in_transit":       (
                f"Your return is in transit via <strong>{extra.get('carrier', '')}</strong>. "
                f"Tracking: <strong>{extra.get('tracking_number', 'N/A')}</strong>"
            ),
            "completed":        (
                f"Your refund of <strong>₹{extra.get('amount', '')}</strong> has been processed "
                "and will reflect in your account within 5–7 business days."
            ),
        }
        body_text = messages.get(event, "There has been an update to your return.")

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
            <div style="background:#0d9488; padding:20px; border-radius:8px 8px 0 0;">
                <h2 style="color:#fff; margin:0;">Return Update — Order #{order.id}</h2>
            </div>
            <div style="border:1px solid #e5e7eb; border-top:none; padding:24px; border-radius:0 0 8px 8px;">
                <p>{body_text}</p>
                <table style="width:100%; border-collapse:collapse; margin:16px 0;">
                    <tr style="background:#f9fafb;">
                        <td style="padding:10px; border:1px solid #e5e7eb; font-weight:bold;">Order ID</td>
                        <td style="padding:10px; border:1px solid #e5e7eb;">#{order.id}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #e5e7eb; font-weight:bold;">Return ID</td>
                        <td style="padding:10px; border:1px solid #e5e7eb;">#{db_return.id}</td>
                    </tr>
                    <tr style="background:#f9fafb;">
                        <td style="padding:10px; border:1px solid #e5e7eb; font-weight:bold;">Return Status</td>
                        <td style="padding:10px; border:1px solid #e5e7eb;">{db_return.status.replace("_", " ").title()}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #e5e7eb; font-weight:bold;">Quantity</td>
                        <td style="padding:10px; border:1px solid #e5e7eb;">{db_return.quantity}</td>
                    </tr>
                    <tr style="background:#f9fafb;">
                        <td style="padding:10px; border:1px solid #e5e7eb; font-weight:bold;">Reason</td>
                        <td style="padding:10px; border:1px solid #e5e7eb;">{db_return.reason}</td>
                    </tr>
                </table>
                <p style="color:#6b7280; font-size:12px; margin-top:32px;">
                    This is an automated message. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
