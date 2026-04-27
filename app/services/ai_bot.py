from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.models.product import Product
from app.core.logger import request_logger

class AIBot:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def process_message(self, message: str) -> str:
        """Process an incoming WhatsApp message and return an AI response."""
        msg = message.lower()
        
        # 1. Intent: Greeting
        if any(word in msg for word in ["hi", "hello", "hey", "start"]):
            return "👋 Welcome! I'm your AI Shopping Assistant. How can I help you today? You can ask about our products or check stock."

        # 2. Intent: Product Search
        # In a real LLM scenario, we would use a model here. 
        # For simplicity and speed, we'll use a keyword-based product search on the local cache.
        products = self.db.query(Product).filter(
            Product.tenant_id == self.tenant_id
        ).all()

        matching_products = []
        for p in products:
            if p.name.lower() in msg or any(word in msg for word in p.name.lower().split()):
                matching_products.append(p)

        if matching_products:
            response = "🔍 I found some items you might like:\n\n"
            for p in matching_products:
                response += f"• *{p.name}*\n  Price: ₹{p.price}\n  Stock: {'Available' if p.quantity > 0 else 'Sold Out'}\n\n"
            response += "Would you like to place an order? Just tell me what you need!"
            return response

        # 3. Intent: Purchase / Order
        if any(word in msg for word in ["buy", "order", "purchase"]):
            for p in products:
                if p.name.lower() in msg or any(word in msg for word in p.name.lower().split()):
                    return (
                        f"✅ Excellent choice! I've prepared a draft order for *{p.name}* (₹{p.price}).\n\n"
                        "💳 *Secure Checkout*:\n"
                        f"Please complete your payment here: https://rzp.io/i/demo_link_{p.id}\n\n"
                        "I'll notify you as soon as the payment is confirmed! 🚀"
                    )
            return "🛒 Which product would you like to order? You can say 'buy Classic Crewneck' or 'order the Denim Jeans'."

        # 4. Intent: Stock/General Inquiry
        if "stock" in msg or "available" in msg:
            return "📦 I can definitely check our inventory for you. Could you please specify which product you're looking for?"

        # 5. Fallback: Direct to Human/Generic Help
        return "🤔 I'm not sure I understood that. You can ask me about our products, prices, or availability! For example: 'Do you have any t-shirts?' or 'buy the Red Tee'."

    def _format_product_list(self, products: List[Product]) -> str:
        if not products:
            return "I couldn't find any products matching your search."
        
        lines = ["Here's what I found:"]
        for p in products:
            lines.append(f"- {p.name}: ₹{p.price}")
        return "\n".join(lines)
