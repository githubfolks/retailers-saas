from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime
from app.models.conversation import ConversationState
from app.models.product import Product
from app.models.sku import ProductSKU
from app.models.order import Order
from app.models.tenant import Tenant
from app.core.logger import request_logger
from app.services.ai_bot import AIBot

class WhatsAppBotService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.ai_bot = AIBot(db, tenant_id)
        
        # WhatsApp Cloud API Config (fetched from Tenant)
        self.tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        self.phone_id = getattr(self.tenant, "whatsapp_phone_id", None)
        self.token = getattr(self.tenant, "whatsapp_token", None)

    async def handle_incoming(self, mobile: str, text: str):
        """Main entry point for incoming WhatsApp messages."""
        # 1. Get or Create Conversation State
        state = self.db.query(ConversationState).filter(
            ConversationState.tenant_id == self.tenant_id,
            ConversationState.mobile == mobile
        ).first()
        
        if not state:
            state = ConversationState(
                tenant_id=self.tenant_id,
                mobile=mobile,
                current_state="IDLE"
            )
            self.db.add(state)
            self.db.flush()

        # Update last message time
        state.last_message_at = datetime.utcnow()
        
        # 2. Command Parsing (Priority)
        msg_clean = text.strip().lower()
        
        # Universal "Reset"
        if msg_clean in ["hi", "hello", "start", "menu", "reset"]:
            state.current_state = "IDLE"
            state.context = {}
            await self.send_message(mobile, "👋 Welcome to our WhatsApp Shop!\n\nYou can:\n1. Browse Catalog (Type 'catalog')\n2. Order by SKU (Type the SKU code)\n3. Check Order Status (Type 'status')\n\nHow can I help you today?")
            self.db.commit()
            return

        # 3. State Machine Logic
        if state.current_state == "IDLE":
            await self._handle_idle_state(state, text)
        elif state.current_state == "AWAITING_QTY":
            await self._handle_awaiting_qty(state, text)
        elif state.current_state == "CONFIRMING_ORDER":
            await self._handle_confirming_order(state, text)
        
        self.db.commit()

    async def _handle_idle_state(self, state: ConversationState, text: str):
        msg = text.strip().lower()
        
        # Intent: Return Request
        if "return" in msg:
            await self.send_message(mobile, "To request a return, please send us your Order ID (e.g. 'RETURN #1001') and a brief reason. Our team will review it shortly!")
            return

        # Intent: Catalog
        if "catalog" in msg:
            await self._send_catalog(state.mobile)
            return

        # Intent: SKU Lookup (e.g. "SKU-123")
        sku_candidate = text.strip().upper()
        sku_record = self.db.query(ProductSKU).filter(
            ProductSKU.sku == sku_candidate,
            ProductSKU.tenant_id == self.tenant_id
        ).first()
        
        if sku_record:
            state.current_state = "AWAITING_QTY"
            state.selected_sku = sku_record.sku
            state.selected_product_id = sku_record.product_id
            
            response = (
                f"✅ Found: *{sku_record.product_name}*\n"
                f"Price: ₹{sku_record.seasonal_price or sku_record.selling_price}\n"
                f"Size: {sku_record.size or 'N/A'}, Color: {sku_record.color or 'N/A'}\n\n"
                "How many would you like to order? (Please send a number)"
            )
            await self.send_message(state.mobile, response)
            return

        # Fallback to AI Bot
        ai_response = await self.ai_bot.process_message(text)
        await self.send_message(state.mobile, ai_response)

    async def _handle_awaiting_qty(self, state: ConversationState, text: str):
        try:
            qty = int(text.strip())
            if qty <= 0:
                await self.send_message(state.mobile, "Please enter a positive number.")
                return
            
            state.quantity = qty
            state.current_state = "CONFIRMING_ORDER"
            
            sku_record = self.db.query(ProductSKU).filter(
                ProductSKU.sku == state.selected_sku,
                ProductSKU.tenant_id == self.tenant_id
            ).first()
            
            total = (sku_record.seasonal_price or sku_record.selling_price) * qty
            
            response = (
                f"🛒 *Order Confirmation*\n\n"
                f"Product: {sku_record.product_name}\n"
                f"SKU: {state.selected_sku}\n"
                f"Qty: {qty}\n"
                f"Total: ₹{total}\n\n"
                "Type 'YES' to confirm this order, or 'NO' to cancel."
            )
            await self.send_message(state.mobile, response)
            
        except ValueError:
            await self.send_message(state.mobile, "I didn't catch that number. How many would you like? (e.g., 2)")

    async def _handle_confirming_order(self, state: ConversationState, text: str):
        msg = text.strip().upper()
        
        if msg == "YES":
            # Create the Order
            sku_record = self.db.query(ProductSKU).filter(
                ProductSKU.sku == state.selected_sku,
                ProductSKU.tenant_id == self.tenant_id
            ).first()
            
            price = sku_record.seasonal_price or sku_record.selling_price
            total = price * state.quantity
            
            new_order = Order(
                tenant_id=self.tenant_id,
                customer_mobile=state.mobile,
                product_name=sku_record.product_name,
                sku=state.selected_sku,
                quantity=state.quantity,
                unit_price=price,
                total_amount=total,
                status="pending",
                notes="Created via WhatsApp Bot"
            )
            self.db.add(new_order)
            self.db.flush()
            
            await self.send_message(state.mobile, f"🚀 *Order Created!* Your Order ID is #{new_order.id}.\n\nWe will notify you once it's dispatched.")
            
            # Reset state
            state.current_state = "IDLE"
            state.context = {}
            state.selected_sku = None
            state.quantity = None
            
        elif msg == "NO":
            state.current_state = "IDLE"
            state.context = {}
            await self.send_message(state.mobile, "Order cancelled. Back to menu!")
        else:
            await self.send_message(state.mobile, "Please type 'YES' to confirm or 'NO' to cancel.")

    async def _send_catalog(self, mobile: str):
        products = self.db.query(Product).filter(
            Product.tenant_id == self.tenant_id
        ).limit(5).all()
        
        if not products:
            await self.send_message(mobile, "Our catalog is currently empty. Check back soon!")
            return

        response = "*🔥 Our Latest Collections*\n\n"
        for p in products:
            response += f"• *{p.name}* (₹{p.price})\n  Reply with SKU to order.\n\n"
        
        await self.send_message(mobile, response)

    async def send_message(self, mobile: str, text: str):
        """Sends a message via WhatsApp Cloud API."""
        if not self.phone_id or not self.token:
            request_logger.warning(f"WhatsApp credentials missing for tenant {self.tenant_id}")
            # In dev, we log it
            print(f"DEBUG [WA -> {mobile}]: {text}")
            return

        url = f"https://graph.facebook.com/v17.0/{self.phone_id}/messages"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "text",
            "text": {"body": text}
        }
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
        except Exception as e:
            request_logger.error(f"WhatsApp send failed: {str(e)}")

    @staticmethod
    async def send_dispatch_notification(tenant: Tenant, mobile: str, order_id: int, tracking_number: str):
        """Static helper for fulfillment updates."""
        msg = f"📦 *Order Shipped!*\n\nYour order #{order_id} has been dispatched.\nTracking: {tracking_number}\n\nThank you for shopping with us!"
        # We need a db session to get credentials, but for now we mock or use a singleton
        print(f"WA NOTIFICATION [{mobile}]: {msg}")

    @staticmethod
    async def send_stock_alert(tenant: Tenant, owner_mobile: str, sku: str, current_stock: int):
        """Notify owner about low stock."""
        msg = f"⚠️ *Low Stock Alert*\n\nSKU: {sku}\nCurrent Stock: {current_stock}\nPlease reorder soon."
        print(f"WA OWNER ALERT [{owner_mobile}]: {msg}")
