from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class OrderReturn(Base):
    """Tracks product returns from customers"""
    __tablename__ = "order_returns"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)

    quantity = Column(Integer)
    reason = Column(String(255))  # "Faulty", "Wrong Size", "Not as described"
    condition = Column(String(50))  # "resellable", "damaged", "opened"

    # Status flow:
    # return_requested → approved/rejected → pickup_scheduled → picked_up
    # → in_transit → received → inspected → completed
    status = Column(String(50), default="return_requested")

    pickup_address = Column(Text, nullable=True)      # Customer's pickup address
    return_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)

    return_date = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Financial linkage
    refund_id = Column(Integer, ForeignKey("refunds.id"), nullable=True)

    order = relationship("Order")
    refund = relationship("Refund", back_populates="order_return")
    pickup = relationship("ReturnPickup", back_populates="order_return", uselist=False)
    shipment = relationship("ReturnShipment", back_populates="order_return", uselist=False)
    inspection = relationship("ReturnInspection", back_populates="order_return", uselist=False)


class Refund(Base):
    """Tracks financial refunds to customers"""
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)

    amount = Column(Float)
    currency = Column(String(10), default="INR")
    refund_method = Column(String(50))  # original_payment, store_credit, bank_transfer

    status = Column(String(50), default="pending")  # pending, completed, failed
    transaction_id = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    order_return = relationship("OrderReturn", back_populates="refund", uselist=False)


class ReturnPickup(Base):
    """Schedules and tracks the physical pickup from the customer."""
    __tablename__ = "return_pickups"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    return_id = Column(Integer, ForeignKey("order_returns.id"), unique=True, index=True)

    pickup_address = Column(Text)
    scheduled_date = Column(DateTime)
    pickup_agent = Column(String(255), nullable=True)   # Name or ID of pickup agent/driver

    # Status: scheduled, attempted, picked_up, failed
    status = Column(String(50), default="scheduled")
    attempt_count = Column(Integer, default=0)
    failure_reason = Column(String(255), nullable=True)

    picked_up_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_return = relationship("OrderReturn", back_populates="pickup")


class ReturnShipment(Base):
    """Tracks the reverse shipment from customer back to warehouse."""
    __tablename__ = "return_shipments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    return_id = Column(Integer, ForeignKey("order_returns.id"), unique=True, index=True)

    carrier = Column(String(100))
    tracking_number = Column(String(255), nullable=True, index=True)
    label_url = Column(String(512), nullable=True)      # Return shipping label PDF

    # Status: label_generated, in_transit, received, lost
    status = Column(String(50), default="label_generated")

    shipped_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)
    receiving_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_return = relationship("OrderReturn", back_populates="shipment")


class ReturnInspection(Base):
    """Records item condition when it arrives back at the warehouse."""
    __tablename__ = "return_inspections"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    return_id = Column(Integer, ForeignKey("order_returns.id"), unique=True, index=True)

    inspected_by = Column(String(255))
    inspected_at = Column(DateTime, default=datetime.utcnow)

    # Condition at inspection — may differ from what customer declared
    condition = Column(String(50))  # resellable, damaged, destroyed
    approved_for_refund = Column(Boolean, default=True)
    refund_deduction_pct = Column(Float, default=0.0)   # % deducted for damage (0–100)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    order_return = relationship("OrderReturn", back_populates="inspection")
