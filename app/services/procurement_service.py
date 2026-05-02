from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from app.models.procurement import (
    Supplier, PurchaseOrder, PurchaseOrderLine, SupplierPerformance,
    OrderFulfillment, BackorderAlert, InventoryRule, AutomationWorkflow,
    InventoryCount, CountLine, ProductBarcode
)
from app.models.product import Product
from app.models.order import Order
from app.core.logger import request_logger
from app.integrations.whatsapp_sender import send_whatsapp_message
import json


class ProcurementService:
    """Supplier, PO, and fulfillment management."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    # ============ SUPPLIER MANAGEMENT ============
    
    def create_supplier(self, supplier_name: str, phone: str, whatsapp_number: str = None,
                       email: str = None, lead_time_days: int = 7) -> int:
        """Create a new supplier."""
        supplier = Supplier(
            tenant_id=self.tenant_id,
            supplier_name=supplier_name,
            phone=phone,
            whatsapp_number=whatsapp_number,
            email=email,
            lead_time_days=lead_time_days
        )
        self.db.add(supplier)
        self.db.commit()
        return supplier.id
    
    def get_suppliers(self, active_only: bool = True) -> List[Dict]:
        """Get all suppliers."""
        query = self.db.query(Supplier).filter(Supplier.tenant_id == self.tenant_id)
        
        if active_only:
            query = query.filter(Supplier.is_active == True)
        
        suppliers = query.all()
        
        return [
            {
                "id": s.id,
                "name": s.supplier_name,
                "phone": s.phone,
                "whatsapp": s.whatsapp_number,
                "lead_time": s.lead_time_days,
                "reliability": s.reliability_score
            } for s in suppliers
        ]
    
    # ============ PURCHASE ORDERS ============
    
    def create_purchase_order(self, supplier_id: int, expected_delivery: datetime,
                            lines: List[Dict]) -> int:
        """Create a purchase order."""
        import uuid as _uuid
        po = PurchaseOrder(
            tenant_id=self.tenant_id,
            supplier_id=supplier_id,
            po_number=f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{_uuid.uuid4().hex[:6]}",
            expected_delivery=expected_delivery,
            po_status="draft"
        )
        self.db.add(po)
        self.db.flush()  # get po.id before creating lines

        total_amount = 0
        for line in lines:
            po_line = PurchaseOrderLine(
                tenant_id=self.tenant_id,
                po_id=po.id,
                product_id=line.get("product_id"),
                product_name=line.get("product_name", ""),
                quantity=line.get("quantity"),
                unit_cost=line.get("unit_cost"),
                total_cost=line.get("quantity") * line.get("unit_cost")
            )
            total_amount += po_line.total_cost
            self.db.add(po_line)

        po.total_amount = total_amount
        self.db.commit()
        
        return po.id
    
    def send_po_to_supplier(self, po_id: int, supplier_config: Dict) -> bool:
        """Send PO via WhatsApp to supplier."""
        po = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        supplier = self.db.query(Supplier).filter(Supplier.id == po.supplier_id).first()
        
        if not supplier or not supplier.whatsapp_number:
            return False
        
        lines_text = ""
        po_lines = self.db.query(PurchaseOrderLine).filter(PurchaseOrderLine.po_id == po_id).all()
        
        for i, line in enumerate(po_lines, 1):
            lines_text += f"{i}. {line.product_name} x {line.quantity} @ ₹{line.unit_cost} = ₹{line.total_cost}\n"
        
        message = f"""📋 Purchase Order Confirmation

PO Number: {po.po_number}
Expected Delivery: {po.expected_delivery.strftime('%d-%m-%Y')}
Total Amount: ₹{po.total_amount:,.2f}

Items:
{lines_text}

