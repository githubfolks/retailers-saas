from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from datetime import datetime
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    mobile = Column(String, index=True)
    name = Column(String)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # CRM Insights
    total_spend = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)
    last_order_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
