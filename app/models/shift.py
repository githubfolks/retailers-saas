from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.core.database import Base

class Shift(Base):
    """POS Shift management for cash register accountability."""
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    opening_cash = Column(Float, default=0.0)
    closing_cash = Column(Float, nullable=True)
    
    # Financial reconciliation
    total_sales = Column(Float, default=0.0)
    total_returns = Column(Float, default=0.0)
    total_tax = Column(Float, default=0.0)
    expected_cash = Column(Float, default=0.0) # opening + sales - returns
    
    status = Column(String, default="open") # open, closed
    
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
