from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.api.auth import get_current_tenant_id
from app.services.return_service import ReturnService
from app.models.return_refund import OrderReturn, Refund, ReturnPickup, ReturnShipment, ReturnInspection

router = APIRouter(prefix="/returns", tags=["returns"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ReturnRequest(BaseModel):
    order_id: int
    quantity: int
    reason: str
    condition: str = "resellable"
    pickup_address: Optional[str] = None


class ReturnApprovalRequest(BaseModel):
    approved_by: str
    approved: bool = True


class PickupScheduleRequest(BaseModel):
    scheduled_date: datetime
    pickup_address: Optional[str] = None
    pickup_agent: Optional[str] = None


class PickupStatusUpdate(BaseModel):
    status: str                        # attempted | picked_up | failed
    failure_reason: Optional[str] = None
    notes: Optional[str] = None


class ShipmentRequest(BaseModel):
    carrier: str
    tracking_number: Optional[str] = None
    label_url: Optional[str] = None
    receiving_warehouse_id: Optional[int] = None


class ShipmentStatusUpdate(BaseModel):
    status: str                        # in_transit | received | lost


class InspectionRequest(BaseModel):
    condition: str                     # resellable | damaged | destroyed
    inspected_by: str
    approved_for_refund: bool = True
    refund_deduction_pct: float = 0.0
    notes: Optional[str] = None


class RefundRequest(BaseModel):
    return_id: int
    amount: Optional[float] = None


# ── Return Request & Approval ─────────────────────────────────────────────────

@router.post("/")
async def create_return(
    req: ReturnRequest,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Initiate a return request."""
    try:
        service = ReturnService(db, current_tenant_id)
        return service.process_return(
            req.order_id, req.quantity, req.reason, req.condition, req.pickup_address
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{return_id}/approve")
async def approve_return(
    return_id: int,
    req: ReturnApprovalRequest,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Approve or reject a return request."""
    import asyncio
    from app.models.order import Order
    from app.models.tenant import Tenant
    from app.services.whatsapp_bot_service import WhatsAppBotService

    try:
        service = ReturnService(db, current_tenant_id)
        result = service.approve_return(return_id, req.approved_by, req.approved)

        db_return = db.query(OrderReturn).filter(OrderReturn.id == return_id).first()
        if db_return:
            order = db.query(Order).filter(Order.id == db_return.order_id).first()
            tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
            if order and tenant and order.customer_mobile:
                if req.approved:
                    asyncio.create_task(WhatsAppBotService.send_return_approved(
                        tenant, order.customer_mobile, return_id
                    ))
                else:
                    asyncio.create_task(WhatsAppBotService.send_return_rejected(
                        tenant, order.customer_mobile, return_id,
                        "Does not meet our return policy criteria"
                    ))

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Pickup ────────────────────────────────────────────────────────────────────

@router.post("/{return_id}/pickup")
async def schedule_pickup(
    return_id: int,
    req: PickupScheduleRequest,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Schedule a pickup agent to collect the item from the customer."""
    import asyncio
    from app.models.order import Order
    from app.models.tenant import Tenant
    from app.services.whatsapp_bot_service import WhatsAppBotService

    try:
        service = ReturnService(db, current_tenant_id)
        result = service.schedule_pickup(
            return_id, req.scheduled_date, req.pickup_address, req.pickup_agent
        )

        db_return = db.query(OrderReturn).filter(OrderReturn.id == return_id).first()
        if db_return:
            order = db.query(Order).filter(Order.id == db_return.order_id).first()
            tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
            if order and tenant and order.customer_mobile:
                pickup_date = req.scheduled_date.strftime("%d %b %Y, %I:%M %p")
                asyncio.create_task(WhatsAppBotService.send_return_pickup_scheduled(
                    tenant, order.customer_mobile, return_id, pickup_date
                ))

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{return_id}/pickup")
async def update_pickup_status(
    return_id: int,
    req: PickupStatusUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Update pickup status: attempted | picked_up | failed."""
    try:
        service = ReturnService(db, current_tenant_id)
        return service.update_pickup_status(
            return_id, req.status, req.failure_reason, req.notes
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{return_id}/pickup")
async def get_pickup(
    return_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Get pickup details for a return."""
    pickup = db.query(ReturnPickup).join(OrderReturn).filter(
        ReturnPickup.return_id == return_id,
        OrderReturn.tenant_id == current_tenant_id,
    ).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="No pickup found for this return")
    return pickup


# ── Shipment Tracking ─────────────────────────────────────────────────────────

@router.post("/{return_id}/shipment")
async def create_shipment(
    return_id: int,
    req: ShipmentRequest,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Register carrier and tracking number for the return shipment."""
    try:
        service = ReturnService(db, current_tenant_id)
        return service.create_return_shipment(
            return_id, req.carrier, req.tracking_number,
            req.label_url, req.receiving_warehouse_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{return_id}/shipment")
async def update_shipment_status(
    return_id: int,
    req: ShipmentStatusUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Update shipment status: in_transit | received | lost."""
    try:
        service = ReturnService(db, current_tenant_id)
        return service.update_shipment_status(return_id, req.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{return_id}/shipment")
async def get_shipment(
    return_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Get return shipment details."""
    shipment = db.query(ReturnShipment).join(OrderReturn).filter(
        ReturnShipment.return_id == return_id,
        OrderReturn.tenant_id == current_tenant_id,
    ).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="No shipment found for this return")
    return shipment


# ── Inspection ────────────────────────────────────────────────────────────────

@router.post("/{return_id}/inspection")
async def record_inspection(
    return_id: int,
    req: InspectionRequest,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Record warehouse inspection result once item is received."""
    try:
        service = ReturnService(db, current_tenant_id)
        return service.record_inspection(
            return_id, req.condition, req.inspected_by,
            req.approved_for_refund, req.refund_deduction_pct, req.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{return_id}/inspection")
async def get_inspection(
    return_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Get inspection record for a return."""
    inspection = db.query(ReturnInspection).join(OrderReturn).filter(
        ReturnInspection.return_id == return_id,
        OrderReturn.tenant_id == current_tenant_id,
    ).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="No inspection found for this return")
    return inspection


# ── Refund ────────────────────────────────────────────────────────────────────

@router.post("/refund")
async def process_refund(
    req: RefundRequest,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Process financial refund after inspection approval."""
    import asyncio
    from app.models.order import Order
    from app.models.tenant import Tenant
    from app.services.whatsapp_bot_service import WhatsAppBotService

    try:
        service = ReturnService(db, current_tenant_id)
        result = service.process_refund(req.return_id, req.amount)

        db_return = db.query(OrderReturn).filter(OrderReturn.id == req.return_id).first()
        if db_return and db_return.refund:
            order = db.query(Order).filter(Order.id == db_return.order_id).first()
            tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
            if order and tenant and order.customer_mobile:
                refund_amount = db_return.refund.amount or req.amount or 0
                asyncio.create_task(WhatsAppBotService.send_refund_processed(
                    tenant, order.customer_mobile, req.return_id,
                    refund_amount, db_return.refund.refund_method or "original payment"
                ))

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Listing ───────────────────────────────────────────────────────────────────

@router.get("/")
async def list_returns(
    status: Optional[str] = None,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """List all returns for the tenant, optionally filtered by status."""
    query = db.query(OrderReturn).filter(OrderReturn.tenant_id == current_tenant_id)
    if status:
        query = query.filter(OrderReturn.status == status)
    return query.order_by(OrderReturn.return_date.desc()).all()


@router.get("/{return_id}")
async def get_return(
    return_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Get full return detail including pickup, shipment, and inspection."""
    db_return = db.query(OrderReturn).filter(
        OrderReturn.id == return_id,
        OrderReturn.tenant_id == current_tenant_id,
    ).first()
    if not db_return:
        raise HTTPException(status_code=404, detail="Return not found")
    return {
        "return": db_return,
        "pickup": db_return.pickup,
        "shipment": db_return.shipment,
        "inspection": db_return.inspection,
        "refund": db_return.refund,
    }
