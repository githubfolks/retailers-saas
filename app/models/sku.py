from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.attribute import AttributeValue
    from app.models.brand import Brand
    from app.models.unit import Unit


class ProductSKU(Base):
    """
    Master product catalog with SKU as primary identifier
    Enables cross-platform inventory management
    """
    __tablename__ = "product_skus"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)  # tenant_id for filtering, not FK
    
    # SKU as universal identifier
    sku = Column(String(255), unique=True, index=True)  # e.g., "SHIRT-BLUE-001"
    sku_type = Column(String(50), default="internal")  # internal, supplier, customer
    
    # Product metadata
    product_name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    sub_category = Column(String(100), nullable=True)
    
    # Template Link
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    
    # FKs
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True)
    
    # Pricing
    cost_price = Column(Float, nullable=True)  # Actual cost
    selling_price = Column(Float, nullable=True)  # Standard selling price
    minimum_selling_price = Column(Float, nullable=True)  # Discount limit
    seasonal_price = Column(Float, nullable=True) # Override for season sales
    seasonal_discount_pct = Column(Float, default=0.0)
    
    # Inventory parameters
    reorder_point = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=50)
    max_stock_level = Column(Integer, nullable=True)
    lead_time_days = Column(Integer, default=7)
    
    # Platform mappings (for multi-channel sync)
    odoo_product_id = Column(Integer, unique=True, nullable=True, index=True)  # Odoo reference
    shopify_product_id = Column(String(255), nullable=True, index=True)  # Shopify reference
    woocommerce_product_id = Column(Integer, nullable=True, index=True)  # WooCommerce reference
    amazon_asin = Column(String(255), nullable=True, index=True)  # Amazon ASIN
    ebay_item_id = Column(String(255), nullable=True, index=True)  # eBay item ID
    external_sku = Column(String(255), nullable=True)  # Supplier's SKU
    
    # Status and tracking
    is_active = Column(Boolean, default=True, index=True)
    is_discontinued = Column(Boolean, default=False)
    weight = Column(Float, nullable=True)  # kg
    dimensions = Column(String(255), nullable=True)  # L x W x H
    color = Column(String(100), nullable=True)
    size = Column(String(100), nullable=True)
    
    # Relationship to dynamic attributes
    from app.models.attribute import sku_attribute_link
    attribute_values = relationship("AttributeValue", secondary=sku_attribute_link, back_populates="skus")
    
    # Relationships
    category_rel = relationship("Category", back_populates="skus")
    brand_rel = relationship("Brand", back_populates="skus")
    unit_rel = relationship("Unit", back_populates="skus")
    product_template = relationship("Product", back_populates="variants")
    season_rel = relationship("Season", backref="skus")
    collection_rel = relationship("Collection", backref="skus")
    inventory_mappings = relationship("SKUInventoryMapping", primaryjoin="ProductSKU.sku == foreign(SKUInventoryMapping.sku)", backref="product_sku_rel")
    
    @property
    def quantity(self):
        """Aggregate quantity across all locations."""
        try:
            return sum(m.quantity_available for m in (self.inventory_mappings or []))
        except (AttributeError, TypeError):
            return 0

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    sync_status = Column(String, default="pending")  # pending, synced, failed

    # GST / Compliance
    hsn_code = Column(String(10), default="6105", nullable=True)  # e.g., 6105 = Men's shirts


class SKUBarcode(Base):
    """
    Barcode/QR code mappings to SKU
    One SKU can have multiple barcodes (primary + alternate codes)
    Complements existing ProductBarcode which links to product_id
    """
    __tablename__ = "sku_barcodes"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)  # tenant_id for filtering, not FK
    
    # Link to product by SKU (not product_id)
    sku = Column(String(255), ForeignKey("product_skus.sku"), index=True)
    
    # Barcode details
    barcode = Column(String(255), unique=True, index=True)  # Unique barcode string
    barcode_type = Column(String(50))  # EAN-13, UPC-A, CODE128, QR, DATAMATRIX
    barcode_format = Column(String(50), default="linear")  # linear, 2d, qr
    
    # Primary vs alternate
    is_primary = Column(Boolean, default=False, index=True)  # Primary barcode
    is_active = Column(Boolean, default=True)
    
    # Additional info
    barcode_source = Column(String(50), nullable=True)  # manufacturer, supplier, custom
    supplier_reference = Column(String(255), nullable=True)  # Supplier's barcode reference
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    scanned_count = Column(Integer, default=0)  # Track scan frequency
    last_scanned = Column(DateTime, nullable=True)


