from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_permission
from app.core.logger import request_logger
from app.services.inventory_service import InventoryService
from app.services.llm_inventory_bot import LLMInventoryBot
from app.models.inventory import (
    StockLocation, StockMovement, StockAlert, DemandForecast,
    ReorderSuggestion, Warehouse, StockTransfer, InventoryNotification
)
from app.models.product import Product

router = APIRouter(
    prefix="/inventory", 
    tags=["inventory"],
    dependencies=[Depends(check_permission("inventory"))]
)


# ============ SCHEMAS ============

class WarehouseResponse(BaseModel):
    id: int
    warehouse_name: str
    warehouse_code: str
    location_address: Optional[str] = "N/A"
    capacity: float
    
    class Config:
        from_attributes = True

class LocationCreate(BaseModel):
    warehouse_id: int
    name: str
    parent_id: Optional[int] = None
    location_type: str = "internal"

class LocationResponse(BaseModel):
    id: int
    warehouse_id: Optional[int]
    parent_id: Optional[int]
    name: str
    location_type: str
    quantity: int
    
    class Config:
        from_attributes = True

class ValuationLayerResponse(BaseModel):
    id: int
    sku: str
    original_quantity: float
    remaining_quantity: float
    unit_cost: float
    total_value: float
    reference_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class InternalTransferCreate(BaseModel):
    product_id: int
    from_location_id: int
    to_location_id: int
    quantity: float

class StockLocationResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: Optional[str]
    zone_name: Optional[str]
    bin_number: Optional[str]
    quantity: int
    reserved_quantity: int
    available_quantity: int
    reorder_point: int
    reorder_quantity: int
    
    class Config:
        from_attributes = True


class StockAlertResponse(BaseModel):
    id: int
    product_id: int
    alert_type: str
    alert_level: str
    current_value: int
    threshold_value: int
    status: str
    triggered_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DemandForecastResponse(BaseModel):
    id: int
    product_id: int
    forecast_date: datetime
    predicted_demand: float
    confidence_level: float
    lower_bound: float
    upper_bound: float
    
    class Config:
        from_attributes = True


class ReorderSuggestionResponse(BaseModel):
    id: int
    product_id: int
    suggested_quantity: int
    rationale: str
    ai_confidence: float
    status: str
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InventoryMetricsResponse(BaseModel):
    total_inventory_value: float
    total_quantity: int
    product_count: int
    location_count: int
    low_stock_items: int
    out_of_stock_items: int
    out_of_stock_rate: float


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity: int
    reason: Optional[str]
    reference_id: Optional[str]
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ STOCK LEVEL ENDPOINTS ============

@router.get("/stock/{product_id}", response_model=Dict[str, Any])
async def get_real_time_stock(
    product_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get real-time stock for a product."""
    service = InventoryService(db, current_tenant_id)
    return service.get_real_time_stock(product_id)


@router.post("/stock/reserve")
async def reserve_stock(
    product_id: int,
    quantity: int,
    reference_id: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Reserve stock for an order."""
    service = InventoryService(db, current_tenant_id)
    success, message = service.reserve_stock(product_id, quantity, reference_id, "order")
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"status": "success", "message": message}


