import pandas as pd
from prophet import Prophet
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.models.order import Order
from app.models.sku import ProductSKU
from app.core.logger import request_logger

class AIForecastingService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def forecast_sku_demand(self, sku: str, periods: int = 30) -> Dict:
        """
        Predict future demand for a specific SKU using Facebook Prophet.
        """
        # 1. Fetch historical sales data
        sales = self.db.query(
            func.date(Order.created_at).label("ds"),
            func.sum(Order.quantity).label("y")
        ).filter(
            Order.tenant_id == self.tenant_id,
            Order.sku == sku,
            Order.status == "completed"
        ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()

        if not sales or len(sales) < 5:
            return {
                "sku": sku,
                "error": "Insufficient data for forecasting (need at least 5 distinct days of sales)",
                "forecast": []
            }

        # 2. Prepare DataFrame for Prophet
        df = pd.DataFrame([{"ds": str(s.ds), "y": float(s.y)} for s in sales])
        df['ds'] = pd.to_datetime(df['ds'])

        # 3. Initialize and Fit Prophet Model
        # We disable daily seasonality since our data is aggregated daily
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.95
        )
        model.fit(df)

        # 4. Create Future DataFrame
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        # 5. Format results
        # We only care about future predictions
        future_forecast = forecast.tail(periods)
        
        results = []
        for _, row in future_forecast.iterrows():
            results.append({
                "date": row['ds'].strftime('%Y-%m-%d'),
                "predicted_qty": max(0, round(row['yhat'], 2)),
                "lower_bound": max(0, round(row['yhat_lower'], 2)),
                "upper_bound": max(0, round(row['yhat_upper'], 2))
            })

        return {
            "sku": sku,
            "forecast_period_days": periods,
            "total_predicted_demand": round(sum(r['predicted_qty'] for r in results), 2),
            "forecast": results
        }

    def get_smart_reorder_suggestions(self) -> List[Dict]:
        """
        Smart Reordering (Phase 2.2):
        Combines demand forecast with lead times and current stock.
        """
        # This would be a more complex implementation combining multiple SKUs
        # For now, we'll provide a framework
        skus = self.db.query(ProductSKU).filter(ProductSKU.tenant_id == self.tenant_id).all()
        
        suggestions = []
        for sku_record in skus:
            # 1. Forecast next 30 days
            forecast_data = self.forecast_sku_demand(sku_record.sku, periods=30)
            if "error" in forecast_data:
                continue
            
            predicted_demand = forecast_data["total_predicted_demand"]
            
            # 2. Check current stock (simplified)
            # In real app, query StockLocation
            from app.models.inventory import StockLocation
            location = self.db.query(StockLocation).filter(
                StockLocation.tenant_id == self.tenant_id,
                StockLocation.product_id == sku_record.product_id
            ).first()
            
            current_stock = location.available_quantity if location else 0
            
            # 3. Calculate Reorder Point
            # Logic: If current stock < predicted demand + safety stock (20%)
            safety_stock = predicted_demand * 0.2
            reorder_threshold = predicted_demand + safety_stock
            
            if current_stock < reorder_threshold:
                suggestions.append({
                    "sku": sku_record.sku,
                    "name": sku_record.product_name,
                    "current_stock": current_stock,
                    "predicted_30d_demand": predicted_demand,
                    "suggested_reorder_qty": round(reorder_threshold - current_stock, 0),
                    "urgency": "high" if current_stock < (predicted_demand * 0.5) else "medium"
                })

        return sorted(suggestions, key=lambda x: x["suggested_reorder_qty"], reverse=True)
