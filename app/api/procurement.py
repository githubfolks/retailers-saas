from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_permission
from app.services.procurement_service import ProcurementService, SupplierPerformanceService
from app.models.procurement import (
    Supplier, PurchaseOrder, PurchaseOrderLine, OrderFulfillment,
    BackorderAlert, InventoryCount, CountLine, ProductBarcode
)

router = APIRouter(
    prefix="/procurement", 
    tags=["procurement"],
    dependencies=[Depends(check_permission("procurement"))]
)


# ============ SCHEMAS ============

class SupplierResponse(BaseModel):
    id: int
    supplier_name: str
    phone: str
    whatsapp_number: Optional[str]
    email: Optional[str]
    lead_time_days: int
    reliability_score: float
    is_active: bool
    
    class Config:
        from_attributes = True


class PurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    po_status: str
    total_amount: float
    po_date: datetime
    expected_delivery: datetime
    actual_delivery: Optional[datetime]
    
    class Config:
        from_attributes = True


class FulfillmentResponse(BaseModel):
    id: int
    order_id: int
    fulfillment_status: str
    warehouse_id: Optional[int]
    tracking_number: Optional[str]
    estimated_delivery: Optional[datetime]
    actual_delivery: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ SUPPLIERS ============

@router.post("/suppliers")
async def create_supplier(
    supplier_name: str,
    phone: str,
    whatsapp_number: Optional[str] = None,
    email: Optional[str] = None,
    lead_time_days: int = 7,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new supplier."""
    service = ProcurementService(db, current_tenant_id)
    supplier_id = service.create_supplier(
        supplier_name, phone, whatsapp_number, email, lead_time_days
    )
    
    return {"status": "success", "supplier_id": supplier_id}


@router.get("/suppliers", response_model=List[SupplierResponse])
async def list_suppliers(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    active_only: bool = True
):
    """List all suppliers."""
    suppliers = db.query(Supplier).filter(Supplier.tenant_id == current_tenant_id)
    
    if active_only:
        suppliers = suppliers.filter(Supplier.is_active == True)
    
    return suppliers.all()


@router.get("/suppliers/{supplier_id}/performance")
async def get_supplier_performance(
    supplier_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get supplier performance metrics."""
    service = SupplierPerformanceService(db, current_tenant_id)
    metrics = service.calculate_supplier_metrics(supplier_id)
    reliability = service.update_supplier_reliability(supplier_id)
    
    return {
        "supplier_id": supplier_id,
        "reliability_score": reliability,
        "metrics": metrics
    }

@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    supplier_data: dict,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Update supplier profile."""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.tenant_id == current_tenant_id
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    for key, value in supplier_data.items():
        if hasattr(supplier, key) and value is not None:
            setattr(supplier, key, value)
            
    db.commit()
    db.refresh(supplier)
    return supplier

@router.delete("/suppliers/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Delete a supplier."""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.tenant_id == current_tenant_id
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    db.delete(supplier)
    db.commit()
    return {"status": "deleted"}


# ============ PURCHASE ORDERS ============

@router.post("/purchase-orders")
async def create_purchase_order(
    supplier_id: int,
    expected_delivery: datetime,
    lines: List[Dict[str, Any]],
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a purchase order."""
    service = ProcurementService(db, current_tenant_id)
    po_id = service.create_purchase_order(supplier_id, expected_delivery, lines)
    
    return {"status": "success", "po_id": po_id}


@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """List purchase orders."""
    query = db.query(PurchaseOrder).filter(PurchaseOrder.tenant_id == current_tenant_id)
    
    if status:
        query = query.filter(PurchaseOrder.po_status == status)
    
    return query.order_by(PurchaseOrder.po_date.desc()).all()


@router.post("/purchase-orders/{po_id}/send")
async def send_purchase_order(
    po_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Send PO to supplier via WhatsApp."""
    service = ProcurementService(db, current_tenant_id)
    
    # Get tenant config
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    
    supplier_config = {
        "whatsapp_phone_id": getattr(tenant, 'whatsapp_phone_id', None),
        "whatsapp_token": getattr(tenant, 'whatsapp_token', None)
    }
    
    if not service.send_po_to_supplier(po_id, supplier_config):
        raise HTTPException(status_code=400, detail="Failed to send PO")
    
    return {"status": "success", "message": "PO sent to supplier"}


@router.post("/purchase-orders/{po_id}/receive")
async def receive_purchase_order(
    po_id: int,
    received_lines: List[Dict[str, Any]],
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Mark PO as received."""
    service = ProcurementService(db, current_tenant_id)
    
    if not service.receive_po(po_id, received_lines):
        raise HTTPException(status_code=400, detail="Failed to receive PO")
    
    return {"status": "success", "message": "PO marked as received"}


# ============ FULFILLMENT ============

@router.post("/fulfillments")
async def create_fulfillment(
    order_id: int,
    warehouse_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create order fulfillment."""
    service = ProcurementService(db, current_tenant_id)
    fulfillment_id = service.create_fulfillment(order_id, warehouse_id)
    
    return {"status": "success", "fulfillment_id": fulfillment_id}


@router.patch("/fulfillments/{fulfillment_id}/status")
async def update_fulfillment_status(
    fulfillment_id: int,
    status: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Update fulfillment status."""
    service = ProcurementService(db, current_tenant_id)
    
    if not service.update_fulfillment_status(fulfillment_id, status):
        raise HTTPException(status_code=400, detail="Failed to update fulfillment")
    
    return {"status": "success", "message": f"Fulfillment status updated to {status}"}


@router.get("/fulfillments/order/{order_id}", response_model=FulfillmentResponse)
async def get_order_fulfillment(
    order_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get fulfillment status for order."""
    fulfillment = db.query(OrderFulfillment).filter(
        OrderFulfillment.order_id == order_id,
        OrderFulfillment.tenant_id == current_tenant_id
    ).first()
    
    if not fulfillment:
        raise HTTPException(status_code=404, detail="Fulfillment not found")
    
    return fulfillment


# ============ BACKORDERS ============

@router.post("/backorders")
async def create_backorder(
    order_id: int,
    product_id: int,
    quantity_short: int,
    expected_date: datetime,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create backorder alert."""
    service = ProcurementService(db, current_tenant_id)
    backorder_id = service.create_backorder_alert(order_id, product_id, quantity_short, expected_date)
    
    return {"status": "success", "backorder_id": backorder_id}


@router.post("/backorders/{backorder_id}/notify")
async def notify_backorder_customer(
    backorder_id: int,
    customer_phone: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Notify customer about backorder."""
    service = ProcurementService(db, current_tenant_id)
    
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    
    tenant_config = {
        "whatsapp_phone_id": getattr(tenant, 'whatsapp_phone_id', None),
        "whatsapp_token": getattr(tenant, 'whatsapp_token', None)
    }
    
    if not service.notify_backorder_customer(backorder_id, customer_phone, tenant_config):
        raise HTTPException(status_code=400, detail="Failed to notify customer")
    
    return {"status": "success", "message": "Customer notified"}


# ============ INVENTORY COUNTS ============

@router.post("/inventory-counts")
async def create_inventory_count(
    count_by_user: str,
    warehouse_id: Optional[int] = None,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create inventory count session."""
    service = ProcurementService(db, current_tenant_id)
    count_id = service.create_inventory_count(count_by_user, warehouse_id)
    
    return {"status": "success", "count_id": count_id}


@router.post("/inventory-counts/{count_id}/lines")
async def add_count_line(
    count_id: int,
    product_id: int,
    counted_qty: int,
    barcode: Optional[str] = None,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Add line to inventory count."""
    service = ProcurementService(db, current_tenant_id)
    
    if not service.add_count_line(count_id, product_id, counted_qty, barcode):
        raise HTTPException(status_code=400, detail="Failed to add count line")
    
    return {"status": "success"}


@router.post("/inventory-counts/{count_id}/complete")
async def complete_inventory_count(
    count_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Complete inventory count."""
    service = ProcurementService(db, current_tenant_id)
    result = service.complete_inventory_count(count_id)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail="Failed to complete count")
    
    return result


# ============ BARCODES ============

@router.post("/products/{product_id}/barcodes")
async def create_barcode(
    product_id: int,
    barcode: str,
    barcode_type: str = "EAN-13",
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create product barcode."""
    service = ProcurementService(db, current_tenant_id)
    barcode_id = service.create_barcode(product_id, barcode, barcode_type)
    
    return {"status": "success", "barcode_id": barcode_id}


@router.get("/products/scan/{barcode}")
async def scan_barcode(
    barcode: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Look up product by barcode."""
    service = ProcurementService(db, current_tenant_id)
    product = service.get_product_by_barcode(barcode)
    
    if not product:
        raise HTTPException(status_code=404, detail="Barcode not found")
    
    return product
