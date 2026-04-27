from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index
from datetime import datetime
from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_tenant_status", "tenant_id", "status"),
        Index("ix_orders_tenant_created_at", "tenant_id", "created_at"),
        Index("ix_orders_tenant_payment_status", "tenant_id", "payment_status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_mobile = Column(String, index=True)
    sku = Column(String, index=True, nullable=True) # Linked to product_skus catalog
    product_name = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_amount = Column(Float)
    status = Column(String, default="pending", index=True)
    payment_status = Column(String, default="pending")
    payment_id = Column(String, nullable=True)
    odoo_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Financial Stability & Margin Tracking
    unit_cost_at_sale = Column(Float, nullable=True) # Historical cost for profit audit
    discount_amount = Column(Float, default=0.0)
    coupon_code = Column(String(50), nullable=True)
    
    # Logistics & Scheduling (sale_order_dates)
    commitment_date = Column(DateTime, nullable=True) # Promised delivery
    effective_delivery_date = Column(DateTime, nullable=True) # Actual delivery

    # Invoicing & Logistics Fields
    invoice_number = Column(String(50), unique=True, nullable=True, index=True)
    shipping_address = Column(Text, nullable=True) # Full address block
    customer_state = Column(String, nullable=True) # For GST logic
    tax_type = Column(String(10), nullable=True)   # IGST or CGST/SGST
    tax_amount = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)       # total_amount + tax_amount

    # GST Component Breakdown (for GSTR-1 filing)
    gst_rate = Column(Float, default=0.0)          # Actual % applied (5 or 12)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    customer_gstin = Column(String(15), nullable=True)  # B2B orders
    hsn_code = Column(String(10), nullable=True)   # Snapshot at time of sale

    # POS & Channel Tracking
    payment_method = Column(String(20), nullable=True)  # cash, upi, card
    source = Column(String(20), default="whatsapp")     # whatsapp, pos, web