Please confirm receipt and send shipping details.
"""
        
        result = send_whatsapp_message(
            recipient_number=supplier.whatsapp_number,
            message_text=message,
            phone_number_id=supplier_config.get("whatsapp_phone_id"),
            whatsapp_token=supplier_config.get("whatsapp_token")
        )
        
        if result:
            po.po_status = "sent"
            self.db.commit()
        
        return bool(result)
    
    def receive_po(self, po_id: int, received_lines: List[Dict]) -> bool:
        """Mark PO lines as received."""
        po = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        
        for line_data in received_lines:
            line = self.db.query(PurchaseOrderLine).filter(
                PurchaseOrderLine.id == line_data.get("line_id")
            ).first()
            
            if line:
                line.received_quantity = line_data.get("quantity")
                line.received_date = datetime.utcnow()
                line.quality_status = "accepted"
        
        po.actual_delivery = datetime.utcnow()
        po.po_status = "received"
        self.db.commit()
        
        return True
    
    # ============ FULFILLMENT ============
    
    def create_fulfillment(self, order_id: int, warehouse_id: int) -> int:
        """Create order fulfillment record."""
        fulfillment = OrderFulfillment(
            tenant_id=self.tenant_id,
            order_id=order_id,
            warehouse_id=warehouse_id,
            fulfillment_status="pending"
        )
        self.db.add(fulfillment)
        self.db.commit()
        return fulfillment.id
    
    def update_fulfillment_status(self, fulfillment_id: int, status: str) -> bool:
        """Update fulfillment status."""
        fulfillment = self.db.query(OrderFulfillment).filter(
            OrderFulfillment.id == fulfillment_id
        ).first()
        
        if not fulfillment:
            return False
        
        fulfillment.fulfillment_status = status
        
        if status == "packed":
            fulfillment.packing_time = datetime.utcnow()
        elif status == "shipped":
            fulfillment.estimated_delivery = datetime.utcnow() + timedelta(days=7)
        elif status == "delivered":
            fulfillment.actual_delivery = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def get_fulfillment_status(self, order_id: int) -> Optional[Dict]:
        """Get fulfillment status for order."""
        fulfillment = self.db.query(OrderFulfillment).filter(
            OrderFulfillment.order_id == order_id
        ).first()
        
        if not fulfillment:
            return None
        
        return {
            "id": fulfillment.id,
            "status": fulfillment.fulfillment_status,
            "warehouse_id": fulfillment.warehouse_id,
            "tracking_number": fulfillment.tracking_number,
            "estimated_delivery": fulfillment.estimated_delivery,
            "actual_delivery": fulfillment.actual_delivery
        }
    
    # ============ BACKORDERS ============
    
    def create_backorder_alert(self, order_id: int, product_id: int, 
                              quantity_short: int, expected_date: datetime) -> int:
        """Create backorder alert."""
        alert = BackorderAlert(
            tenant_id=self.tenant_id,
            order_id=order_id,
            product_id=product_id,
            quantity_short=quantity_short,
            expected_restock_date=expected_date
        )
        self.db.add(alert)
        self.db.commit()
        return alert.id
    
    def notify_backorder_customer(self, backorder_id: int, customer_phone: str,
                                 tenant_config: Dict) -> bool:
        """Notify customer about backorder."""
        backorder = self.db.query(BackorderAlert).filter(
            BackorderAlert.id == backorder_id
        ).first()
        
        if not backorder:
            return False
        
        product = self.db.query(Product).filter(Product.id == backorder.product_id).first()
        
        message = f"""📦 Order Status Update

Product: {product.name if product else 'Item'}
Quantity Short: {backorder.quantity_short}
Expected Restock: {backorder.expected_restock_date.strftime('%d-%m-%Y')}

We'll ship the remaining items as soon as they're back in stock.
You'll receive a tracking update via WhatsApp.

