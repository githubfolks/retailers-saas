from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, unique=True, index=True)
    business_name = Column(String)
    whatsapp_number = Column(String, unique=True, index=True)
    odoo_url = Column(String)
    odoo_db = Column(String)
    odoo_user = Column(String)
    odoo_password = Column(String)
    razorpay_key = Column(String)
    razorpay_secret = Column(String)
    n8n_webhook_url = Column(String, nullable=True)
    primary_color = Column(String, default="#0d9488")
    logo_url = Column(String, nullable=True)
    
    # WhatsApp Cloud API credentials
    whatsapp_phone_id = Column(String, nullable=True)
    whatsapp_token = Column(String, nullable=True)
    owner_mobile = Column(String, nullable=True)  # merchant's personal number for alerts

    # Business Profile for Invoicing
    gstin = Column(String(15), nullable=True)
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String(10), nullable=True)