@router.post("/stock/release")
async def release_stock(
    product_id: int,
    quantity: int,
    reference_id: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Release reserved stock."""
    service = InventoryService(db, current_tenant_id)
    success, message = service.release_stock(product_id, quantity, reference_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"status": "success", "message": message}


@router.post("/stock/adjust")
async def adjust_stock(
    product_id: int,
    quantity: int,
    reason: str,
    notes: Optional[str] = None,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Adjust stock (damage, loss, etc.)."""
    service = InventoryService(db, current_tenant_id)
    
    if not service.adjust_stock(product_id, quantity, reason, notes or "", "user"):
        raise HTTPException(status_code=400, detail="Failed to adjust stock")
    
    return {"status": "success", "message": f"Adjusted {quantity} units"}


# ============ ALERTS ============

@router.get("/alerts", response_model=List[StockAlertResponse])
async def list_stock_alerts(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    alert_type: Optional[str] = None
):
    """List stock alerts."""
    query = db.query(StockAlert).filter(StockAlert.tenant_id == current_tenant_id)

    if status:
        query = query.filter(StockAlert.status == status)
    if alert_type:
        query = query.filter(StockAlert.alert_type == alert_type)

    return query.order_by(StockAlert.triggered_at.desc()).limit(200).all()


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Acknowledge an alert."""
    alert = db.query(StockAlert).filter(
        StockAlert.id == alert_id,
        StockAlert.tenant_id == current_tenant_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    
    return {"status": "success"}


# ============ MOVEMENTS ============

@router.get("/movements/{product_id}", response_model=List[StockMovementResponse])
async def get_stock_movements(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get stock movement history."""
    service = InventoryService(db, current_tenant_id)
    movements = service.get_stock_movements(product_id, days)
    
    return movements


# ============ FORECASTS ============

@router.get("/forecasts/{product_id}", response_model=List[DemandForecastResponse])
async def get_demand_forecast(
    product_id: int,
    days_ahead: int = Query(30, ge=1, le=365),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get demand forecast for product."""
    cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=days_ahead)
    forecasts = db.query(DemandForecast).filter(
        DemandForecast.tenant_id == current_tenant_id,
        DemandForecast.product_id == product_id,
        DemandForecast.forecast_date <= cutoff
    ).order_by(DemandForecast.forecast_date).all()
    
    return forecasts


# ============ REORDER SUGGESTIONS ============

@router.get("/reorder-suggestions", response_model=List[ReorderSuggestionResponse])
async def get_reorder_suggestions(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    status: Optional[str] = "pending"
):
    """Get reorder suggestions."""
    query = db.query(ReorderSuggestion).filter(
        ReorderSuggestion.tenant_id == current_tenant_id
    )

    if status:
        query = query.filter(ReorderSuggestion.status == status)

    return query.order_by(ReorderSuggestion.created_at.desc()).limit(200).all()


@router.post("/reorder-suggestions/{suggestion_id}/approve")
async def approve_reorder_suggestion(
    suggestion_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Approve a reorder suggestion."""
    suggestion = db.query(ReorderSuggestion).filter(
        ReorderSuggestion.id == suggestion_id,
        ReorderSuggestion.tenant_id == current_tenant_id
    ).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.status = "approved"
    suggestion.approved_at = datetime.utcnow()
    suggestion.approved_by = "user"
    db.commit()
    
    return {"status": "success", "message": "Suggestion approved"}


# ============ WAREHOUSES ============

@router.post("/warehouses", response_model=WarehouseResponse)
async def create_warehouse(
    name: str,
    code: str,
    address: str,
    capacity: float,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new warehouse (with automatic default location)."""
    return InventoryService.create_warehouse(db, current_tenant_id, name, code, address, capacity)


@router.get("/warehouses", response_model=List[WarehouseResponse])
async def list_warehouses(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """List all warehouses for the tenant."""
    return InventoryService.get_warehouses(db, current_tenant_id)


@router.post("/locations", response_model=LocationResponse)
async def create_location(
    data: LocationCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a hierarchical stock location (Rack, Shelf, etc.)."""
    return InventoryService.create_location(
        db, current_tenant_id, data.warehouse_id, 
        data.name, data.parent_id, data.location_type
    )


@router.get("/locations", response_model=List[LocationResponse])
async def list_locations(
    warehouse_id: Optional[int] = None,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """List stock locations, optionally filtered by warehouse."""
    query = db.query(StockLocation).filter(StockLocation.tenant_id == current_tenant_id)
    if warehouse_id:
        query = query.filter(StockLocation.warehouse_id == warehouse_id)
    return query.all()


@router.get("/valuation/ledger", response_model=List[ValuationLayerResponse])
async def get_valuation_ledger(
    product_id: Optional[int] = None,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get the financial valuation ledger (FIFO layers)."""
    return InventoryService.get_valuation_ledger(db, current_tenant_id, product_id)


# ============ TRANSFERS ============

@router.post("/transfers/internal")
async def create_internal_transfer(
    data: InternalTransferCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Transfer stock between two locations within a warehouse."""
    success = InventoryService.move_stock(
        db, current_tenant_id, data.product_id, 
        data.from_location_id, data.to_location_id, data.quantity, 
        "user" # In real app, use current_user.id
    )
    return {"status": "success" if success else "failed"}


# ============ TRANSFERS ============

@router.post("/transfers")
async def create_transfer(
    product_id: int,
    from_warehouse_id: int,
    to_warehouse_id: int,
    quantity: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create stock transfer between warehouses."""
    service = InventoryService(db, current_tenant_id)
    transfer_id = service.create_transfer(product_id, from_warehouse_id, to_warehouse_id, quantity)
    
    return {"status": "success", "transfer_id": transfer_id}


@router.post("/transfers/{transfer_id}/receive")
async def receive_transfer(
    transfer_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Mark transfer as received."""
    service = InventoryService(db, current_tenant_id)
    
    if not service.receive_transfer(transfer_id, "user"):
        raise HTTPException(status_code=400, detail="Failed to receive transfer")
    
    return {"status": "success"}


# ============ METRICS ============

@router.get("/metrics", response_model=InventoryMetricsResponse)
async def get_inventory_metrics(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get overall inventory health metrics."""
    service = InventoryService(db, current_tenant_id)
    return service.get_inventory_metrics()


# ============ AI BOT ============

@router.post("/ai-query")
async def query_inventory_ai(
    query: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Query inventory AI bot."""
    bot = LLMInventoryBot(db, current_tenant_id)
    response = await bot.answer_inventory_query(query)
    return response


@router.get("/ai-briefing")
async def get_ai_briefing(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get daily AI-generated inventory briefing."""
    bot = LLMInventoryBot(db, current_tenant_id)
    briefing = bot.generate_daily_briefing()
    
    return {"briefing": briefing, "generated_at": datetime.utcnow()}
