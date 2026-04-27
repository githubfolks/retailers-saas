from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.inventory import StockLocation, DemandForecast, ReorderSuggestion
from app.core.logger import request_logger
from app.core.config import settings
import json
from datetime import datetime


class LLMInventoryBot:
    """LLM-powered inventory management AI bot using LangChain & OpenAI."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=getattr(settings, 'openai_api_key', None)
        )
    
    async def answer_inventory_query(self, user_query: str) -> Dict[str, Any]:
        """Answer natural language inventory queries using LLM."""
        try:
            # Get inventory context
            context = self._build_inventory_context()
            
            prompt = ChatPromptTemplate.from_template("""
You are an expert AI inventory manager for a retail business using Odoo.
Your role is to:
1. Answer questions about current stock levels
2. Provide demand forecasts and insights
3. Suggest reorder quantities and timing
4. Identify risks and optimization opportunities
5. Give actionable recommendations

Current Inventory Context:
{context}

User Query: {query}

Provide a JSON response with:
{{
    "answer": "Direct answer to the query",
    "insights": ["Key insight 1", "Key insight 2"],
    "recommendations": ["Action 1", "Action 2"],
    "urgency": "low|medium|high|critical",
    "confidence": 0-100
}}
""")
            
            chain = prompt | self.llm | JsonOutputParser()
            
            response = await chain.ainvoke({
                "context": context,
                "query": user_query
            })
            
            return response
        
        except Exception as e:
            request_logger.error(f"LLM query error: {str(e)}")
            return {
                "answer": "I encountered an error processing your query. Please try again.",
                "insights": [],
                "recommendations": [],
                "urgency": "low",
                "confidence": 0
            }
    
    def _build_inventory_context(self) -> str:
        """Build current inventory context for LLM."""
        from sqlalchemy import func

        # Single query: products with aggregated stock quantities
        rows = self.db.query(
            Product.id,
            Product.name,
            Product.sku,
            Product.price,
            func.coalesce(func.sum(StockLocation.quantity), 0).label("total_qty"),
            func.coalesce(func.sum(StockLocation.reserved_quantity), 0).label("total_reserved"),
            func.max(StockLocation.reorder_point).label("reorder_point"),
        ).outerjoin(StockLocation, StockLocation.product_id == Product.id).filter(
            Product.tenant_id == self.tenant_id
        ).group_by(Product.id, Product.name, Product.sku, Product.price).all()

        total_value = 0.0
        out_of_stock = 0
        low_stock = 0
        product_summary = []

        for r in rows:
            value = (r.price or 0.0) * r.total_qty
            total_value += value
            if r.total_qty == 0:
                out_of_stock += 1
            elif r.total_qty <= (r.reorder_point or 10):
                low_stock += 1
            if len(product_summary) < 20:
                product_summary.append({
                    "name": r.name,
                    "sku": r.sku,
                    "price": r.price,
                    "total_qty": r.total_qty,
                    "reserved": r.total_reserved,
                    "available": r.total_qty - r.total_reserved,
                    "reorder_point": r.reorder_point or 10,
                })

        context = f"""
Total Products: {len(rows)}

Top Products Inventory:
{json.dumps(product_summary, indent=2)}