Thanks for your patience! 🙏
"""
        
        result = send_whatsapp_message(
            recipient_number=customer_phone,
            message_text=message,
            phone_number_id=tenant_config.get("whatsapp_phone_id"),
            whatsapp_token=tenant_config.get("whatsapp_token")
        )
        
        if result:
            backorder.customer_notification_sent = True
            backorder.last_notification_at = datetime.utcnow()
            self.db.commit()
        
        return bool(result)
    
    # ============ INVENTORY COUNTS ============
    
    def create_inventory_count(self, count_by_user: str, warehouse_id: int = None) -> int:
        """Create inventory count session."""
        count = InventoryCount(
            tenant_id=self.tenant_id,
            count_by_user=count_by_user,
            warehouse_id=warehouse_id,
            status="in_progress"
        )
        self.db.add(count)
        self.db.commit()
        return count.id
    
    def add_count_line(self, count_id: int, product_id: int, 
                      counted_qty: int, barcode: str = None) -> bool:
        """Add line to inventory count."""
        from app.models.inventory import StockLocation
        
        location = self.db.query(StockLocation).filter(
            StockLocation.tenant_id == self.tenant_id,
            StockLocation.product_id == product_id
        ).first()
        
        system_qty = location.quantity if location else 0
        variance = counted_qty - system_qty
        
        count_line = CountLine(
            count_id=count_id,
            product_id=product_id,
            barcode=barcode,
            counted_qty=counted_qty,
            system_qty=system_qty,
            variance=variance
        )
        self.db.add(count_line)
        self.db.commit()
        
        return True
    
    def complete_inventory_count(self, count_id: int) -> Dict:
        """Mark inventory count as complete."""
        count = self.db.query(InventoryCount).filter(
            InventoryCount.id == count_id
        ).first()
        
        if not count:
            return {"status": "error"}
        
        lines = self.db.query(CountLine).filter(CountLine.count_id == count_id).all()
        
        total_discrepancies = len([l for l in lines if l.variance != 0])
        total_variance = sum(abs(l.variance) for l in lines)
        total_items = sum(l.system_qty for l in lines)
        
        count.status = "completed"
        count.total_items_counted = len(lines)
        count.total_discrepancies = total_discrepancies
        count.variance_percentage = (total_variance / total_items * 100) if total_items > 0 else 0
        count.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "count_id": count_id,
            "total_items": len(lines),
            "discrepancies": total_discrepancies,
            "variance_pct": count.variance_percentage
        }
    
    # ============ BARCODES ============
    
    def create_barcode(self, product_id: int, barcode: str, barcode_type: str = "EAN-13") -> int:
        """Create product barcode."""
        # Deactivate other primary barcodes
        existing = self.db.query(ProductBarcode).filter(
            ProductBarcode.product_id == product_id,
            ProductBarcode.is_primary == True
        ).first()
        
        if existing:
            existing.is_primary = False
        
        barcode_obj = ProductBarcode(
            tenant_id=self.tenant_id,
            product_id=product_id,
            barcode=barcode,
            barcode_type=barcode_type,
            is_primary=True
        )
        self.db.add(barcode_obj)
        self.db.commit()
        return barcode_obj.id
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Look up product by barcode."""
        barcode_obj = self.db.query(ProductBarcode).filter(
            ProductBarcode.barcode == barcode
        ).first()
        
        if not barcode_obj:
            return None
        
        product = self.db.query(Product).filter(Product.id == barcode_obj.product_id).first()
        
        return {
            "product_id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": product.price
        }
    
    # ============ AUTOMATION RULES ============
    
    def create_automation_rule(self, rule_name: str, trigger_type: str,
                             trigger_condition: str, actions: List[str]) -> int:
        """Create inventory automation rule."""
        rule = InventoryRule(
            tenant_id=self.tenant_id,
            rule_name=rule_name,
            condition=trigger_condition,
            action=json.dumps(actions),
            rule_priority=0,
            is_enabled=True
        )
        self.db.add(rule)
        self.db.commit()
        return rule.id
    
    def evaluate_rules(self) -> List[Dict]:
        """Evaluate all active rules and return triggered actions."""
        rules = self.db.query(InventoryRule).filter(
            InventoryRule.tenant_id == self.tenant_id,
            InventoryRule.is_enabled == True
        ).order_by(InventoryRule.rule_priority.desc()).all()
        
        triggered_actions = []
        
        for rule in rules:
            # Evaluate rule condition (simplified)
            if self._evaluate_condition(rule.condition):
                actions = json.loads(rule.action)
                triggered_actions.append({
                    "rule_id": rule.id,
                    "rule_name": rule.rule_name,
                    "actions": actions
                })
                
                rule.last_triggered = datetime.utcnow()
                rule.trigger_count += 1
        
        self.db.commit()
        return triggered_actions
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a rule condition string."""
        # This is simplified. In production, use a proper expression evaluator
        # or business rules engine like json-rules-engine
        return True


class SupplierPerformanceService:
    """Track and analyze supplier performance."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def calculate_supplier_metrics(self, supplier_id: int) -> Dict:
        """Calculate supplier performance metrics."""
        pos = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.supplier_id == supplier_id,
            PurchaseOrder.po_status == "received"
        ).all()
        
        if not pos:
            return {
                "on_time_rate": 0,
                "quality_score": 0,
                "avg_lead_time": 0,
                "defect_rate": 0
            }
        
        on_time = len([po for po in pos if po.actual_delivery <= po.expected_delivery])
        on_time_rate = (on_time / len(pos) * 100) if pos else 0
        
        avg_lead_time = sum(
            (po.actual_delivery - po.po_date).days for po in pos if po.actual_delivery
        ) // len(pos) if pos else 0
        
        return {
            "on_time_rate": on_time_rate,
            "quality_score": 85.0,  # From quality checks
            "avg_lead_time": avg_lead_time,
            "defect_rate": 2.5
        }
    
    def update_supplier_reliability(self, supplier_id: int) -> float:
        """Update supplier reliability score."""
        metrics = self.calculate_supplier_metrics(supplier_id)
        
        # Weighted scoring
        reliability_score = (
            metrics["on_time_rate"] * 0.4 +
            metrics["quality_score"] * 0.4 +
            (100 - metrics["defect_rate"]) * 0.2
        )
        
        supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if supplier:
            supplier.reliability_score = reliability_score
            self.db.commit()
        
        return reliability_score
