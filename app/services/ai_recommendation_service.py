import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.models.order import Order
from app.models.sku import ProductSKU
from app.models.product import Product
from app.core.logger import request_logger

class AIRecommendationService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def get_frequently_bought_together(self, sku: str, limit: int = 5) -> List[Dict]:
        """
        Identify products frequently purchased in the same order context as the given SKU.
        """
        # 1. Find all orders containing this SKU
        # Since we don't have an order_lines table, we'll assume orders with same customer on same day are 'together'
        # OR if your schema allows multi-item orders in one record (currently it's 1 SKU per Order record)
        # Let's assume 'same customer, same day' = together.
        
        target_orders = self.db.query(Order.customer_mobile, func.date(Order.created_at).label("day")).filter(
            Order.tenant_id == self.tenant_id,
            Order.sku == sku,
            Order.status == "completed"
        ).all()
        
        if not target_orders:
            return []
            
        # 2. Find other SKUs in those same customer-day sessions
        related_skus = []
        for customer, day in target_orders:
            others = self.db.query(Order.sku).filter(
                Order.tenant_id == self.tenant_id,
                Order.customer_mobile == customer,
                func.date(Order.created_at) == day,
                Order.sku != sku,
                Order.status == "completed"
            ).all()
            related_skus.extend([o.sku for o in others])
            
        if not related_skus:
            return []
            
        # 3. Count frequencies
        df = pd.Series(related_skus).value_counts().head(limit).reset_index()
        df.columns = ['sku', 'count']
        
        # 4. Enrich with product data
        recommendations = []
        for _, row in df.iterrows():
            sku_info = self.db.query(ProductSKU).filter(
                ProductSKU.sku == row['sku'],
                ProductSKU.tenant_id == self.tenant_id
            ).first()
            if sku_info:
                recommendations.append({
                    "sku": row['sku'],
                    "name": sku_info.product_name,
                    "frequency": int(row['count']),
                    "price": float(sku_info.selling_price)
                })
                
        return recommendations

    def get_personal_recommendations(self, mobile: str, limit: int = 5) -> List[Dict]:
        """
        Identify products a specific customer might like based on their history.
        Uses a simple item-item similarity approach.
        """
        # 1. Get customer's purchase history
        past_skus = self.db.query(Order.sku).filter(
            Order.customer_mobile == mobile,
            Order.tenant_id == self.tenant_id,
            Order.status == "completed"
        ).all()
        
        past_sku_list = [s.sku for s in past_skus]
        if not past_sku_list:
            # Fallback to popular items
            return self._get_popular_items(limit)
            
        # 2. For each past item, find related items
        recommendation_counts = {}
        for sku in past_sku_list:
            related = self.get_frequently_bought_together(sku, limit=3)
            for r in related:
                if r['sku'] not in past_sku_list: # Don't recommend what they already bought
                    recommendation_counts[r['sku']] = recommendation_counts.get(r['sku'], 0) + r['frequency']
                    
        # 3. Sort and Enrich
        sorted_skus = sorted(recommendation_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        results = []
        for sku, score in sorted_skus:
            sku_info = self.db.query(ProductSKU).filter(
                ProductSKU.sku == sku,
                ProductSKU.tenant_id == self.tenant_id
            ).first()
            if sku_info:
                results.append({
                    "sku": sku,
                    "name": sku_info.product_name,
                    "match_score": score,
                    "price": float(sku_info.selling_price)
                })
                
        return results if results else self._get_popular_items(limit)

    def _get_popular_items(self, limit: int) -> List[Dict]:
        """Fallback: Top selling items."""
        popular = self.db.query(
            Order.sku,
            func.count(Order.id).label("sales_count")
        ).filter(
            Order.tenant_id == self.tenant_id,
            Order.status == "completed"
        ).group_by(Order.sku).order_by(func.count(Order.id).desc()).limit(limit).all()
        
        results = []
        for sku, count in popular:
            sku_info = self.db.query(ProductSKU).filter(
                ProductSKU.sku == sku,
                ProductSKU.tenant_id == self.tenant_id
            ).first()
            if sku_info:
                results.append({
                    "sku": sku,
                    "name": sku_info.product_name,
                    "sales_count": int(count),
                    "price": float(sku_info.selling_price)
                })
        return results
