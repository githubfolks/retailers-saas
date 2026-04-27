from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.tenant import Tenant
from app.api.auth import get_current_tenant_id, check_owner
from app.integrations.odoo_base import OdooClient
from app.core.logger import request_logger

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SettingsUpdate(BaseModel):
    business_name: Optional[str] = None
    whatsapp_number: Optional[str] = None
    razorpay_key: Optional[str] = None
    razorpay_secret: Optional[str] = None
    n8n_webhook_url: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None
    gstin: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

class SettingsResponse(BaseModel):
    tenant_id: str
    business_name: str
    whatsapp_number: Optional[str] = None
    razorpay_key: Optional[str] = None
    n8n_webhook_url: Optional[str]
    primary_color: str
    logo_url: Optional[str]
    gstin: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    
    class Config:
        from_attributes = True

@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Fetch current merchant settings (Infrastructure fields omitted)."""
    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.patch("", response_model=SettingsResponse)
async def update_settings(
    settings: SettingsUpdate,
    user: dict = Depends(check_owner), # OWNER ONLY
    db: Session = Depends(get_db)
):
    """Update merchant settings (Owner Restricted)."""
    current_tenant_id = user["tenant_id"]
    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    update_data = settings.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tenant, key, value)
    
    db.commit()
    db.refresh(tenant)
    request_logger.info(f"Settings updated for tenant: {current_tenant_id} by Owner: {user['user_id']}")
    return tenant
