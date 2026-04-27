from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_permission
from app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/analytics", 
    tags=["analytics"],
    dependencies=[Depends(check_permission("reports"))]
)


@router.get("/valuation")
async def get_inventory_valuation(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get inventory valuation by product."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_inventory_valuation()


@router.get("/matrix")
async def get_size_color_matrix(
    product_id: Optional[int] = None,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get Size/Color sales matrix."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_size_color_matrix(product_id)


@router.get("/dead-stock")
async def get_dead_stock(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get enhanced dead stock report (30/60/90 days)."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_dead_stock_report()


@router.get("/sku-pl")
async def get_sku_profit_loss(
    days: int = 30,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get P&L per SKU."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_sku_profit_loss(days)


@router.get("/supplier-performance")
async def get_supplier_performance(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get supplier delivery performance."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_supplier_performance()


@router.get("/customer-loyalty")
async def get_customer_loyalty(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get customer purchase frequency and loyalty."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_customer_loyalty()


@router.get("/season-comparison")
async def get_season_comparison(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Compare revenue across seasons."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_season_comparison()


@router.get("/abc-analysis")
async def get_abc_analysis(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get ABC inventory classification."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_inventory_abc_analysis()


@router.get("/sales-trends")
async def get_sales_trends(
    days: int = 30,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get daily sales trends and anomalies."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_sales_trends(days)


@router.get("/export/{report_type}")
async def export_analytics_report(
    report_type: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Export any analytics report to Excel."""
    service = AnalyticsService(db, current_tenant_id)
    xlsx_file = service.export_to_excel(report_type)
    
    filename = f"{report_type}_report_{current_tenant_id}.xlsx"
    return StreamingResponse(
        xlsx_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/comprehensive-report")
async def get_comprehensive_report(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get comprehensive inventory health report."""
    service = AnalyticsService(db, current_tenant_id)
    return service.get_inventory_report()
