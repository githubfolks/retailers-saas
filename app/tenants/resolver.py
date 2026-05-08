from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.tenant import Tenant
from app.core.database import get_session


def resolve_tenant_by_whatsapp_number(
    whatsapp_number: str,
    db: Optional[Session] = None
) -> Optional[Dict[str, Any]]:
    db = db or get_session()
    
    try:
        tenant = db.query(Tenant).filter(
            Tenant.whatsapp_number == whatsapp_number
        ).first()
        
        if not tenant:
            return None
        
        tenant_config = {
            "id": tenant.id,
            "tenant_id": tenant.tenant_id,
            "business_name": tenant.business_name,
            "whatsapp_number": tenant.whatsapp_number,
            "razorpay_key": tenant.razorpay_key,
            "razorpay_secret": tenant.razorpay_secret,
            "n8n_webhook_url": tenant.n8n_webhook_url,
        }
        
        return tenant_config
    finally:
        if db:
            db.close()
