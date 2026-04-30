from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from pydantic import BaseModel
from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.order import Order
from app.models.product import Product
from app.schemas.admin import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantMetrics,
    AdminDashboard,
)
from app.core.config import settings
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])


def verify_admin_token(authorization: str = None):
    """Verify admin token from Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization scheme",
            )
        if token != settings.admin_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin token",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )


@router.post("/login", response_model=dict)
async def admin_login(credentials: dict):
    """Admin login endpoint"""
    if credentials.get("password") != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password",
        )

    return {
        "access_token": settings.admin_token,
        "token_type": "bearer",
    }


@router.get("/dashboard", response_model=AdminDashboard)
async def get_dashboard(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get admin dashboard overview"""
    verify_admin_token(authorization)
    
    total_tenants = db.query(func.count(Tenant.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_products = db.query(func.count(Product.id)).scalar()
    
    # Calculate revenue
    total_revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(Order.status == "completed")
        .scalar() or 0.0
    )
    
    return AdminDashboard(
        total_tenants=total_tenants,
        total_orders=total_orders,
        total_products=total_products,
        total_revenue=float(total_revenue),
    )


@router.get("/tenants", response_model=list[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 10,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """List all tenants with pagination"""
    verify_admin_token(authorization)
    
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    return tenants


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get specific tenant details"""
    verify_admin_token(authorization)
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    return tenant


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant: TenantCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Create new tenant"""
    verify_admin_token(authorization)
    
    # Check if tenant already exists
    existing = db.query(Tenant).filter(Tenant.tenant_id == tenant.tenant_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant already exists",
        )
    
    # Check if WhatsApp number already registered
    existing_whatsapp = (
        db.query(Tenant)
        .filter(Tenant.whatsapp_number == tenant.whatsapp_number)
        .first()
    )
    if existing_whatsapp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp number already registered",
        )
    
    new_tenant = Tenant(
        tenant_id=tenant.tenant_id,
        business_name=tenant.business_name,
        whatsapp_number=tenant.whatsapp_number,
        odoo_url=tenant.odoo_url,
        odoo_db=tenant.odoo_db,
        odoo_user=tenant.odoo_user,
        odoo_password=tenant.odoo_password,
        razorpay_key=tenant.razorpay_key,
        razorpay_secret=tenant.razorpay_secret,
        n8n_webhook_url=tenant.n8n_webhook_url,
    )
    
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    
    return new_tenant


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    tenant_update: TenantUpdate,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Update tenant configuration (Admin only)"""
    verify_admin_token(authorization)
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Update fields from schema
    update_data = tenant_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tenant, key, value)
    
    db.commit()
    db.refresh(tenant)
    
    return tenant


@router.post("/tenants/{tenant_id}/test-odoo")
async def test_tenant_odoo(
    tenant_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Test the Odoo ERP link for a tenant (Admin only)."""
    from app.integrations.odoo_base import OdooClient
    
    verify_admin_token(authorization)
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant or not tenant.odoo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant or Odoo config missing",
        )
    
    try:
        client = OdooClient(tenant.odoo_url, tenant.odoo_db, tenant.odoo_user, tenant.odoo_password)
        if client.authenticate():
            return {"status": "success", "message": "ERP Connection Verified"}
        return {"status": "error", "message": "Authentication Failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Delete tenant"""
    verify_admin_token(authorization)
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    db.delete(tenant)
    db.commit()
    
    return {"message": "Tenant deleted successfully"}


@router.get("/tenants/{tenant_id}/metrics", response_model=TenantMetrics)
async def get_tenant_metrics(
    tenant_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get metrics for specific tenant"""
    verify_admin_token(authorization)
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    total_orders = (
        db.query(func.count(Order.id))
        .filter(Order.tenant_id == tenant.id)
        .scalar()
    )
    
    completed_orders = (
        db.query(func.count(Order.id))
        .filter(Order.tenant_id == tenant.id, Order.status == "completed")
        .scalar()
    )
    
    total_revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(Order.tenant_id == tenant.id, Order.status == "completed")
        .scalar() or 0.0
    )
    
    total_products = (
        db.query(func.count(Product.id))
        .filter(Product.tenant_id == tenant.id)
        .scalar()
    )
    
    return TenantMetrics(
        tenant_id=tenant_id,
        total_orders=total_orders,
        completed_orders=completed_orders,
        total_revenue=float(total_revenue),
        total_products=total_products,
    )


# ─── Supplier Email Notification Management ────────────────────────────────────

class SupplierEmailSettingsResponse(BaseModel):
    tenant_id: str
    is_enabled: bool
    cooldown_hours: int
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SupplierEmailSettingsUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    cooldown_hours: Optional[int] = None


class SupplierNotificationResponse(BaseModel):
    id: int
    tenant_id: str
    alert_id: Optional[int]
    recipient: str
    notification_type: str
    channel: str
    status: str
    sent_at: Optional[datetime]
    retries: int
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/tenants/{tenant_id}/supplier-email-settings", response_model=SupplierEmailSettingsResponse)
async def get_supplier_email_settings(
    tenant_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get supplier email notification settings for a tenant."""
    verify_admin_token(authorization)
    from app.models.procurement import SupplierEmailSettings

    settings_obj = db.query(SupplierEmailSettings).filter(
        SupplierEmailSettings.tenant_id == tenant_id
    ).first()

    if not settings_obj:
        # Return defaults if not yet configured
        return SupplierEmailSettingsResponse(
            tenant_id=tenant_id,
            is_enabled=True,
            cooldown_hours=24,
            updated_at=None,
        )

    return settings_obj


@router.put("/tenants/{tenant_id}/supplier-email-settings", response_model=SupplierEmailSettingsResponse)
async def update_supplier_email_settings(
    tenant_id: str,
    body: SupplierEmailSettingsUpdate,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Update supplier email notification settings.
    - is_enabled: false pauses all outgoing supplier emails for this tenant
    - cooldown_hours: minimum hours between emails to the same supplier for the same product
    """
    verify_admin_token(authorization)
    from app.models.procurement import SupplierEmailSettings

    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    settings_obj = db.query(SupplierEmailSettings).filter(
        SupplierEmailSettings.tenant_id == tenant_id
    ).first()

    if not settings_obj:
        settings_obj = SupplierEmailSettings(tenant_id=tenant_id)
        db.add(settings_obj)

    if body.is_enabled is not None:
        settings_obj.is_enabled = body.is_enabled
    if body.cooldown_hours is not None:
        if body.cooldown_hours < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cooldown_hours must be >= 1")
        settings_obj.cooldown_hours = body.cooldown_hours

    db.commit()
    db.refresh(settings_obj)
    return settings_obj


@router.get("/tenants/{tenant_id}/supplier-notifications", response_model=List[SupplierNotificationResponse])
async def list_supplier_notifications(
    tenant_id: str,
    status_filter: Optional[str] = Query(None, alias="status", description="pending | sent | failed"),
    supplier_email: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """List supplier email notifications for a tenant with optional filters."""
    verify_admin_token(authorization)
    from app.models.inventory import InventoryNotification

    query = db.query(InventoryNotification).filter(
        InventoryNotification.tenant_id == tenant_id,
        InventoryNotification.channel == "email",
    )

    if status_filter:
        query = query.filter(InventoryNotification.status == status_filter)
    if supplier_email:
        query = query.filter(InventoryNotification.recipient == supplier_email)

    return query.order_by(InventoryNotification.created_at.desc()).offset(skip).limit(limit).all()


@router.delete("/tenants/{tenant_id}/supplier-notifications/{notification_id}")
async def cancel_supplier_notification(
    tenant_id: str,
    notification_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Cancel a pending supplier email notification so it won't be sent.
    Only pending notifications can be cancelled.
    """
    verify_admin_token(authorization)
    from app.models.inventory import InventoryNotification

    notif = db.query(InventoryNotification).filter(
        InventoryNotification.id == notification_id,
        InventoryNotification.tenant_id == tenant_id,
        InventoryNotification.channel == "email",
    ).first()

    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if notif.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a notification with status '{notif.status}'"
        )

    notif.status = "failed"
    db.commit()
    return {"message": "Notification cancelled successfully", "id": notification_id}
