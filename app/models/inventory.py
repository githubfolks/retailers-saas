from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum, Index
from datetime import datetime
from app.core.database import Base
import enum


class StockLocation(Base):
    __tablename__ = "stock_locations"
    __table_args__ = (
        Index("ix_stock_locations_tenant_product", "tenant_id", "product_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    # Hierarchy & Type
    parent_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=True)
    location_type = Column(String(50), default="internal") # internal, view, transit, vendor, customer
    name = Column(String(100), index=True) # Location name e.g. "Row A-1"
    
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    zone_name = Column(String, nullable=True)  # e.g., "A1", "B2"
    bin_number = Column(String, nullable=True)
    
    # Flags
    is_scrap = Column(Boolean, default=False)
    is_clearance = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)  # Stock reserved for orders
    available_quantity = Column(Integer, default=0)  # quantity - reserved
    reorder_point = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=50)
    last_counted = Column(DateTime, nullable=True)
    last_stock_check = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=True)
    movement_type = Column(String)  # "in", "out", "adjustment", "transfer", "return"
    quantity = Column(Integer)  # Positive for IN, negative for OUT
    reference_id = Column(String, nullable=True)  # order_id, po_id, etc.
    reference_type = Column(String, nullable=True)  # "order", "po", "adjustment"
    reason = Column(String, nullable=True)  # "purchase", "sale", "damage", "lost", "transfer"
    created_by = Column(String)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class StockAlert(Base):
    __tablename__ = "stock_alerts"
    __table_args__ = (
        Index("ix_stock_alerts_tenant_status", "tenant_id", "status"),
        Index("ix_stock_alerts_tenant_product", "tenant_id", "product_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    alert_type = Column(String)  # "low_stock", "out_of_stock", "overstock", "slow_moving", "dead_stock"
    alert_level = Column(String)  # "info", "warning", "critical"
    threshold_value = Column(Integer)
    current_value = Column(Integer)
    status = Column(String, default="active")  # "active", "triggered", "acknowledged", "resolved"
    triggered_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class InventoryNotification(Base):
    __tablename__ = "inventory_notifications"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    alert_id = Column(Integer, ForeignKey("stock_alerts.id"), nullable=True)
    recipient = Column(String)  # phone number or email
    notification_type = Column(String)  # "low_stock", "out_of_stock", "forecast", "reorder_ready"
    channel = Column(String)  # "whatsapp", "sms", "email", "in_app"
    message = Column(Text)
    status = Column(String, default="pending")  # "pending", "sent", "failed", "read"
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    retries = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    forecast_date = Column(DateTime, index=True)  # Date being forecast
    forecast_period = Column(String)  # "daily", "weekly", "monthly"
    predicted_demand = Column(Float)
    confidence_level = Column(Float)  # 0-100
    model_type = Column(String)  # "arima", "prophet", "ml", "manual"
    lower_bound = Column(Float)  # 95% CI lower
    upper_bound = Column(Float)  # 95% CI upper
    actual_demand = Column(Float, nullable=True)
    accuracy_error = Column(Float, nullable=True)  # |predicted - actual|
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReorderSuggestion(Base):
    __tablename__ = "reorder_suggestions"
    __table_args__ = (
        Index("ix_reorder_suggestions_tenant_product_status", "tenant_id", "product_id", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    suggested_quantity = Column(Integer)
    reorder_point = Column(Integer)
    lead_time_days = Column(Integer)
    forecast_demand = Column(Float)
    rationale = Column(Text)  # Why this quantity
    ai_confidence = Column(Float)  # 0-100
    status = Column(String, default="pending")  # "pending", "approved", "ordered", "cancelled"
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)  # Suggestion validity


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    warehouse_name = Column(String)
    warehouse_code = Column(String, unique=True, index=True)
    location_address = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    capacity = Column(Float)
    manager_name = Column(String, nullable=True)
    manager_phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    odoo_warehouse_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StockTransfer(Base):
    __tablename__ = "stock_transfers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    quantity = Column(Integer)
    status = Column(String, default="pending")  # "pending", "in_transit", "received", "cancelled"
    transfer_date = Column(DateTime, default=datetime.utcnow)
    received_date = Column(DateTime, nullable=True)
    received_by = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class InventoryAuditLog(Base):
    __tablename__ = "inventory_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    entity_type = Column(String)  # "product", "location", "warehouse", "movement"
    entity_id = Column(Integer)
    action = Column(String)  # "create", "update", "delete"
    old_values = Column(Text, nullable=True)  # JSON
    new_values = Column(Text, nullable=True)  # JSON
    changed_by = Column(String)
    change_reason = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
