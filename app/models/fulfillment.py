from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from datetime import datetime
from app.core.database import Base


class Fulfillment(Base):
    """
    Tracks the shipping and delivery lifecycle of an order
    """
    __tablename__ = "fulfillments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    
    # Shipment Tracking
    carrier_name = Column(String, nullable=True) # e.g., Delhivery, BlueDart
    tracking_number = Column(String, unique=True, nullable=True, index=True)
    shipping_label_url = Column(String, nullable=True) # URL to PDF
    
    # Status
    # picking, packing, shipped, out_for_delivery, delivered, cancelled
    status = Column(String, default="packing", index=True)
    
    # Datetimes
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Provider metadata
    provider_shipment_id = Column(String, nullable=True)
    shipping_cost = Column(Float, nullable=True)

    # Notes/Audit
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
