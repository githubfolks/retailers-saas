import hmac
import hashlib
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from typing import Dict, Any
from app.core.logger import request_logger

router = APIRouter(prefix="/payment", tags=["payment"])


def verify_razorpay_signature(
    payload: str,
    signature: str,
    secret: str
) -> bool:
    """
    Verify Razorpay webhook signature using HMAC SHA256.
    
    Args:
        payload: Request body as string
        signature: Signature from X-Razorpay-Signature header
        secret: Razorpay API secret key
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        generated_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(generated_signature, signature)
    
    except Exception as e:
        request_logger.error(f"Error verifying signature: {str(e)}")
        return False


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle multi-tenant Razorpay webhooks with dynamic signature verification."""
    from app.models.tenant import Tenant
    
    try:
        signature = request.headers.get("X-Razorpay-Signature")
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        body = await request.body()
        body_str = body.decode()
        payload = json.loads(body_str)
        
        # 1. Resolve Tenant from Payload Notes
        # We stored tenant_id in the 'notes' during link creation
        data = payload.get("payload", {})
        payment_link = data.get("payment_link", {}) or data.get("payment", {})
        notes = payment_link.get("notes", {})
        tenant_id = notes.get("tenant_id")
        
        if not tenant_id:
            request_logger.error("Webhook payload missing tenant_id in notes")
            return {"status": "error", "message": "unresolved_tenant"}

        # 2. Fetch Tenant Security Keys
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant or not tenant.razorpay_secret:
            request_logger.error(f"Tenant {tenant_id} configuration not found for webhook")
            return {"status": "error", "message": "tenant_config_missing"}

        # 3. Verify Signature
        if not verify_razorpay_signature(body_str, signature, tenant.razorpay_secret):
            request_logger.error(f"Invalid signature for tenant: {tenant_id}")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # 4. Process Event
        event = payload.get("event")
        if event == "payment_link.completed":
            return await handle_payment_completed(payload, db, tenant)
        elif event == "payment.captured":
            return await handle_payment_completed(payload, db, tenant)
        
        return {"status": "received", "event": event}
    
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error(f"Payment Webhook Error: {str(e)}")
        return {"status": "error", "detail": str(e)}


async def handle_payment_completed(payload: Dict[str, Any], db: Session, tenant: Any):
    """Update order status and trigger fulfillment workflows."""
    from app.services.n8n_service import N8NService
    from app.models.order import Order
    
    try:
        data = payload.get("payload", {})
        payment_link = data.get("payment_link", {}) or data.get("payment", {})
        notes = payment_link.get("notes", {})
        order_id = notes.get("order_id")
        
        if not order_id:
            return {"status": "error", "message": "order_id_missing"}

        # Update Local Database
        order = db.query(Order).filter(Order.id == int(order_id)).first()
        if order:
            order.payment_status = "completed"
            order.status = "processing"
            db.commit()
            
            # Trigger n8n Workflow
            if tenant.n8n_webhook_url:
                import asyncio
                asyncio.create_task(N8NService.trigger_payment_flow(
                    tenant.n8n_webhook_url,
                    order.id,
                    payment_link.get("id")
                ))
            
            request_logger.info(f"Order {order_id} marked as PAID for {tenant.tenant_id}")
            return {"status": "success", "order_id": order_id}
            
        return {"status": "not_found"}
        
    except Exception as e:
        request_logger.error(f"Fulfillment Logic Failed: {str(e)}")
        return {"status": "error"}
