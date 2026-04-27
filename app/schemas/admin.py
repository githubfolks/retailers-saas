from pydantic import BaseModel
from typing import Optional


class TenantCreate(BaseModel):
    tenant_id: str
    business_name: str
    whatsapp_number: str
    odoo_url: str
    odoo_db: str
    odoo_user: str
    odoo_password: str
    razorpay_key: str
    razorpay_secret: str
    n8n_webhook_url: Optional[str] = None


class TenantUpdate(BaseModel):
    business_name: Optional[str] = None
    whatsapp_number: Optional[str] = None
    odoo_url: Optional[str] = None
    odoo_db: Optional[str] = None
    odoo_user: Optional[str] = None
    odoo_password: Optional[str] = None
    razorpay_key: Optional[str] = None
    razorpay_secret: Optional[str] = None
    n8n_webhook_url: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None


class TenantResponse(BaseModel):
    id: int
    tenant_id: str
    business_name: str
    whatsapp_number: Optional[str] = None
    odoo_url: Optional[str] = None
    odoo_db: Optional[str] = None
    odoo_user: Optional[str] = None
    razorpay_key: Optional[str] = None
    primary_color: Optional[str] = "#0d9488"
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True


class TenantMetrics(BaseModel):
    tenant_id: str
    total_orders: int
    completed_orders: int
    total_revenue: float
    total_products: int


class AdminDashboard(BaseModel):
    total_tenants: int
    total_orders: int
    total_products: int
    total_revenue: float