class SKUInventoryMapping(Base):
    """
    Maps SKU to inventory locations
    Replaces direct product_id references with SKU
    """
    __tablename__ = "sku_inventory_mappings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)  # tenant_id for filtering, not FK
    
    # SKU and location
    sku = Column(String(255), ForeignKey("product_skus.sku"), index=True)
    warehouse_id = Column(Integer, nullable=True)  # Warehouse/location
    zone_name = Column(String(50), nullable=True)  # Zone within warehouse
    bin_number = Column(String(50), nullable=True)  # Specific bin
    
    # Stock quantities
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    quantity_available = Column(Integer, default=0)
    quantity_damaged = Column(Integer, default=0)
    
    # Tracking
    last_counted = Column(DateTime, nullable=True)
    last_movement = Column(DateTime, nullable=True)
    movement_count = Column(Integer, default=0)  # Number of movements
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SKUMovementLog(Base):
    """
    Complete audit trail for SKU movements
    Links stock movements to SKU (not product_id)
    """
    __tablename__ = "sku_movement_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)  # tenant_id for filtering, not FK
    
    # Movement details
    sku = Column(String(255), ForeignKey("product_skus.sku"), index=True)
    movement_type = Column(String(50))  # in, out, transfer, adjustment, return
    quantity = Column(Integer)  # Positive for IN, negative for OUT
    
    # Reference information
    reference_type = Column(String(50), nullable=True)  # order, po, transfer, adjustment
    reference_id = Column(String(255), nullable=True)  # Order ID, PO ID, etc
    
    # Location details
    from_warehouse_id = Column(Integer, nullable=True)
    from_zone = Column(String(50), nullable=True)
    from_bin = Column(String(50), nullable=True)
    
    to_warehouse_id = Column(Integer, nullable=True)
    to_zone = Column(String(50), nullable=True)
    to_bin = Column(String(50), nullable=True)
    
    # Business context
    reason = Column(String(100), nullable=True)  # purchase, sale, damage, loss, transfer, return
    platform_source = Column(String(50), nullable=True)  # odoo, shopify, woocommerce, amazon
    
    # Audit
    created_by = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SKUAlertRule(Base):
    """
    Alert rules based on SKU
    Replaces direct product_id references
    """
    __tablename__ = "sku_alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)  # tenant_id for filtering, not FK
    
    # SKU-specific rule
    sku = Column(String(255), ForeignKey("product_skus.sku"), index=True)
    
    # Alert configuration
    alert_type = Column(String(50))  # low_stock, out_of_stock, overstock, slow_moving
    trigger_threshold = Column(Integer)  # Alert triggers at this level
    alert_level = Column(String(20), default="warning")  # info, warning, critical
    
    # Notification
    notify_channels = Column(String(255))  # whatsapp,sms,email (comma separated)
    notify_recipients = Column(String(500))  # Contact info (comma separated)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SKUPlatformMapping(Base):
    """
    Maps single SKU to multiple platform product IDs
    Essential for multi-channel inventory sync
    """
    __tablename__ = "sku_platform_mappings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)  # tenant_id for filtering, not FK
    
    # SKU is the source of truth
    sku = Column(String(255), ForeignKey("product_skus.sku"), index=True)
    
    # Platform-specific IDs
    platform_name = Column(String(50), index=True)  # odoo, shopify, woocommerce, amazon, ebay, etc
    platform_product_id = Column(String(255), index=True)  # Platform's product identifier
    platform_variant_id = Column(String(255), nullable=True)  # For platforms with variants
    
    # Sync tracking
    last_synced = Column(DateTime, nullable=True)
    sync_status = Column(String(50), default="pending")  # pending, synced, failed
    sync_errors = Column(Text, nullable=True)  # Error details if failed
    
    # Stock quantities on platform (cached)
    platform_stock_level = Column(Integer, default=0)
    platform_reserved = Column(Integer, default=0)
    platform_available = Column(Integer, default=0)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint: unique per platform per SKU
    __table_args__ = (
        __import__('sqlalchemy').UniqueConstraint('sku', 'platform_name', 'platform_product_id', 
                                                   name='_sku_platform_unique'),
    )
