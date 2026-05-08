from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import httpx
import json
from datetime import datetime, timedelta
from app.models.conversation import ConversationState
from app.models.product import Product
from app.models.sku import ProductSKU
from app.models.order import Order
from app.models.customer import Customer
from app.models.tenant import Tenant
from app.core.logger import request_logger
from app.services.ai_bot import AIBot
from app.integrations.whatsapp_sender import send_whatsapp_message

# States
_IDLE = "IDLE"
_AWAITING_QTY = "AWAITING_QTY"
_BROWSING_CART = "BROWSING_CART"
_CONFIRMING_ORDER = "CONFIRMING_ORDER"
_AWAITING_ADDRESS = "AWAITING_ADDRESS"
_AWAITING_PAYMENT_METHOD = "AWAITING_PAYMENT_METHOD"
_AWAITING_REORDER_CHOICE = "AWAITING_REORDER_CHOICE"
_AWAITING_NOTIFY_CONFIRM = "AWAITING_NOTIFY_CONFIRM"


def _is_likely_english(text: str) -> bool:
    """Return True if text is ASCII-only (fast path — no API call needed)."""
    return all(ord(c) < 128 for c in text)


class WhatsAppBotService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.ai_bot = AIBot(db, tenant_id)

        self.tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        self.phone_id = getattr(self.tenant, "whatsapp_phone_id", None)
        self.token = getattr(self.tenant, "whatsapp_token", None)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def handle_incoming(self, mobile: str, text: str):
        # Detect B2B customer once per message (fast indexed lookup)
        from app.models.b2b import B2BCustomer as _B2BCust
        self._b2b_customer = self.db.query(_B2BCust).filter(
            _B2BCust.tenant_id == self.tenant_id,
            _B2BCust.mobile == mobile,
            _B2BCust.is_active == True,
        ).first()

        state = self.db.query(ConversationState).filter(
            ConversationState.tenant_id == self.tenant_id,
            ConversationState.mobile == mobile
        ).first()

        if not state:
            state = ConversationState(
                tenant_id=self.tenant_id,
                mobile=mobile,
                current_state=_IDLE,
                context={}
            )
            self.db.add(state)
            self.db.flush()

        state.last_message_at = datetime.utcnow()

        # Language detection — fast ASCII check; OpenAI fallback for non-ASCII scripts
        ctx_for_lang = state.context or {}
        self._customer_lang = ctx_for_lang.get("lang", "en")
        if not _is_likely_english(text):
            self._customer_lang = await self._detect_and_cache_language(
                text, state, ctx_for_lang
            )
            if self._customer_lang != "en":
                text = await self._translate_to_english(text)

        msg_clean = text.strip().lower()

        # Universal reset
        if msg_clean in ["hi", "hello", "start", "menu", "reset"]:
            state.current_state = _IDLE
            ctx_for_lang.pop("reorder_list", None)
            ctx_for_lang.pop("notify_sku", None)
            ctx_for_lang["cart"] = []
            state.context = ctx_for_lang
            state.selected_sku = None
            state.quantity = None
            welcome = self._welcome_text(self._b2b_customer)
            await self.send_message(mobile, await self._maybe_translate(welcome))
            self.db.commit()
            return

        if state.current_state == _IDLE:
            await self._handle_idle_state(state, text)
        elif state.current_state == _AWAITING_QTY:
            await self._handle_awaiting_qty(state, text)
        elif state.current_state == _BROWSING_CART:
            await self._handle_browsing_cart(state, text)
        elif state.current_state == _CONFIRMING_ORDER:
            await self._handle_confirming_order(state, text)
        elif state.current_state == _AWAITING_ADDRESS:
            await self._handle_awaiting_address(state, text)
        elif state.current_state == _AWAITING_PAYMENT_METHOD:
            await self._handle_awaiting_payment_method(state, text)
        elif state.current_state == _AWAITING_REORDER_CHOICE:
            await self._handle_awaiting_reorder_choice(state, text)
        elif state.current_state == _AWAITING_NOTIFY_CONFIRM:
            await self._handle_awaiting_notify_confirm(state, text)

        self.db.commit()

    # ------------------------------------------------------------------
    # State handlers
    # ------------------------------------------------------------------

    async def _handle_idle_state(self, state: ConversationState, text: str):
        msg = text.strip().lower()

        if "return" in msg:
            await self.send_message(state.mobile,
                "To request a return, send your Order ID like: RETURN #1001\n"
                "Our team will review it shortly.")
            return

        if msg in ["catalog", "browse", "shop"]:
            await self._send_catalog(state.mobile)
            return

        if msg in ["cart", "view cart", "my cart"]:
            await self._send_cart_summary(state)
            return

        if msg in ["reorder", "repeat order", "last order"]:
            await self._handle_reorder(state)
            return

        # SKU lookup
        sku_candidate = text.strip().upper()
        sku_record = self.db.query(ProductSKU).filter(
            ProductSKU.sku == sku_candidate,
            ProductSKU.tenant_id == self.tenant_id
        ).first()

        if sku_record:
            stock = getattr(sku_record, "quantity", None)
            if stock is not None and stock <= 0:
                ctx = state.context or {}
                ctx["notify_sku"] = sku_record.sku
                state.context = ctx
                state.current_state = _AWAITING_NOTIFY_CONFIRM
                await self.send_message(state.mobile,
                    f"Sorry, *{sku_record.product_name}* is currently out of stock.\n"
                    "Reply *NOTIFY* to get alerted when it's back, or 'catalog' to browse.")
                return

            state.current_state = _AWAITING_QTY
            state.selected_sku = sku_record.sku
            state.selected_product_id = sku_record.product_id
            price = sku_record.seasonal_price or sku_record.selling_price

            detail_lines = [f"*{sku_record.product_name}*"]
            if self._b2b_customer:
                from app.models.b2b import WholesalePriceList as _WPL
                tiers = (
                    self.db.query(_WPL)
                    .filter(
                        _WPL.tenant_id == self.tenant_id,
                        _WPL.sku == sku_candidate,
                        _WPL.tier == self._b2b_customer.customer_tier,
                    )
                    .order_by(_WPL.min_qty)
                    .all()
                )
                if tiers:
                    detail_lines.append(
                        f"Wholesale Price ({self._b2b_customer.customer_tier.upper()} tier):"
                    )
                    for t in tiers:
                        detail_lines.append(f"  {t.min_qty}+ units: Rs.{t.unit_price}")
                else:
                    detail_lines.append(f"Price: Rs.{price} (retail — no wholesale rate set)")
            else:
                detail_lines.append(f"Price: Rs.{price}")
            if sku_record.size:
                detail_lines.append(f"Size: {sku_record.size}")
            if sku_record.color:
                detail_lines.append(f"Color: {sku_record.color}")
            if stock is not None:
                detail_lines.append(f"In Stock: {stock} units")
            detail_lines.append("\nHow many would you like? (send a number)")
            caption = "\n".join(detail_lines)

            image_url = getattr(sku_record, "image_url", None)
            if image_url:
                await self.send_image(state.mobile, image_url, caption)
            else:
                await self.send_message(state.mobile, caption)
            return

        # Fallback AI
        ai_response = await self.ai_bot.process_message(text)
        await self.send_message(state.mobile, ai_response)

    async def _handle_awaiting_qty(self, state: ConversationState, text: str):
        try:
            qty = int(text.strip())
            if qty <= 0:
                await self.send_message(state.mobile, "Please enter a positive number.")
                return
        except ValueError:
            await self.send_message(state.mobile,
                "I didn't catch that. How many would you like? (e.g. 2)")
            return

        sku_record = self.db.query(ProductSKU).filter(
            ProductSKU.sku == state.selected_sku,
            ProductSKU.tenant_id == self.tenant_id
        ).first()

        price = sku_record.seasonal_price or sku_record.selling_price
        if self._b2b_customer:
            from app.models.b2b import WholesalePriceList as _WPL
            tier_entry = (
                self.db.query(_WPL)
                .filter(
                    _WPL.tenant_id == self.tenant_id,
                    _WPL.sku == state.selected_sku,
                    _WPL.tier == self._b2b_customer.customer_tier,
                    _WPL.min_qty <= qty,
                )
                .order_by(_WPL.min_qty.desc())
                .first()
            )
            if tier_entry:
                price = tier_entry.unit_price
        subtotal = price * qty

        ctx = state.context or {}
        cart: List[Dict] = ctx.get("cart", [])

        existing = next((i for i in cart if i["sku"] == state.selected_sku), None)
        if existing:
            existing["qty"] += qty
            existing["subtotal"] = existing["unit_price"] * existing["qty"]
        else:
            cart.append({
                "sku": state.selected_sku,
                "product_name": sku_record.product_name,
                "qty": qty,
                "unit_price": float(price),
                "subtotal": float(subtotal),
            })

        ctx["cart"] = cart
        state.context = ctx
        state.current_state = _BROWSING_CART
        state.selected_sku = None
        state.quantity = None

        cart_total = sum(i["subtotal"] for i in cart)
        lines = [f"Added to cart: *{sku_record.product_name}* x{qty} = Rs.{subtotal:.0f}"]
        lines.append(f"\nCart total: *Rs.{cart_total:.0f}* ({len(cart)} item(s))")
        lines.append("\nType *checkout* to place order\nType *add more* to keep shopping\nType *clear cart* to start over")
        await self.send_message(state.mobile, "\n".join(lines))

    async def _handle_browsing_cart(self, state: ConversationState, text: str):
        msg = text.strip().lower()

        if msg in ["checkout", "place order", "buy", "confirm"]:
            state.current_state = _CONFIRMING_ORDER
            await self._send_cart_summary(state, checkout_mode=True)
            return

        if msg in ["add more", "add", "continue", "more"]:
            state.current_state = _IDLE
            await self.send_message(state.mobile,
                "Sure! Send a SKU code to add another item, or type 'catalog' to browse.")
            return

        if msg in ["clear cart", "clear", "cancel"]:
            ctx = state.context or {}
            ctx["cart"] = []
            state.context = ctx
            state.current_state = _IDLE
            await self.send_message(state.mobile, "Cart cleared. Type 'catalog' to start shopping again.")
            return

        if msg in ["cart", "view cart", "my cart"]:
            await self._send_cart_summary(state)
            return

        # Any other text — treat as a new SKU lookup
        state.current_state = _IDLE
        await self._handle_idle_state(state, text)

    async def _handle_confirming_order(self, state: ConversationState, text: str):
        msg = text.strip().upper()

        if msg == "YES":
            ctx = state.context or {}
            cart: List[Dict] = ctx.get("cart", [])

            if not cart:
                await self.send_message(state.mobile, "Your cart is empty. Type 'catalog' to browse.")
                state.current_state = _IDLE
                return

            # Check for saved address
            customer = self.db.query(Customer).filter(
                Customer.tenant_id == self.tenant_id,
                Customer.mobile == state.mobile
            ).first()
            saved_address = customer.address if customer else None

            state.current_state = _AWAITING_ADDRESS
            if saved_address:
                ctx["saved_address"] = saved_address
            state.context = ctx

            if saved_address:
                await self.send_message(state.mobile,
                    f"Deliver to:\n{saved_address}\n\nType *SAME* to confirm or send a new address.")
            else:
                await self.send_message(state.mobile, "Please share your delivery address:")

        elif msg == "NO":
            state.current_state = _IDLE
            state.context = {}
            await self.send_message(state.mobile, "Order cancelled. Type 'menu' to start over.")
        else:
            await self.send_message(state.mobile, "Please type *YES* to confirm or *NO* to cancel.")

    async def _handle_awaiting_address(self, state: ConversationState, text: str):
        msg = text.strip()
        ctx = state.context or {}

        if msg.upper() == "SAME" and ctx.get("saved_address"):
            address = ctx["saved_address"]
        else:
            address = msg
            customer = self.db.query(Customer).filter(
                Customer.tenant_id == self.tenant_id,
                Customer.mobile == state.mobile
            ).first()
            if customer:
                customer.address = address

        ctx["delivery_address"] = address
        state.context = ctx

        if self._b2b_customer:
            # B2B customers always pay on credit terms — skip payment method prompt
            cart: List[Dict] = ctx.get("cart", [])
            await self._finalize_order(state, cart, ctx, "credit")
        else:
            state.current_state = _AWAITING_PAYMENT_METHOD
            await self.send_message(state.mobile,
                "How would you like to pay?\n\n"
                "1. UPI / Card (Pay online now)\n"
                "2. Cash on Delivery (COD)")

    async def _handle_awaiting_payment_method(self, state: ConversationState, text: str):
        msg = text.strip().lower()
        ctx = state.context or {}
        cart: List[Dict] = ctx.get("cart", [])

        if not cart:
            await self.send_message(state.mobile,
                "Your session expired. Type 'catalog' to start again.")
            state.current_state = _IDLE
            return

        if msg in ["1", "upi", "online", "card", "pay online", "pay now"]:
            payment_method = "upi"
        elif msg in ["2", "cod", "cash", "cash on delivery"]:
            payment_method = "cod"
        else:
            await self.send_message(state.mobile,
                "Please choose:\n1. UPI / Card\n2. Cash on Delivery (COD)")
            return

        await self._finalize_order(state, cart, ctx, payment_method)

    async def _finalize_order(
        self,
        state: ConversationState,
        cart: List[Dict],
        ctx: Dict,
        payment_method: str,
    ):
        delivery_address = ctx.get("delivery_address", "")
        product_names = ", ".join(f"{i['product_name']} x{i['qty']}" for i in cart)
        skus = ", ".join(i["sku"] for i in cart)
        total_qty = sum(i["qty"] for i in cart)
        total_amount = sum(i["subtotal"] for i in cart)

        def _reset_state():
            state.current_state = _IDLE
            ctx["cart"] = []
            ctx.pop("delivery_address", None)
            ctx.pop("saved_address", None)
            state.context = ctx
            state.selected_sku = None
            state.quantity = None

        # B2B credit order
        if self._b2b_customer and payment_method == "credit":
            credit_available = self._b2b_customer.credit_limit - self._b2b_customer.credit_used
            if self._b2b_customer.credit_limit > 0 and total_amount > credit_available:
                await self.send_message(
                    state.mobile,
                    f"Order exceeds your available credit.\n"
                    f"Available: Rs.{credit_available:.0f} | Order: Rs.{total_amount:.0f}\n"
                    "Please contact us to extend your credit limit.",
                )
                _reset_state()
                return

            from app.models.b2b import B2BOrder as _B2BOrd
            due_date = datetime.utcnow() + timedelta(days=self._b2b_customer.payment_terms_days)
            b2b_order = _B2BOrd(
                tenant_id=self.tenant_id,
                b2b_customer_id=self._b2b_customer.id,
                items=json.dumps(cart),
                total_amount=total_amount,
                discount_amount=0.0,
                grand_total=total_amount,
                payment_terms_days=self._b2b_customer.payment_terms_days,
                due_date=due_date,
                shipping_address=delivery_address,
            )
            self.db.add(b2b_order)
            self._b2b_customer.credit_used += total_amount
            self.db.flush()

            await self.send_message(
                state.mobile,
                f"B2B Order #{b2b_order.id} confirmed!\n"
                f"Business: {self._b2b_customer.business_name}\n"
                f"Total: Rs.{total_amount:.0f}\n"
                f"Payment due in {self._b2b_customer.payment_terms_days} days "
                f"({due_date.strftime('%d %b %Y')})",
            )
            await self._alert_merchant_b2b_order(
                b2b_order.id, self._b2b_customer.business_name,
                total_amount, self._b2b_customer.payment_terms_days,
            )
            _reset_state()
            return

        # Standard retail order (COD or UPI)
        new_order = Order(
            tenant_id=self.tenant_id,
            customer_mobile=state.mobile,
            product_name=product_names,
            sku=skus,
            quantity=total_qty,
            unit_price=total_amount / total_qty if total_qty else 0,
            total_amount=total_amount,
            grand_total=total_amount,
            status="pending",
            payment_method=payment_method,
            payment_status="cod_pending" if payment_method == "cod" else "pending",
            shipping_address=delivery_address,
            source="whatsapp",
            notes=json.dumps({"cart": cart}),
        )
        self.db.add(new_order)
        self.db.flush()

        if payment_method == "cod":
            await self.send_message(state.mobile,
                f"Order #{new_order.id} placed!\n"
                f"Total: Rs.{total_amount:.0f} — Cash on Delivery\n"
                "Our team will contact you to confirm the delivery slot.")
        else:
            payment_url = await self._create_and_send_payment_link(
                new_order, state.mobile, total_amount
            )
            if not payment_url:
                await self.send_message(state.mobile,
                    f"Order #{new_order.id} created!\n"
                    "Our team will share the payment link shortly.")
            else:
                await self.send_message(state.mobile,
                    f"Order #{new_order.id} confirmed!\n\n"
                    f"Pay Rs.{total_amount:.0f} here:\n{payment_url}\n\n"
                    "Link expires in 15 minutes.")

        await self._alert_merchant_new_order(new_order.id, state.mobile, total_amount)
        _reset_state()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _send_catalog(self, mobile: str):
        from app.integrations.whatsapp_sender import send_interactive_list

        skus = self.db.query(ProductSKU).filter(
            ProductSKU.tenant_id == self.tenant_id
        ).limit(10).all()

        if not skus:
            await self.send_message(mobile, "Our catalog is currently empty. Check back soon!")
            return

        rows = []
        for s in skus:
            price = s.seasonal_price or s.selling_price
            desc = f"Rs.{price}"
            if s.size:
                desc += f" | Size: {s.size}"
            if s.color:
                desc += f" | {s.color}"
            rows.append({
                "id": s.sku,
                "title": s.product_name[:24],
                "description": desc[:72],
            })

        sections = [{"title": "Available Products", "rows": rows}]
        result = send_interactive_list(
            recipient_number=mobile,
            header="Our Collection",
            body="Browse and select a product to order:",
            button_text="View Products",
            sections=sections,
            phone_number_id=self.phone_id,
            whatsapp_token=self.token,
        )
        if not result:
            lines = ["*Our Collection*\n"]
            for s in skus:
                price = s.seasonal_price or s.selling_price
                lines.append(f"• *{s.product_name}* ({s.sku}) — Rs.{price}")
            lines.append("\nSend the SKU code to order.")
            await self.send_message(mobile, "\n".join(lines))

    async def _send_cart_summary(self, state: ConversationState, checkout_mode: bool = False):
        ctx = state.context or {}
        cart: List[Dict] = ctx.get("cart", [])

        if not cart:
            await self.send_message(state.mobile,
                "Your cart is empty. Send a SKU code or type 'catalog' to browse.")
            return

        lines = ["*Your Cart*\n"]
        for item in cart:
            lines.append(f"• {item['product_name']} x{item['qty']} — Rs.{item['subtotal']:.0f}")
        total = sum(i["subtotal"] for i in cart)
        lines.append(f"\nTotal: *Rs.{total:.0f}*")

        if checkout_mode:
            lines.append("\nType *YES* to place order or *NO* to cancel.")
        else:
            lines.append("\nType *checkout* to place order or *add more* to continue shopping.")

        await self.send_message(state.mobile, "\n".join(lines))

    async def _handle_reorder(self, state: ConversationState):
        orders = self.db.query(Order).filter(
            Order.tenant_id == self.tenant_id,
            Order.customer_mobile == state.mobile,
            Order.status != "cancelled"
        ).order_by(Order.created_at.desc()).limit(3).all()

        if not orders:
            await self.send_message(state.mobile,
                "No previous orders found. Type 'catalog' to start shopping.")
            return

        ctx = state.context or {}
        ctx["reorder_list"] = [
            {"order_id": o.id, "notes": o.notes, "product_name": o.product_name}
            for o in orders
        ]
        state.context = ctx
        state.current_state = _AWAITING_REORDER_CHOICE

        lines = ["*Recent Orders — reply with number to reorder*\n"]
        for idx, o in enumerate(orders, 1):
            lines.append(f"{idx}. {o.product_name} — Rs.{o.total_amount:.0f}")
        lines.append("\nOr type 'cancel' to go back.")
        await self.send_message(state.mobile, "\n".join(lines))

    async def _handle_awaiting_reorder_choice(self, state: ConversationState, text: str):
        msg = text.strip()
        ctx = state.context or {}
        reorder_list = ctx.get("reorder_list", [])

        if msg.lower() in ["cancel", "back", "menu"]:
            ctx.pop("reorder_list", None)
            state.context = ctx
            state.current_state = _IDLE
            await self.send_message(state.mobile, "Reorder cancelled. Type 'menu' to start over.")
            return

        try:
            choice = int(msg)
        except ValueError:
            await self.send_message(state.mobile,
                f"Please reply with a number (1–{len(reorder_list)}) or 'cancel'.")
            return

        if not (1 <= choice <= len(reorder_list)):
            await self.send_message(state.mobile,
                f"Please choose a number between 1 and {len(reorder_list)}.")
            return

        chosen = reorder_list[choice - 1]
        notes_raw = chosen.get("notes")
        raw_cart_items = []
        if notes_raw:
            try:
                raw_cart_items = json.loads(notes_raw).get("cart", [])
            except (json.JSONDecodeError, AttributeError):
                pass

        cart = []
        for item in raw_cart_items:
            sku_code = item.get("sku")
            if not sku_code:
                continue
            sku_rec = self.db.query(ProductSKU).filter(
                ProductSKU.sku == sku_code,
                ProductSKU.tenant_id == self.tenant_id,
            ).first()
            if sku_rec:
                qty = item.get("qty", 1)
                price = sku_rec.seasonal_price or sku_rec.selling_price
                cart.append({
                    "sku": sku_code,
                    "product_name": sku_rec.product_name,
                    "qty": qty,
                    "unit_price": float(price),
                    "subtotal": float(price * qty),
                })

        if not cart:
            await self.send_message(state.mobile,
                "Could not rebuild that order — items may be unavailable.\n"
                "Type a SKU code or 'catalog' to browse.")
            ctx.pop("reorder_list", None)
            state.context = ctx
            state.current_state = _IDLE
            return

        ctx["cart"] = cart
        ctx.pop("reorder_list", None)
        state.context = ctx
        state.current_state = _BROWSING_CART

        total = sum(i["subtotal"] for i in cart)
        lines = ["*Cart loaded from previous order:*\n"]
        for item in cart:
            lines.append(f"• {item['product_name']} x{item['qty']} — Rs.{item['subtotal']:.0f}")
        lines.append(f"\nTotal: *Rs.{total:.0f}*")
        lines.append("\nType *checkout* to place order or *add more* to continue shopping.")
        await self.send_message(state.mobile, "\n".join(lines))

    async def _handle_awaiting_notify_confirm(self, state: ConversationState, text: str):
        msg = text.strip().upper()
        ctx = state.context or {}
        notify_sku = ctx.get("notify_sku")

        if msg == "NOTIFY" and notify_sku:
            from app.models.inventory import StockWatchlist
            existing = self.db.query(StockWatchlist).filter(
                StockWatchlist.tenant_id == self.tenant_id,
                StockWatchlist.mobile == state.mobile,
                StockWatchlist.sku == notify_sku,
                StockWatchlist.notified_at.is_(None),
            ).first()
            if not existing:
                self.db.add(StockWatchlist(
                    tenant_id=self.tenant_id,
                    mobile=state.mobile,
                    sku=notify_sku,
                ))
            ctx.pop("notify_sku", None)
            state.context = ctx
            state.current_state = _IDLE
            await self.send_message(state.mobile,
                f"Got it! We'll WhatsApp you as soon as *{notify_sku}* is back in stock.")
        elif msg in ["CATALOG", "BROWSE", "MENU"]:
            ctx.pop("notify_sku", None)
            state.context = ctx
            state.current_state = _IDLE
            await self._send_catalog(state.mobile)
        else:
            ctx.pop("notify_sku", None)
            state.context = ctx
            state.current_state = _IDLE
            await self.send_message(state.mobile,
                "No problem! Type 'catalog' to browse other products.")

    async def _create_and_send_payment_link(
        self, order: Order, mobile: str, amount: float
    ) -> Optional[str]:
        if not self.tenant:
            return None
        razorpay_key = getattr(self.tenant, "razorpay_key", None)
        razorpay_secret = getattr(self.tenant, "razorpay_secret", None)
        if not razorpay_key or not razorpay_secret:
            return None

        from app.services.razorpay_service import RazorpayService
        payment_link = await RazorpayService.create_payment_link(
            tenant_id=self.tenant_id,
            order_id=order.id,
            amount=amount,
            customer_mobile=mobile,
            razorpay_key=razorpay_key,
            razorpay_secret=razorpay_secret,
            business_name=self.tenant.business_name,
        )
        if payment_link:
            order.payment_id = payment_link.get("id")
            return payment_link.get("short_url")
        return None

    async def _alert_merchant_b2b_order(
        self, order_id: int, business_name: str, amount: float, payment_terms: int
    ):
        owner_mobile = getattr(self.tenant, "owner_mobile", None)
        if not owner_mobile or not self.phone_id or not self.token:
            return
        msg = (
            f"B2B Order #{order_id}\n"
            f"Business: {business_name}\n"
            f"Amount: Rs.{amount:.0f}\n"
            f"Payment Terms: {payment_terms} days credit"
        )
        send_whatsapp_message(owner_mobile, msg, self.phone_id, self.token)

    async def _alert_merchant_new_order(
        self, order_id: int, customer_mobile: str, amount: float
    ):
        owner_mobile = getattr(self.tenant, "owner_mobile", None)
        if not owner_mobile or not self.phone_id or not self.token:
            return
        msg = (
            f"New Order #{order_id}\n"
            f"Customer: {customer_mobile}\n"
            f"Amount: Rs.{amount:.0f}\n"
            "Check dashboard for details."
        )
        send_whatsapp_message(owner_mobile, msg, self.phone_id, self.token)

    def _welcome_text(self, b2b_customer=None) -> str:
        name = self.tenant.business_name if self.tenant else "our shop"
        if b2b_customer:
            credit_available = b2b_customer.credit_limit - b2b_customer.credit_used
            return (
                f"Welcome back, *{b2b_customer.business_name}*!\n\n"
                f"Tier: *{b2b_customer.customer_tier.upper()}* | "
                f"Credit available: Rs.{credit_available:.0f}\n\n"
                "• Send a *SKU code* to order at wholesale prices\n"
                "• Type *catalog* to browse\n"
                "• Type *cart* to view your cart"
            )
        return (
            f"Welcome to *{name}*!\n\n"
            "What would you like to do?\n"
            "• Send a *SKU code* to order\n"
            "• Type *catalog* to browse\n"
            "• Type *cart* to view your cart\n"
            "• Type *reorder* to repeat a past order\n"
            "• Type *RETURN #1001* to request a return"
        )

    # ------------------------------------------------------------------
    # Language helpers (4.6 — vernacular support)
    # ------------------------------------------------------------------

    async def _llm_call(self, prompt: str) -> str:
        """Single-shot OpenAI call; returns empty string on failure."""
        from app.core.config import settings
        api_key = getattr(settings, "openai_api_key", None)
        if not api_key:
            return ""
        try:
            import httpx as _httpx
            async with _httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 256,
                        "temperature": 0,
                    },
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            request_logger.warning(f"LLM call failed: {e}")
            return ""

    async def _detect_and_cache_language(
        self, text: str, state: ConversationState, ctx: dict
    ) -> str:
        cached = ctx.get("lang")
        if cached and cached != "en":
            return cached
        result = await self._llm_call(
            f"Detect the language of the following text. Reply with the ISO 639-1 code only "
            f"(e.g. 'hi', 'ta', 'gu', 'en'). Text: {text}"
        )
        lang = result.lower().strip()[:2] if result else "en"
        if lang != ctx.get("lang"):
            ctx["lang"] = lang
            state.context = ctx
        return lang

    async def _translate_to_english(self, text: str) -> str:
        result = await self._llm_call(
            f"Translate the following text to English. Reply with the translation only, "
            f"no explanation. Text: {text}"
        )
        return result if result else text

    async def _maybe_translate(self, text: str) -> str:
        """Translate outgoing message to customer language if not English."""
        lang = getattr(self, "_customer_lang", "en")
        if lang == "en":
            return text
        result = await self._llm_call(
            f"Translate the following text to {lang} language. "
            f"Preserve formatting (asterisks, line breaks). Reply with the translation only. "
            f"Text:\n{text}"
        )
        return result if result else text

    async def send_message(self, mobile: str, text: str):
        # Translate to customer language if not English
        text = await self._maybe_translate(text)

        if not self.phone_id or not self.token:
            request_logger.warning(f"WhatsApp credentials missing for tenant {self.tenant_id}")
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
                resp = await client.post(url, json=payload, headers=headers, timeout=10)
                resp.raise_for_status()
        except Exception as e:
            request_logger.error(f"WhatsApp send failed: {str(e)}")

    async def send_image(self, mobile: str, image_url: str, caption: str):
        if not self.phone_id or not self.token:
            await self.send_message(mobile, caption)
            return

        url = f"https://graph.facebook.com/v17.0/{self.phone_id}/messages"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "image",
            "image": {"link": image_url, "caption": caption}
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers, timeout=10)
                resp.raise_for_status()
        except Exception as e:
            request_logger.error(f"WhatsApp image send failed: {str(e)}")
            await self.send_message(mobile, caption)

    # ------------------------------------------------------------------
    # Outbound notification helpers (called from orders/procurement/tasks)
    # ------------------------------------------------------------------

    @classmethod
    def _send(cls, tenant: Tenant, mobile: str, text: str):
        """Synchronous send via whatsapp_sender for use in non-async contexts."""
        phone_id = getattr(tenant, "whatsapp_phone_id", None)
        token = getattr(tenant, "whatsapp_token", None)
        if not phone_id or not token or not mobile:
            request_logger.warning(
                f"WhatsApp notification skipped — missing credentials or mobile "
                f"(tenant={tenant.tenant_id})"
            )
            return
        send_whatsapp_message(mobile, text, phone_id, token)

    @classmethod
    async def send_order_confirmation(
        cls, tenant: Tenant, mobile: str, order_id: int, grand_total: float
    ):
        msg = (
            f"Your order #{order_id} has been placed!\n"
            f"Total: Rs.{grand_total:.0f}\n"
            "We will notify you once it ships."
        )
        cls._send(tenant, mobile, msg)

    @classmethod
    async def send_dispatch_notification(
        cls, tenant: Tenant, mobile: str, order_id: int, tracking_number: str
    ):
        msg = (
            f"Your order #{order_id} has been shipped!\n"
            f"Tracking: {tracking_number}\n"
            "Thank you for shopping with us!"
        )
        cls._send(tenant, mobile, msg)

    @classmethod
    async def send_delivery_notification(
        cls, tenant: Tenant, mobile: str, order_id: int
    ):
        msg = (
            f"Your order #{order_id} has been delivered!\n"
            "Hope you love it. Type 'catalog' to shop again."
        )
        cls._send(tenant, mobile, msg)

    @classmethod
    async def send_new_order_alert(
        cls, tenant: Tenant, order_id: int, customer_mobile: str, grand_total: float
    ):
        owner_mobile = getattr(tenant, "owner_mobile", None)
        msg = (
            f"New Order #{order_id}\n"
            f"Customer: {customer_mobile}\n"
            f"Amount: Rs.{grand_total:.0f}"
        )
        cls._send(tenant, owner_mobile, msg)

    @classmethod
    async def send_payment_received_alert(
        cls, tenant: Tenant, order_id: int, amount: float
    ):
        owner_mobile = getattr(tenant, "owner_mobile", None)
        msg = f"Payment received for Order #{order_id} — Rs.{amount:.0f}"
        cls._send(tenant, owner_mobile, msg)

    @classmethod
    async def send_stock_alert(
        cls, tenant: Tenant, owner_mobile: str, sku: str, current_stock: int
    ):
        msg = (
            f"Low Stock Alert\n"
            f"SKU: {sku}\n"
            f"Current stock: {current_stock} units\n"
            "Please reorder soon."
        )
        cls._send(tenant, owner_mobile, msg)

    @classmethod
    async def send_b2b_order_alert(
        cls, tenant: Tenant, order_id: int, business_name: str,
        amount: float, payment_terms: int
    ):
        owner_mobile = getattr(tenant, "owner_mobile", None)
        msg = (
            f"B2B Order #{order_id}\n"
            f"Business: {business_name}\n"
            f"Amount: Rs.{amount:.0f}\n"
            f"Payment Terms: {payment_terms} days credit"
        )
        cls._send(tenant, owner_mobile, msg)

    @classmethod
    async def send_return_approved(
        cls, tenant: Tenant, mobile: str, return_id: int
    ):
        msg = (
            f"Return #{return_id} has been approved!\n"
            "Our team will contact you shortly to schedule a pickup."
        )
        cls._send(tenant, mobile, msg)

    @classmethod
    async def send_return_rejected(
        cls, tenant: Tenant, mobile: str, return_id: int, reason: str
    ):
        msg = (
            f"Return #{return_id} could not be approved.\n"
            f"Reason: {reason}\n"
            "Contact us for assistance."
        )
        cls._send(tenant, mobile, msg)

    @classmethod
    async def send_return_pickup_scheduled(
        cls, tenant: Tenant, mobile: str, return_id: int, pickup_date: str
    ):
        msg = (
            f"Pickup scheduled for Return #{return_id}!\n"
            f"Date: {pickup_date}\n"
            "Please keep the item ready for collection."
        )
        cls._send(tenant, mobile, msg)

    @classmethod
    async def send_refund_processed(
        cls, tenant: Tenant, mobile: str, return_id: int, amount: float, method: str
    ):
        msg = (
            f"Refund processed for Return #{return_id}\n"
            f"Amount: Rs.{amount:.0f} via {method}\n"
            "It may take 3-5 business days to reflect."
        )
        cls._send(tenant, mobile, msg)
