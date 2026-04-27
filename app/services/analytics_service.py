import json
import pandas as pd
import io
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
from app.models.product import Product
from app.models.inventory import StockLocation, StockMovement
from app.models.order import Order
from app.models.sku import ProductSKU
from app.models.customer import Customer
from app.models.procurement import Supplier, PurchaseOrder, PurchaseOrderLine
from app.models.season import Season, Collection
from app.core.logger import request_logger


class AnalyticsService:
    """Inventory analytics and reporting."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def get_inventory_valuation(self) -> Dict:
        """Get total inventory value with trends."""
        results = self.db.query(
            Product.id,
            Product.name,
            Product.sku,
            Product.price,
            func.coalesce(func.sum(StockLocation.quantity), 0).label("qty")
        ).outerjoin(
            StockLocation, StockLocation.product_id == Product.id
        ).filter(
            Product.tenant_id == self.tenant_id
        ).group_by(
            Product.id, Product.name, Product.sku, Product.price
        ).all()

        total_value = 0
        product_values = []
        for r in results:
            value = (r.price or 0.0) * r.qty
            total_value += value
            product_values.append({
                "product_id": r.id,
                "name": r.name,
                "sku": r.sku,
                "quantity": r.qty,
                "unit_price": r.price,
                "total_value": value
            })

        product_values.sort(key=lambda x: x["total_value"], reverse=True)

        return {
            "total_inventory_value": total_value,
            "product_count": len(product_values),
            "by_product": product_values[:50],
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_size_color_matrix(self, product_id: Optional[int] = None) -> Dict:
        """Size/Color Sales Matrix — which combinations sell and which don't."""
        query = self.db.query(
            ProductSKU.size,
            ProductSKU.color,
            func.sum(Order.quantity).label("total_sold"),
            func.sum(Order.total_amount).label("revenue")
        ).join(
            Order, Order.sku == ProductSKU.sku
        ).filter(
            ProductSKU.tenant_id == self.tenant_id,
            Order.status == "completed"
        )
        
        if product_id:
            query = query.filter(ProductSKU.product_id == product_id)
            
        results = query.group_by(ProductSKU.size, ProductSKU.color).all()
        
        matrix = []
        for size, color, sold, revenue in results:
            matrix.append({
                "size": size or "N/A",
                "color": color or "N/A",
                "total_sold": int(sold or 0),
                "revenue": round(float(revenue or 0.0), 2)
            })
            
        return {
            "product_id": product_id,
            "matrix": matrix,
            "summary": {
                "top_size": max(matrix, key=lambda x: x["total_sold"])["size"] if matrix else None,
                "top_color": max(matrix, key=lambda x: x["total_sold"])["color"] if matrix else None
            }
        }

    def get_dead_stock_report(self) -> Dict:
        """Dead Stock Report — items unsold for 30/60/90 days with ageing value."""
        now = datetime.utcnow()
        report = {30: [], 60: [], 999: []}

        last_sale_subq = (
            self.db.query(
                Order.sku.label("sku"),
                func.max(Order.created_at).label("last_sold")
            ).filter(
                Order.tenant_id == self.tenant_id,
                Order.status == "completed"
            ).group_by(Order.sku)
            .subquery()
        )

        results = (
            self.db.query(StockLocation, ProductSKU, last_sale_subq.c.last_sold)
            .join(ProductSKU, ProductSKU.product_id == StockLocation.product_id)
            .outerjoin(last_sale_subq, last_sale_subq.c.sku == ProductSKU.sku)
            .filter(
                StockLocation.tenant_id == self.tenant_id,
                StockLocation.quantity > 0
            ).all()
        )

        for loc, sku, last_sold in results:
            ref_date = last_sold or sku.created_at
            days_since = (now - ref_date).days if ref_date else 999

            item_data = {
                "sku": sku.sku,
                "name": sku.product_name,
                "quantity": loc.quantity,
                "value": loc.quantity * (sku.cost_price or 0),
                "days_idle": days_since
            }

            if days_since >= 90:
                report[999].append(item_data)
            elif days_since >= 60:
                report[60].append(item_data)
            elif days_since >= 30:
                report[30].append(item_data)

        return {
            "summary": {
                "30_days": {"count": len(report[30]), "value": sum(i["value"] for i in report[30])},
                "60_days": {"count": len(report[60]), "value": sum(i["value"] for i in report[60])},
                "90_days": {"count": len(report[999]), "value": sum(i["value"] for i in report[999])}
            },
            "details": report
        }

    def get_sku_profit_loss(self, days: int = 30) -> List[Dict]:
        """Gross Margin per SKU (selling price - cost price * qty sold)."""
        since = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            Order.sku,
            Order.product_name,
            func.sum(Order.quantity).label("total_qty"),
            func.sum(Order.total_amount).label("total_revenue"),
            func.sum(Order.quantity * Order.unit_cost_at_sale).label("total_cost")
        ).filter(
            Order.tenant_id == self.tenant_id,
            Order.created_at >= since,
            Order.status == "completed"
        ).group_by(Order.sku, Order.product_name).all()
        
        pl_data = []
        for sku, name, qty, rev, cost in results:
            revenue = float(rev or 0.0)
            total_cost = float(cost or 0.0)
            profit = revenue - total_cost
            margin = (profit / revenue * 100) if revenue > 0 else 0
            
            pl_data.append({
                "sku": sku,
                "name": name,
                "quantity_sold": int(qty or 0),
                "revenue": round(revenue, 2),
                "cost_of_goods": round(total_cost, 2),
                "gross_profit": round(profit, 2),
                "margin_pct": round(margin, 1)
            })
            
        return sorted(pl_data, key=lambda x: x["gross_profit"], reverse=True)

    def get_supplier_performance(self) -> List[Dict]:
        """Supplier-wise purchase analysis (delivery performance)."""
        from sqlalchemy import and_

        results = (
            self.db.query(
                Supplier.supplier_name,
                Supplier.reliability_score,
                func.count(PurchaseOrder.id).label("total_pos"),
                func.sum(case(
                    (PurchaseOrder.po_status == "received", 1),
                    else_=0
                )).label("received_pos"),
                func.sum(case(
                    (and_(
                        PurchaseOrder.po_status == "received",
                        PurchaseOrder.actual_delivery.isnot(None),
                        PurchaseOrder.expected_delivery.isnot(None),
                        PurchaseOrder.actual_delivery <= PurchaseOrder.expected_delivery
                    ), 1),
                    else_=0
                )).label("on_time")
            ).join(PurchaseOrder, PurchaseOrder.supplier_id == Supplier.id)
            .filter(Supplier.tenant_id == self.tenant_id)
            .group_by(Supplier.id, Supplier.supplier_name, Supplier.reliability_score)
            .all()
        )

        perf_report = []
        for name, reliability, total_pos, received_pos, on_time in results:
            on_time_rate = (float(on_time) / float(received_pos) * 100) if received_pos else 0
            perf_report.append({
                "supplier": name,
                "total_pos": total_pos,
                "received_pos": received_pos,
                "on_time_delivery_rate": round(on_time_rate, 1),
                "reliability_score": reliability
            })

        return perf_report

    def get_customer_loyalty(self) -> List[Dict]:
        """Customer purchase frequency (loyalty & repeat rate)."""
        customers = self.db.query(Customer).filter(
            Customer.tenant_id == self.tenant_id
        ).order_by(Customer.total_spend.desc()).limit(100).all()
        
        report = []
        for c in customers:
            report.append({
                "name": c.name,
                "mobile": c.mobile,
                "total_orders": c.order_count,
                "total_spend": round(c.total_spend, 2),
                "last_order": c.last_order_date.isoformat() if c.last_order_date else "N/A"
            })
        return report

    def get_season_comparison(self) -> Dict:
        """Season vs Season comparison."""
        results = (
            self.db.query(
                Season.name,
                Season.start_date,
                Season.end_date,
                func.coalesce(func.sum(Order.total_amount), 0.0).label("revenue")
            ).outerjoin(Product, Product.season_id == Season.id)
            .outerjoin(ProductSKU, ProductSKU.product_id == Product.id)
            .outerjoin(Order, (Order.sku == ProductSKU.sku) & (Order.status == "completed"))
            .filter(Season.tenant_id == self.tenant_id)
            .group_by(Season.id, Season.name, Season.start_date, Season.end_date)
            .all()
        )

        comparison = [
            {
                "season": name,
                "revenue": round(float(revenue), 2),
                "period": f"{start_date.date()} to {end_date.date()}" if start_date else "N/A"
            }
            for name, start_date, end_date, revenue in results
        ]
        return {"seasons": comparison}

    def get_inventory_abc_analysis(self) -> Dict:
        """
        ABC Analysis:
        A - Top 70% Revenue (Critical)
        B - Next 20% Revenue (Important)
        C - Remaining 10% Revenue (Routine)
        """
        # 1. Get revenue per product
        results = self.db.query(
            Product.id,
            Product.name,
            func.sum(Order.total_amount).label("revenue")
        ).join(
            ProductSKU, ProductSKU.product_id == Product.id
        ).join(
            Order, Order.sku == ProductSKU.sku
        ).filter(
            Order.tenant_id == self.tenant_id,
            Order.status == "completed"
        ).group_by(Product.id, Product.name).all()
        
        if not results:
            return {"a": [], "b": [], "c": [], "summary": {}}
            
        data = [{"id": r.id, "name": r.name, "revenue": float(r.revenue or 0.0)} for r in results]
        df = pd.DataFrame(data)
        df = df.sort_values(by="revenue", ascending=False)
        
        total_revenue = df["revenue"].sum()
        df["cumulative_revenue"] = df["revenue"].cumsum()
        df["revenue_pct"] = (df["cumulative_revenue"] / total_revenue) * 100
        
        # 2. Categorize
        def categorize(pct):
            if pct <= 70: return "A"
            if pct <= 90: return "B"
            return "C"
        
        df["category"] = df["revenue_pct"].apply(categorize)
        
        # 3. Format Response
        categories = {"A": [], "B": [], "C": []}
        for _, row in df.iterrows():
            categories[row["category"]].append({
                "product_id": int(row["id"]),
                "name": row["name"],
                "revenue": round(float(row["revenue"]), 2),
                "revenue_pct": round(float(row["revenue_pct"]), 2)
            })
            
        return {
            "a": categories["A"],
            "b": categories["B"],
            "c": categories["C"],
            "summary": {
                "a_count": len(categories["A"]),
                "b_count": len(categories["B"]),
                "c_count": len(categories["C"]),
                "total_revenue": round(float(total_revenue), 2)
            }
        }

    def get_sales_trends(self, days: int = 30) -> Dict:
        """Analyze daily sales trends and identify anomalies."""
        since = datetime.utcnow() - timedelta(days=days)
        
        # 1. Get daily revenue
        daily_sales = self.db.query(
            func.date(Order.created_at).label("day"),
            func.sum(Order.total_amount).label("revenue"),
            func.count(Order.id).label("order_count")
        ).filter(
            Order.tenant_id == self.tenant_id,
            Order.created_at >= since,
            Order.status == "completed"
        ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()
        
        if not daily_sales:
            return {"trends": [], "anomalies": []}
            
        data = [{"day": str(r.day), "revenue": float(r.revenue or 0.0), "count": int(r.order_count or 0)} for r in daily_sales]
        df = pd.DataFrame(data)
        
        # 2. Calculate simple moving average and standard deviation for anomaly detection
        df["sma"] = df["revenue"].rolling(window=3, min_periods=1).mean()
        df["std"] = df["revenue"].rolling(window=3, min_periods=1).std()
        
        anomalies = []
        for i, row in df.iterrows():
            # If revenue is > 2 sigma from SMA, mark as anomaly (spike or drop)
            if i > 0 and not pd.isna(row["std"]) and row["std"] > 0:
                z_score = (row["revenue"] - row["sma"]) / row["std"]
                if abs(z_score) > 2:
                    anomalies.append({
                        "day": str(row["day"]),
                        "revenue": round(float(row["revenue"]), 2),
                        "type": "spike" if z_score > 0 else "drop",
                        "z_score": round(float(z_score), 2)
                    })

        import json as _json
        return {
            "trends": _json.loads(df[["day", "revenue", "count"]].to_json(orient="records")),
            "anomalies": anomalies,
            "summary": {
                "avg_daily_revenue": round(float(df["revenue"].mean()), 2),
                "max_revenue_day": str(df.loc[df["revenue"].idxmax()]["day"])
            }
        }

    def export_to_excel(self, report_type: str) -> io.BytesIO:
        """Export any report to Excel."""
        data = []
        if report_type == "valuation": data = self.get_inventory_valuation()["by_product"]
        elif report_type == "sku_pl": data = self.get_sku_profit_loss()
        elif report_type == "customer_loyalty": data = self.get_customer_loyalty()
        elif report_type == "supplier_perf": data = self.get_supplier_performance()
        elif report_type == "matrix": data = self.get_size_color_matrix()["matrix"]
        elif report_type == "abc": 
            abc = self.get_inventory_abc_analysis()
            data = abc["a"] + abc["b"] + abc["c"]
        elif report_type == "trends": data = self.get_sales_trends()["trends"]
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Report")
        output.seek(0)
        return output

    def get_financials_summary(self) -> Dict:
        """P&L and GST summary for completed orders (all-time)."""
        row = self.db.query(
            func.coalesce(func.sum(Order.total_amount), 0.0).label("revenue"),
            func.coalesce(func.sum(Order.quantity * Order.unit_cost_at_sale), 0.0).label("cogs"),
            func.coalesce(func.sum(Order.tax_amount), 0.0).label("total_gst"),
            func.coalesce(func.sum(Order.igst_amount), 0.0).label("igst"),
            func.coalesce(func.sum(Order.cgst_amount), 0.0).label("cgst"),
            func.coalesce(func.sum(Order.sgst_amount), 0.0).label("sgst"),
        ).filter(
            Order.tenant_id == self.tenant_id,
            Order.status == "completed"
        ).one()

        revenue = round(float(row.revenue), 2)
        cogs = round(float(row.cogs), 2)
        gross_profit = round(revenue - cogs, 2)
        gross_margin_pct = round((gross_profit / revenue * 100), 1) if revenue > 0 else 0.0

        return {
            "financials": {
                "total_revenue": revenue,
                "total_cogs": cogs,
                "gross_profit": gross_profit,
                "gross_margin_pct": gross_margin_pct,
            },
            "taxes": {
                "total_gst": round(float(row.total_gst), 2),
                "breakdown": {
                    "IGST": round(float(row.igst), 2),
                    "CGST": round(float(row.cgst), 2),
                    "SGST": round(float(row.sgst), 2),
                },
            },
        }

    def get_inventory_report(self) -> Dict:
        """Comprehensive business health report."""
        financials = self.get_financials_summary()
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "financials": financials["financials"],
            "taxes": financials["taxes"],
            "valuation": self.get_inventory_valuation(),
            "sku_pl": self.get_sku_profit_loss(days=30),
            "dead_stock": self.get_dead_stock_report(),
            "matrix": self.get_size_color_matrix(),
            "abc_analysis": self.get_inventory_abc_analysis(),
            "sales_trends": self.get_sales_trends()
        }
