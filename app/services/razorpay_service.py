import httpx
from typing import Dict, Any, Optional
from app.core.logger import request_logger
from app.core.config import settings


class RazorpayService:
    @staticmethod
    async def create_payment_link(
        tenant_id: str,
        order_id: int,
        amount: float,
        customer_mobile: str,
        razorpay_key: str,
        razorpay_secret: str,
        business_name: str
    ) -> Optional[Dict[str, Any]]:
        """Create a Razorpay Payment Link for a specific tenant order."""
        if not razorpay_key or not razorpay_secret:
            request_logger.warning(f"Razorpay credentials missing for tenant: {tenant_id}")
            return None

        amount_paise = int(amount * 100)
        callback_url = f"{settings.app_base_url.rstrip('/')}/static/payment-success.html?order={order_id}"

        payload = {
            "amount": amount_paise,
            "currency": "INR",
            "accept_partial": False,
            "description": f"Order #{order_id} from {business_name}",
            "customer": {
                "contact": customer_mobile
            },
            "notify": {
                "sms": True,
                "email": False
            },
            "reminder_enable": True,
            "notes": {
                "tenant_id": tenant_id,
                "order_id": str(order_id)
            },
            "callback_url": callback_url,
            "callback_method": "get"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.razorpay.com/v1/payment_links",
                    json=payload,
                    auth=(razorpay_key, razorpay_secret),
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            request_logger.error(f"Razorpay Link Creation Failed for {tenant_id}: {str(e)}")
            return None

    @staticmethod
    async def get_payment_link_status(
        payment_link_id: str,
        razorpay_key: str,
        razorpay_secret: str,
    ) -> Optional[Dict[str, Any]]:
        """Fetch current status of a Razorpay payment link."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.razorpay.com/v1/payment_links/{payment_link_id}",
                    auth=(razorpay_key, razorpay_secret),
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            request_logger.error(f"Razorpay status check failed for {payment_link_id}: {str(e)}")
            return None
