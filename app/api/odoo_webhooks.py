from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.core.logger import request_logger
from app.services.inventory_service import InventoryService
from app.models.product import Product
from app.models.inventory import StockLocation, StockMovement
from datetime import datetime


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/odoo/stock-update")
async def odoo_stock_update(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Receive real-time stock updates from Odoo.
    Expected payload:
    {
        "tenant_id": "...",
        "product_id": 123,
        "warehouse_id": 456,
        "quantity": 100,
        "movement_type": "stock_move",
        "reason": "inventory_adjustment"
    }
    """
    try:
        tenant_id = payload.get("tenant_id")
        product_id = payload.get("product_id")
        quantity = payload.get("quantity", 0)
        warehouse_id = payload.get("warehouse_id")
        movement_type = payload.get("movement_type", "stock_move")
        reason = payload.get("reason", "odoo_sync")
        
        if not tenant_id or not product_id:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Get or create stock location
        location = db.query(StockLocation).filter(
            StockLocation.tenant_id == tenant_id,
            StockLocation.product_id == product_id
        ).first()
        
        if not location:
            location = StockLocation(
                tenant_id=tenant_id,
                product_id=product_id,
                warehouse_id=warehouse_id,
                quantity=quantity,
                available_quantity=quantity,
                reserved_quantity=0
            )
            db.add(location)
        else:
            old_qty = location.quantity
            location.quantity = quantity
            location.available_quantity = max(0, quantity - location.reserved_quantity)
            
            # Log movement
            qty_change = quantity - old_qty
            if qty_change != 0:
                movement = StockMovement(
                    tenant_id=tenant_id,
                    product_id=product_id,
                    location_id=location.id,
                    movement_type="in" if qty_change > 0 else "out",
                    quantity=abs(qty_change),
                    reason=reason,
                    created_by="odoo_webhook"
                )
                db.add(movement)
        
        location.last_stock_check = datetime.utcnow()
        db.commit()
        
        # Check for alerts
        service = InventoryService(db, tenant_id)
        service.check_and_create_alerts(product_id)
        
        request_logger.info(f"Stock update from Odoo: Product {product_id}, Qty: {quantity}")
        
        return {
            "status": "success",
            "message": "Stock updated",
            "product_id": product_id,
            "new_quantity": quantity
        }
    
    except Exception as e:
        request_logger.error(f"Odoo webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/odoo/order-confirmation")
async def odoo_order_confirmation(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Receive order confirmations from Odoo.
    Expected payload:
    {
        "tenant_id": "...",
        "order_id": 123,
        "status": "confirmed",
        "items": [
            {"product_id": 1, "quantity": 10},
            {"product_id": 2, "quantity": 5}
        ]
    }
    """
    try:
        tenant_id = payload.get("tenant_id")
        order_id = payload.get("order_id")
        status = payload.get("status", "confirmed")
        items = payload.get("items", [])
        
        if not tenant_id or not order_id:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Reserve stock for confirmed items
        service = InventoryService(db, tenant_id)
        
        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")
            
            success, message = service.reserve_stock(
                product_id, quantity, str(order_id), "order"
            )
            
            if not success:
                request_logger.warning(f"Failed to reserve stock: {message}")
        
        request_logger.info(f"Order {order_id} stock reserved")
        
        return {
            "status": "success",
            "message": "Order confirmed and stock reserved",
            "order_id": order_id,
            "items_reserved": len(items)
        }
    
    except Exception as e:
        request_logger.error(f"Order confirmation webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/odoo/po-received")
async def odoo_po_received(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Receive PO received notifications from Odoo.
    Expected payload:
    {
        "tenant_id": "...",
        "po_id": 123,
        "items": [
            {"product_id": 1, "quantity_received": 100}
        ]
    }
    """
    try:
        tenant_id = payload.get("tenant_id")
        po_id = payload.get("po_id")
        items = payload.get("items", [])
        
        if not tenant_id or not po_id:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        service = InventoryService(db, tenant_id)
        
        # Add received stock
        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity_received")
            
            service.adjust_stock(
                product_id, quantity, "purchase_order_receipt",
                f"PO {po_id}", "odoo_webhook"
            )
        
        request_logger.info(f"PO {po_id} receipt processed")
        
        return {
            "status": "success",
            "message": "PO receipt recorded",
            "po_id": po_id,
            "items_received": len(items)
        }
    
    except Exception as e:
        request_logger.error(f"PO receipt webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/odoo/inventory-adjustment")
async def odoo_inventory_adjustment(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Receive inventory adjustments from Odoo (damages, losses, etc).
    Expected payload:
    {
        "tenant_id": "...",
        "product_id": 1,
        "quantity_change": -5,
        "reason": "damage",
        "notes": "Damaged during transit"
    }
    """
    try:
        tenant_id = payload.get("tenant_id")
        product_id = payload.get("product_id")
        quantity_change = payload.get("quantity_change")
        reason = payload.get("reason", "adjustment")
        notes = payload.get("notes", "")
        
        if not tenant_id or not product_id or quantity_change is None:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        service = InventoryService(db, tenant_id)
        service.adjust_stock(product_id, quantity_change, reason, notes, "odoo_webhook")
        
        request_logger.info(f"Inventory adjustment: Product {product_id}, Change: {quantity_change}")
        
        return {
            "status": "success",
            "message": "Adjustment recorded",
            "product_id": product_id,
            "quantity_change": quantity_change
        }
    
    except Exception as e:
        request_logger.error(f"Inventory adjustment webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
