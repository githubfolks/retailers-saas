from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from datetime import datetime
from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    supplier_name = Column(String, index=True)
    contact_person = Column(String, nullable=True)
    phone = Column(String)
    whatsapp_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    lead_time_days = Column(Integer, default=7)
    reliability_score = Column(Float, default=0.0)  # 0-100
    payment_terms = Column(String, nullable=True)  # Net 30, COD, etc.
    is_preferred = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    po_number = Column(String, unique=True, index=True)
    po_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery = Column(DateTime)
    actual_delivery = Column(DateTime, nullable=True)
    po_status = Column(String, default="draft")  # draft, sent, confirmed, shipped, received, cancelled
    total_amount = Column(Float, default=0.0)
    payment_status = Column(String, default="pending")  # pending, partial, paid
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    product_id = Column(Integer, nullable=True)
    product_name = Column(String)
    quantity = Column(Integer)
    unit_cost = Column(Float)
    total_cost = Column(Float)
    received_quantity = Column(Integer, default=0)
    received_date = Column(DateTime, nullable=True)
    quality_status = Column(String, default="pending")  # pending, accepted, rejected, partial


class SupplierPerformance(Base):
    __tablename__ = "supplier_performance"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    on_time_delivery_rate = Column(Float, default=0.0)  # Percentage
    quality_score = Column(Float, default=0.0)  # 0-100
    lead_time_average = Column(Integer, default=0)  # Days
    defect_rate = Column(Float, default=0.0)  # Percentage
    last_evaluated = Column(DateTime)
    evaluation_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrderFulfillment(Base):
    __tablename__ = "order_fulfillments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    order_id = Column(Integer, index=True)  # Reference to Order
    fulfillment_status = Column(String, default="pending")  # pending, picking, packed, shipped, delivered, failed
    warehouse_id = Column(Integer, nullable=True)
    picker_id = Column(String, nullable=True)
    packing_time = Column(DateTime, nullable=True)
    carrier = Column(String, nullable=True)  # Courier name
    tracking_number = Column(String, nullable=True, index=True)
    estimated_delivery = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)
    proof_of_delivery = Column(String, nullable=True)  # URL to image
    delivery_signature = Column(String, nullable=True)  # Base64 or URL
    delivery_notes = Column(Text, nullable=True)
    
    batch_id = Column(Integer, ForeignKey("picking_batches.id"), nullable=True)
    fulfillment_method = Column(String(50), default="standard") # standard, dropship
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PickingBatch(Base):
    """Groups multiple fulfillments for bulk operations"""
    __tablename__ = "picking_batches"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    
    batch_name = Column(String(100))
    status = Column(String(50), default="draft") # draft, in_progress, packed, shipped
    
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    picker_id = Column(String, nullable=True) # User ID assigned to pick this batch
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BackorderAlert(Base):
    __tablename__ = "backorder_alerts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    order_id = Column(Integer, index=True)
    product_id = Column(Integer)
    quantity_short = Column(Integer)
    expected_restock_date = Column(DateTime)
    customer_notification_sent = Column(Boolean, default=False)
    customer_notification_channel = Column(String, default="whatsapp")  # whatsapp, sms, email
    last_notification_at = Column(DateTime, nullable=True)
    backorder_status = Column(String, default="active")  # active, fulfilled, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)


class InventoryRule(Base):
    __tablename__ = "inventory_rules"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    rule_name = Column(String)
    rule_description = Column(Text, nullable=True)
    condition = Column(Text)  # Condition logic as string (will be evaluated)
    action = Column(Text)  # Action to perform
    rule_priority = Column(Integer, default=0)  # Higher = executed first
    is_enabled = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AutomationWorkflow(Base):
    __tablename__ = "automation_workflows"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    workflow_name = Column(String)
    workflow_description = Column(Text, nullable=True)
    trigger_type = Column(String)  # "low_stock", "auto_discount", "out_of_stock", "seasonal"
    trigger_condition = Column(Text)
    steps = Column(Text)  # JSON array of workflow steps
    notification_channels = Column(Text)  # JSON array: ["whatsapp", "email"]
    is_active = Column(Boolean, default=True)
    execution_count = Column(Integer, default=0)
    last_executed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SupplierEmailSettings(Base):
    """Per-tenant configuration for automated supplier email notifications."""
    __tablename__ = "supplier_email_settings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), unique=True, index=True)
    is_enabled = Column(Boolean, default=True)
    cooldown_hours = Column(Integer, default=24)  # Min hours between emails to same supplier/product
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InventoryCount(Base):
    __tablename__ = "inventory_counts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    count_date = Column(DateTime, default=datetime.utcnow)
    count_by_user = Column(String)
    status = Column(String, default="in_progress")  # in_progress, completed, verified
    warehouse_id = Column(Integer, nullable=True)
    total_items_counted = Column(Integer, default=0)
    total_discrepancies = Column(Integer, default=0)
    variance_percentage = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class CountLine(Base):
    __tablename__ = "count_lines"

    id = Column(Integer, primary_key=True, index=True)
    count_id = Column(Integer, ForeignKey("inventory_counts.id"))
    product_id = Column(Integer)
    barcode = Column(String, nullable=True)
    counted_qty = Column(Integer)
    system_qty = Column(Integer)
    variance = Column(Integer)  # Signed difference
    variance_reason = Column(String, nullable=True)  # "damage", "loss", "data_error", etc.


class ProductBarcode(Base):
    __tablename__ = "product_barcodes"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    barcode = Column(String, unique=True, index=True)
    barcode_type = Column(String)  # EAN-13, UPC, QR, CODE128
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class LogisticsPartner(Base):
    __tablename__ = "logistics_partners"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    name = Column(String, index=True)
    provider_type = Column(String, default="manual")  # manual | shiprocket | delhivery
    api_email = Column(String, nullable=True)
    api_password = Column(String, nullable=True)
    pickup_location_name = Column(String, nullable=True)  # Shiprocket pickup location label
    tracking_url_template = Column(String, nullable=True)  # e.g. https://courier.com/track/{awb}
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
