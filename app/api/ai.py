from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_permission
from app.services.ai_forecasting_service import AIForecastingService
from app.services.ai_recommendation_service import AIRecommendationService

router = APIRouter(
    prefix="/ai",
    tags=["AI/ML Intelligence"],
    dependencies=[Depends(check_permission("reports"))]
)

@router.get("/recommendations/bought-together/{sku}")
async def get_bought_together(
    sku: str,
    limit: int = 5,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get items frequently bought with this SKU."""
    service = AIRecommendationService(db, current_tenant_id)
    return service.get_frequently_bought_together(sku, limit)

@router.get("/recommendations/personal/{mobile}")
async def get_personal_recommendations(
    mobile: str,
    limit: int = 5,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get personalized product recommendations for a customer."""
    service = AIRecommendationService(db, current_tenant_id)
    return service.get_personal_recommendations(mobile, limit)


@router.get("/forecast/{sku}")
async def get_sku_forecast(
    sku: str,
    days: int = Query(30, ge=7, le=90),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get AI-driven demand forecast for a specific SKU.
    Uses Facebook Prophet for time-series analysis.
    """
    service = AIForecastingService(db, current_tenant_id)
    result = service.forecast_sku_demand(sku, periods=days)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@router.get("/reorder-suggestions")
async def get_ai_reorder_suggestions(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get smart reorder suggestions based on demand forecasting.
    Compares predicted demand vs current stock levels.
    """
    service = AIForecastingService(db, current_tenant_id)
    return service.get_smart_reorder_suggestions()
