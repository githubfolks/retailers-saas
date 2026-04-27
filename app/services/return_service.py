from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.order import Order
from app.models.return_refund import OrderReturn, Refund
from app.models.inventory import StockLocation, StockMovement
from app.core.logger import get_logger

logger = get_logger(__name__)

class ReturnService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def process_return(self, order_id: int, quantity: int, reason: str, condition: str = "resellable") -> Dict[str, Any]:
        """
        Process a product return.
        1. Create Return record
        2. Adjust Inventory (if resellable)
        3. Update Order status
        """
        order = self.db.query(Order).filter(
            Order.id == order_id, 
            Order.tenant_id == self.tenant_id
        ).first()
        
        if not order:
            raise ValueError("Order not found")
        
        if quantity > order.quantity:
            raise ValueError("Return quantity exceeds original order quantity")

        # 1. Create Return Record
        db_return = OrderReturn(
            tenant_id=self.tenant_id,
            order_id=order_id,
            quantity=quantity,
            reason=reason,
            condition=condition,
            status="received"
        )
        self.db.add(db_return)
        
        # 2. Adjust Inventory
        # Find stock location for this product (using SKU)
        # Note: In a real system we'd need to find the specific product_id from the SKU
        from app.models.product import Product
        product = self.db.query(Product).filter(
            Product.tenant_id == self.tenant_id,
            Product.sku == order.sku
        ).first()
        
        if product and condition == "resellable":
            location = self.db.query(StockLocation).filter(
                StockLocation.tenant_id == self.tenant_id,
                StockLocation.product_id == product.id
            ).first()
            
            if location:
                location.quantity += quantity
                
                # Log Movement
                movement = StockMovement(
                    tenant_id=self.tenant_id,
                    product_id=product.id,
                    location_id=location.id,
                    movement_type="in",
                    quantity=quantity,
                    reason="return",
                    reference_id=str(order_id),
                    reference_type="return",
                    created_by="system"
                )
                self.db.add(movement)
        
        # 3. Update Order Status
        if quantity == order.quantity:
            order.status = "returned"
        else:
            order.status = "partially_returned"
            
        self.db.commit()
        self.db.refresh(db_return)
        
        return {
            "status": "success",
            "return_id": db_return.id,
            "order_status": order.status
        }

    def process_refund(self, return_id: int, amount: Optional[float] = None) -> Dict[str, Any]:
        """Process financial refund for a return."""
        db_return = self.db.query(OrderReturn).filter(
            OrderReturn.id == return_id,
            OrderReturn.tenant_id == self.tenant_id
        ).first()
        
        if not db_return:
            raise ValueError("Return record not found")
        
        order = self.db.query(Order).filter(Order.id == db_return.order_id).first()
        refund_amount = amount or (order.unit_price * db_return.quantity)
        
        db_refund = Refund(
            tenant_id=self.tenant_id,
            order_id=order.id,
            amount=refund_amount,
            refund_method="original_payment",
            status="completed",
            processed_at=datetime.utcnow()
        )
        self.db.add(db_refund)
        
        db_return.refund_id = db_refund.id
        db_return.status = "refunded"
        
        self.db.commit()
        self.db.refresh(db_refund)
        
        return {
            "status": "success",
            "refund_id": db_refund.id,
            "amount": refund_amount
        }
