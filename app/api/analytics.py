from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
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


@router.get("/dashboard")
async def get_dashboard(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Real-time merchant dashboard snapshot."""
    from app.models.order import Order
    from app.models.inventory import StockLocation
    from app.models.procurement import PurchaseOrder
    from app.models.return_refund import OrderReturn

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    order_count, order_revenue = db.query(
        func.count(Order.id),
        func.coalesce(func.sum(Order.grand_total), 0.0),
    ).filter(
        Order.tenant_id == current_tenant_id,
        Order.created_at >= today_start,
        Order.status != "cancelled",
    ).first()

    pending_fulfillment = db.query(func.count(Order.id)).filter(
        Order.tenant_id == current_tenant_id,
        Order.status.in_(["pending", "confirmed"]),
    ).scalar() or 0

    low_stock_count = db.query(func.count(StockLocation.id)).filter(
        StockLocation.tenant_id == current_tenant_id,
        StockLocation.quantity > 0,
        StockLocation.quantity <= StockLocation.reorder_point,
    ).scalar() or 0

    out_of_stock_count = db.query(func.count(StockLocation.id)).filter(
        StockLocation.tenant_id == current_tenant_id,
        StockLocation.quantity <= 0,
    ).scalar() or 0

    open_po_count, open_po_value = db.query(
        func.count(PurchaseOrder.id),
        func.coalesce(func.sum(PurchaseOrder.total_amount), 0.0),
    ).filter(
        PurchaseOrder.tenant_id == current_tenant_id,
        PurchaseOrder.po_status.in_(["draft", "sent", "confirmed"]),
    ).first()

    pending_returns = db.query(func.count(OrderReturn.id)).filter(
        OrderReturn.tenant_id == current_tenant_id,
        OrderReturn.status.in_(["return_requested", "approved"]),
    ).scalar() or 0

    top_skus_rows = db.query(
        Order.sku,
        Order.product_name,
        func.sum(Order.quantity).label("qty_sold"),
    ).filter(
        Order.tenant_id == current_tenant_id,
        Order.created_at >= today_start,
        Order.status != "cancelled",
    ).group_by(Order.sku, Order.product_name).order_by(
        func.sum(Order.quantity).desc()
    ).limit(5).all()

    return {
        "today": {
            "orders": order_count or 0,
            "revenue": float(order_revenue),
            "pending_fulfillment": pending_fulfillment,
        },
        "inventory": {
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
        },
        "open_pos": {
            "count": open_po_count or 0,
            "value": float(open_po_value),
        },
        "pending_returns": pending_returns,
        "top_selling_today": [
            {"sku": r.sku, "name": r.product_name, "qty_sold": int(r.qty_sold)}
            for r in top_skus_rows
        ],
    }


@router.get("/forecast-accuracy")
async def get_forecast_accuracy(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Forecast vs actual accuracy by SKU."""
    from app.models.inventory import DemandForecast
    from app.models.product import Product

    forecasts = db.query(DemandForecast).filter(
        DemandForecast.tenant_id == current_tenant_id,
        DemandForecast.actual_demand.isnot(None),
        DemandForecast.predicted_demand.isnot(None),
    ).all()

    if not forecasts:
        return {"overall_mape": None, "by_sku": [], "last_30_days": None}

    product_ids = list({f.product_id for f in forecasts})
    product_map = {
        p.id: p.sku for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
    }

    # Group by product_id
    from collections import defaultdict
    by_product: dict = defaultdict(list)
    for f in forecasts:
        if f.predicted_demand and f.actual_demand is not None:
            ape = abs(f.predicted_demand - f.actual_demand) / max(f.actual_demand, 1) * 100
            bias = f.predicted_demand - f.actual_demand
            by_product[f.product_id].append({"ape": ape, "bias": bias})

    by_sku = []
    all_apes = []
    for pid, entries in by_product.items():
        mape = sum(e["ape"] for e in entries) / len(entries)
        avg_bias = sum(e["bias"] for e in entries) / len(entries)
        all_apes.extend(e["ape"] for e in entries)
        by_sku.append({
            "sku": product_map.get(pid, str(pid)),
            "mape": round(mape, 2),
            "bias": round(avg_bias, 2),
            "sample_size": len(entries),
        })

    overall_mape = round(sum(all_apes) / len(all_apes), 2) if all_apes else None
    by_sku.sort(key=lambda x: x["mape"], reverse=True)

    cutoff_30 = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    cutoff_30 = cutoff_30 - timedelta(days=30)
    recent = [f for f in forecasts if f.forecast_date and f.forecast_date >= cutoff_30]
    last_30: dict | None = None
    if recent:
        errors = [abs(f.predicted_demand - f.actual_demand) / max(f.actual_demand, 1) * 100 for f in recent]
        over = sum(1 for f in recent if f.predicted_demand > f.actual_demand)
        under = sum(1 for f in recent if f.predicted_demand <= f.actual_demand)
        last_30 = {
            "avg_error": round(sum(errors) / len(errors), 2),
            "over_forecast_count": over,
            "under_forecast_count": under,
        }

    return {
        "overall_mape": overall_mape,
        "by_sku": by_sku,
        "last_30_days": last_30,
    }
