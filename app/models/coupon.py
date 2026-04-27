from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Coupon(Base):
    """Promotional coupons and discounts"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    
    code = Column(String(50), nullable=False) # e.g., "WELCOME10", "SUMMER24"
    discount_type = Column(String(20)) # "percentage" or "fixed"
    discount_value = Column(Float) # 10.0 for 10% or ₹10
    
    min_purchase_amount = Column(Float, default=0.0)
    max_discount_amount = Column(Float, nullable=True) # Cap for percentage discounts
    
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    
    usage_limit = Column(Integer, nullable=True) # Total uses allowed
    usage_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional: Link to specific categories or products
    # target_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
