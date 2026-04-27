from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class OrderReturn(Base):
    """Tracks product returns from customers"""
    __tablename__ = "order_returns"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    
    quantity = Column(Integer)
    reason = Column(String(255)) # e.g., "Faulty", "Wrong Size", "Not as described"
    condition = Column(String(50)) # e.g., "resellable", "damaged", "opened"
    
    status = Column(String(50), default="pending") # pending, approved, rejected, received
    return_date = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processed_by = Column(String, nullable=True) # User ID who approved/rejected
    
    # Financial linkage
    refund_id = Column(Integer, ForeignKey("refunds.id"), nullable=True)
    
    order = relationship("Order")
    refund = relationship("Refund", back_populates="order_return")

class Refund(Base):
    """Tracks financial refunds to customers"""
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    
    amount = Column(Float)
    currency = Column(String(10), default="INR")
    refund_method = Column(String(50)) # original_payment, store_credit, bank_transfer
    
    status = Column(String(50), default="pending") # pending, completed, failed
    transaction_id = Column(String(255), nullable=True) # From payment gateway
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    order_return = relationship("OrderReturn", back_populates="refund", uselist=False)