Total Inventory Value: ₹{total_value:,.2f}
Out of Stock Items: {out_of_stock}
Low Stock Items: {low_stock}
"""
        return context
    
    async def process_whatsapp_message(self, message: str) -> str:
        """Process WhatsApp message with enhanced NLP."""
        # Classify intent
        intent = self._classify_intent(message)
        
        if intent == "stock_check":
            return await self._handle_stock_check(message)
        elif intent == "forecast":
            return await self._handle_forecast_query(message)
        elif intent == "reorder":
            return await self._handle_reorder_query(message)
        elif intent == "low_stock_alert":
            return await self._handle_low_stock_alert(message)
        elif intent == "trend_analysis":
            return await self._handle_trend_analysis(message)
        else:
            response = await self.answer_inventory_query(message)
            return response.get("answer", "I'm not sure how to help with that.")
    
    def _classify_intent(self, message: str) -> str:
        """Classify user intent from message."""
        msg_lower = message.lower()
        
        if any(word in msg_lower for word in ["stock", "available", "quantity", "how many"]):
            return "stock_check"
        elif any(word in msg_lower for word in ["forecast", "predict", "demand", "expect"]):
            return "forecast"
        elif any(word in msg_lower for word in ["reorder", "order", "purchase", "buy"]):
            return "reorder"
        elif any(word in msg_lower for word in ["low", "alert", "warning", "critical"]):
            return "low_stock_alert"
        elif any(word in msg_lower for word in ["trend", "velocity", "moving", "sales"]):
            return "trend_analysis"
        else:
            return "general"
    
    async def _handle_stock_check(self, message: str) -> str:
        """Handle stock level queries."""
        response = await self.answer_inventory_query(
            f"What is the current stock status? User asked: {message}"
        )
        
        answer = response.get("answer", "")
        urgency = response.get("urgency", "")
        
        emoji = "🟢" if urgency == "low" else "🟡" if urgency == "medium" else "🔴"
        
        return f"{emoji} {answer}\n\nRecommendations:\n" + "\n".join(
            f"• {r}" for r in response.get("recommendations", [])
        )
    
    async def _handle_forecast_query(self, message: str) -> str:
        """Handle demand forecast queries."""
        response = await self.answer_inventory_query(
            f"What is the demand forecast? User asked: {message}"
        )
        
        return f"📊 {response.get('answer', '')}\n\nInsights:\n" + "\n".join(
            f"📈 {i}" for i in response.get("insights", [])
        )
    
    async def _handle_reorder_query(self, message: str) -> str:
        """Handle reorder suggestion queries."""
        response = await self.answer_inventory_query(
            f"What products should be reordered and in what quantities? User asked: {message}"
        )
        
        return f"📦 {response.get('answer', '')}\n\nActions:\n" + "\n".join(
            f"✅ {r}" for r in response.get("recommendations", [])
        )
    
    async def _handle_low_stock_alert(self, message: str) -> str:
        """Handle low stock alerts."""
        rows = (
            self.db.query(
                StockLocation.quantity,
                StockLocation.reorder_point,
                Product.name
            ).join(Product, Product.id == StockLocation.product_id)
            .filter(
                StockLocation.tenant_id == self.tenant_id,
                StockLocation.quantity <= StockLocation.reorder_point
            ).limit(5).all()
        )

        total_low = self.db.query(StockLocation).filter(
            StockLocation.tenant_id == self.tenant_id,
            StockLocation.quantity <= StockLocation.reorder_point
        ).count()

        if not rows:
            return "✅ All products are well stocked!"

        alert_msg = f"⚠️ {total_low} products have low stock:\n\n"
        for qty, reorder_pt, name in rows:
            alert_msg += f"📦 {name}\n  Current: {qty} | Threshold: {reorder_pt}\n\n"

        return alert_msg + "🚨 Action required!"
    
    async def _handle_trend_analysis(self, message: str) -> str:
        """Handle trend analysis queries."""
        response = await self.answer_inventory_query(
            f"Analyze inventory trends and velocity. User asked: {message}"
        )
        
        return f"📉 {response.get('answer', '')}\n\nKey Points:\n" + "\n".join(
            f"• {i}" for i in response.get("insights", [])
        )
    
    def generate_daily_briefing(self) -> str:
        """Generate daily inventory briefing using LLM."""
        context = self._build_inventory_context()

        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser

            prompt = ChatPromptTemplate.from_template("""
You are an expert supply chain analyst for a retail business.
Based on the current inventory snapshot below, write a concise executive briefing.

Inventory Snapshot:
{context}

Write a 3-5 sentence plain-English briefing covering:
1. Overall inventory health (healthy, needs attention, critical)
2. Any items that are low or out of stock
3. One key action the team should take today

