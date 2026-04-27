from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class StockValuationLayer(Base):
    """
    FIFO Stock Valuation Layer
    Tracks specific quantities received at specific costs
    """
    __tablename__ = "stock_valuation_layers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    sku = Column(String(255), index=True)
    
    # Financial data
    original_quantity = Column(Float)
    remaining_quantity = Column(Float)
    unit_cost = Column(Float) # Base cost from PO
    total_value = Column(Float) # qty * unit_cost
    
    # Reference
    reference_id = Column(String, index=True) # PO ID or Receipt ID
    reference_type = Column(String) # "purchase_order", "adjustment", "return"
    
    # Landed Costs
    landed_cost_value = Column(Float, default=0.0) # Sum of freight, duties, etc. allocated
    
    # Status
    is_fully_consumed = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LandedCost(Base):
    """
    Additional costs associated with stock reception
    """
    __tablename__ = "landed_costs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    
    name = Column(String(255)) # e.g., "Freight Bill #123"
    cost_type = Column(String(50)) # freight, insurance, duty, storage
    amount = Column(Float)
    
    # Status
    status = Column(String, default="draft") # draft, validated
    
    # Reference
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)


class LandedCostAssignment(Base):
    """
    Allocation of landed costs to specific valuation layers
    """
    __tablename__ = "landed_cost_assignments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    
    landed_cost_id = Column(Integer, ForeignKey("landed_costs.id"))
    valuation_layer_id = Column(Integer, ForeignKey("stock_valuation_layers.id"))
    
    allocated_amount = Column(Float)
    allocation_method = Column(String) # equal, quantity, weight, volume, value
    
    created_at = Column(DateTime, default=datetime.utcnow)
