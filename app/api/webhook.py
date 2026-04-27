from fastapi import APIRouter, Query, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.webhook import WebhookPayload
from app.tenants.resolver import resolve_tenant_by_whatsapp_number
from app.core.logger import request_logger
from app.core.limiter import limiter

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(...),
    hub_challenge: str = Query(...),
    hub_verify_token: str = Query(...)
):
    if hub_mode != "subscribe":
        raise HTTPException(status_code=400, detail="Invalid hub mode")
    
    if hub_verify_token != settings.whatsapp_verify_token:
        raise HTTPException(status_code=403, detail="Invalid verify token")
    
    return int(hub_challenge)


@router.post("/webhook")
@limiter.limit("60/minute")
async def receive_message(
    request: Request,
    payload: WebhookPayload,
    db: Session = Depends(get_db)
):
    """Receive and respond to WhatsApp messages with LLM-powered AI Bot."""
    from app.services.llm_inventory_bot import LLMInventoryBot
    from app.integrations.whatsapp_outbound import WhatsAppOutbound
    from app.tenants.resolver import resolve_tenant_by_whatsapp_number
    import asyncio
    
    request_logger.info("Processing WhatsApp Webhook with LLM...")
    
    try:
        for entry in payload.entry:
            for change in entry.changes:
                if not change.value.messages:
                    continue
                
                for message in change.value.messages:
                    sender_number = message.from_
                    message_text = message.text.body if message.text else ""
                    
                    # Identify the Merchant (Tenant)
                    tenant_config = resolve_tenant_by_whatsapp_number(sender_number)
                    if not tenant_config:
                        request_logger.warning(f"No tenant mapping found for: {sender_number}")
                        continue
                    
                    # Process with LLM-powered Inventory Bot
                    bot = LLMInventoryBot(db, tenant_config["tenant_id"])
                    ai_response = await bot.process_whatsapp_message(message_text)
                    
                    # Respond via Outbound WhatsApp API
                    await WhatsAppOutbound.send_text(
                        to_number=sender_number,
                        text=ai_response,
                        tenant_config=tenant_config
                    )
        
        return {"status": "success"}
    
    except Exception as e:
        request_logger.error(f"WhatsApp Webhook Error: {str(e)}")
        return {"status": "error", "detail": str(e)}
