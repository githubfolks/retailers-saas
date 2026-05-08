from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from datetime import datetime
from app.core.database import Base


class B2BCustomer(Base):
    __tablename__ = "b2b_customers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    business_name = Column(String, index=True)
    contact_person = Column(String, nullable=True)
    mobile = Column(String, index=True)
    email = Column(String, nullable=True)
    gstin = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    credit_limit = Column(Float, default=0.0)
    credit_used = Column(Float, default=0.0)
    payment_terms_days = Column(Integer, default=30)
    customer_tier = Column(String, default="bronze")  # gold, silver, bronze
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WholesalePriceList(Base):
    __tablename__ = "wholesale_price_lists"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    tier = Column(String, index=True)  # gold, silver, bronze
    sku = Column(String, index=True)
    min_qty = Column(Integer, default=1)
    unit_price = Column(Float)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class B2BOrder(Base):
    __tablename__ = "b2b_orders"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    b2b_customer_id = Column(Integer, ForeignKey("b2b_customers.id"), index=True)
    po_reference = Column(String, nullable=True)  # buyer's own PO number
    status = Column(String, default="pending")  # pending, confirmed, shipped, delivered, cancelled
    payment_status = Column(String, default="pending")  # pending, partial, paid
    payment_terms_days = Column(Integer, default=30)
    due_date = Column(DateTime, nullable=True)
    items = Column(Text)  # JSON: [{sku, product_name, qty, unit_price, subtotal}]
    total_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    shipping_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
