import httpx
from typing import Dict, Any, Optional
from app.core.logger import request_logger

class N8NService:
    @staticmethod
    async def trigger_order_flow(webhook_url: str, order_data: Dict[str, Any]):
        """Fire an asynchronous webhook to n8n for order processing."""
        if not webhook_url:
            request_logger.warning("No n8n webhook URL configured for this tenant.")
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url, 
                    json={
                        "event": "order.created",
                        "data": order_data
                    },
                    timeout=5.0
                )
                response.raise_for_status()
                request_logger.info(f"n8n flow triggered for order {order_data.get('id')}")
        except Exception as e:
            request_logger.error(f"Failed to trigger n8n flow: {str(e)}")

    @staticmethod
    async def trigger_payment_flow(webhook_url: str, order_id: int, payment_id: str):
        """Fire an asynchronous webhook to n8n for payment confirmation."""
        if not webhook_url:
            return

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    webhook_url, 
                    json={
                        "event": "payment.success",
                        "order_id": order_id,
                        "payment_id": payment_id
                    },
                    timeout=5.0
                )
        except Exception as e:
            request_logger.error(f"Failed to trigger n8n payment flow: {str(e)}")
