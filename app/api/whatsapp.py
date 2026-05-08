from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.whatsapp_bot_service import WhatsAppBotService
from app.core.logger import request_logger

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Bot"])

# VERIFICATION_TOKEN for Meta Webhook setup
VERIFY_TOKEN = "saas_wa_verify_token_2026"

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Verify Meta Webhook."""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def handle_whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming messages from Meta."""
    data = await request.json()
    
    try:
        # 1. Parse Meta JSON
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return {"status": "ignored"}
            
        message = messages[0]
        mobile = message.get("from")
        text = message.get("text", {}).get("body")
        
        # 2. Identify Tenant (Based on Phone Number ID)
        # In a real SaaS, we map Meta Phone ID to Tenant ID
        # For demo, we'll use a test tenant or look it up
        phone_id = value.get("metadata", {}).get("phone_number_id")
        
        from app.models.tenant import Tenant
        tenant = db.query(Tenant).filter(Tenant.whatsapp_phone_id == phone_id).first()
        
        if not tenant:
            # Fallback for testing/unconfigured
            tenant_id = "test_tenant_bulk" 
        else:
            tenant_id = tenant.tenant_id

        # 3. Process via Bot Service
        bot = WhatsAppBotService(db, tenant_id)
        await bot.handle_incoming(mobile, text)
        
        return {"status": "success"}
        
    except Exception as e:
        request_logger.error(f"WhatsApp Webhook Error: {str(e)}")
        # Meta expects 200 even on error to stop retries, but we'll log it
        return {"status": "error", "detail": str(e)}

@router.post("/test-incoming")
async def test_incoming_message(
    mobile: str, 
    text: str, 
    tenant_id: str = "test_tenant_bulk",
    db: Session = Depends(get_db)
):
    """Simulate an incoming WhatsApp message for testing."""
    bot = WhatsAppBotService(db, tenant_id)
    await bot.handle_incoming(mobile, text)
    return {"status": "simulated"}