Use plain text. No JSON. No bullet points. No markdown. Be direct and specific.
""")

            chain = prompt | self.llm | StrOutputParser()
            return chain.invoke({"context": context})

        except Exception as e:
            request_logger.error(f"Daily briefing LLM error: {str(e)}")
            # Fallback: build a readable summary without LLM
            products = self.db.query(Product).filter(Product.tenant_id == self.tenant_id).all()
            locations = self.db.query(StockLocation).filter(StockLocation.tenant_id == self.tenant_id).all()
            low_stock = [l for l in locations if l.quantity <= l.reorder_point and l.quantity > 0]
            out_of_stock = [l for l in locations if l.quantity == 0]
            total_value = sum(
                p.price * next((l.quantity for l in locations if l.product_id == p.id), 0)
                for p in products
            )

            lines = [
                f"📊 Daily Briefing — {datetime.now().strftime('%d %b %Y')}",
                f"",
                f"Total Products: {len(products)} | Locations: {len(locations)}",
                f"Inventory Value: ₹{total_value:,.0f}",
                f"",
            ]
            if out_of_stock:
                lines.append(f"🔴 Out of Stock: {len(out_of_stock)} location(s) need immediate restocking.")
            if low_stock:
                lines.append(f"🟡 Low Stock: {len(low_stock)} item(s) are below reorder point.")
            if not out_of_stock and not low_stock:
                lines.append("✅ All stock levels are healthy. No immediate action required.")

            return "\n".join(lines)


class LLMDemandForecaster:
    """LLM-assisted demand forecasting."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            api_key=getattr(settings, 'openai_api_key', None)
        )
    
    async def forecast_demand(self, product_id: int, days_ahead: int = 30) -> Dict:
        """Generate AI-powered demand forecast."""
        try:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            
            # Get historical data
            movements = self._get_sales_history(product_id, days=90)
            
            prompt = ChatPromptTemplate.from_template("""
You are an expert demand forecaster. Based on sales history and market factors:

Product: {product_name}
Price: {price}
Historical Sales (last 90 days): {sales_history}

Forecast demand for the next {days_ahead} days.

Return JSON:
{{
    "predicted_demand": <number>,
    "confidence_level": <0-100>,
    "lower_bound": <pessimistic>,
    "upper_bound": <optimistic>,
    "seasonal_factors": ["factor1", "factor2"],
    "risk_factors": ["risk1", "risk2"],
    "recommendation": "Action to take"
}}
""")
            
            chain = prompt | self.llm | JsonOutputParser()
            
            response = await chain.ainvoke({
                "product_name": product.name,
                "price": product.price,
                "sales_history": movements,
                "days_ahead": days_ahead
            })
            
            return response
        
        except Exception as e:
            request_logger.error(f"Forecasting error: {str(e)}")
            return {
                "predicted_demand": 0,
                "confidence_level": 0,
                "recommendation": "Unable to forecast"
            }
    
    def _get_sales_history(self, product_id: int, days: int = 90) -> List[Dict]:
        """Get sales history for forecasting."""
        # This would query actual sales data
        # For now, returning mock structure
        return [
            {"date": "2024-01-01", "quantity": 10},
            {"date": "2024-01-02", "quantity": 12},
        ]


class LLMReorderOptimizer:
    """LLM-powered reorder quantity optimization."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            api_key=getattr(settings, 'openai_api_key', None)
        )
    
    async def optimize_reorder(self, product_id: int) -> Dict:
        """Generate optimized reorder quantity."""
        try:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            location = self.db.query(StockLocation).filter(
                StockLocation.tenant_id == self.tenant_id,
                StockLocation.product_id == product_id
            ).first()
            
            prompt = ChatPromptTemplate.from_template("""
As an inventory optimization AI, recommend optimal reorder quantity.

Product: {product_name}
Current Stock: {current_stock}
Reorder Point: {reorder_point}
Lead Time: {lead_time} days
Unit Cost: ₹{unit_cost}
Monthly Demand: {monthly_demand}

Consider: Holding costs, stockout risks, supplier minimums.

Return JSON:
{{
    "suggested_quantity": <number>,
    "rationale": "Why this quantity",
    "economic_order_qty": <EOQ>,
    "safety_stock": <number>,
    "total_cost_estimate": <annual>,
    "ai_confidence": <0-100>
}}
""")
            
            chain = prompt | self.llm | JsonOutputParser()
            
            response = await chain.ainvoke({
                "product_name": product.name,
                "current_stock": location.quantity if location else 0,
                "reorder_point": location.reorder_point if location else 10,
                "lead_time": 7,
                "unit_cost": product.price,
                "monthly_demand": 50
            })
            
            return response
        
        except Exception as e:
            request_logger.error(f"Reorder optimization error: {str(e)}")
            return {"suggested_quantity": 50, "ai_confidence": 0}
