#!/usr/bin/env python
"""
Database migration script for inventory management system.
Run this after deploying the new inventory models.
"""

import sys
from sqlalchemy import inspect
from app.core.database import engine, SessionLocal
from app.models.inventory import (
    StockLocation, StockMovement, StockAlert, InventoryNotification,
    DemandForecast, ReorderSuggestion, Warehouse, StockTransfer, InventoryAuditLog
)
from app.models.procurement import (
    Supplier, PurchaseOrder, PurchaseOrderLine, SupplierPerformance,
    OrderFulfillment, BackorderAlert, InventoryRule, AutomationWorkflow,
    InventoryCount, CountLine, ProductBarcode
)
from app.core.logger import request_logger


def check_table_exists(table_name: str) -> bool:
    """Check if table exists in database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate_inventory_tables():
    """Create all inventory tables if they don't exist."""
    tables = [
        ('stock_locations', StockLocation),
        ('stock_movements', StockMovement),
        ('stock_alerts', StockAlert),
        ('inventory_notifications', InventoryNotification),
        ('demand_forecasts', DemandForecast),
        ('reorder_suggestions', ReorderSuggestion),
        ('warehouses', Warehouse),
        ('stock_transfers', StockTransfer),
        ('inventory_audit_logs', InventoryAuditLog),
    ]
    
    created = []
    for table_name, model in tables:
        if not check_table_exists(table_name):
            model.__table__.create(engine)
            created.append(table_name)
            print(f"✓ Created table: {table_name}")
        else:
            print(f"✓ Table exists: {table_name}")
    
    return created


def migrate_procurement_tables():
    """Create all procurement tables if they don't exist."""
    tables = [
        ('suppliers', Supplier),
        ('purchase_orders', PurchaseOrder),
        ('purchase_order_lines', PurchaseOrderLine),
        ('supplier_performance', SupplierPerformance),
        ('order_fulfillments', OrderFulfillment),
        ('backorder_alerts', BackorderAlert),
        ('inventory_rules', InventoryRule),
        ('automation_workflows', AutomationWorkflow),
        ('inventory_counts', InventoryCount),
        ('count_lines', CountLine),
        ('product_barcodes', ProductBarcode),
    ]
    
    created = []
    for table_name, model in tables:
        if not check_table_exists(table_name):
            model.__table__.create(engine)
            created.append(table_name)
            print(f"✓ Created table: {table_name}")
        else:
            print(f"✓ Table exists: {table_name}")
    
    return created


def migrate_stock_locations_from_products():
    """Initialize stock_locations from existing products."""
    from app.models.product import Product
    from app.models.tenant import Tenant
    
    db = SessionLocal()
    try:
        # Check if stock_locations already has data
        existing = db.query(StockLocation).count()
        if existing > 0:
            print(f"⚠️  Stock locations already populated ({existing} records)")
            return 0
        
        products = db.query(Product).all()
        if not products:
            print("⚠️  No products found to seed")
            return 0
        
        created = 0
        for product in products:
            location = StockLocation(
                tenant_id=product.tenant_id,
                product_id=product.id,
                quantity=product.quantity,
                reserved_quantity=0,
                available_quantity=product.quantity,
                reorder_point=10,
                reorder_quantity=50
            )
            db.add(location)
            created += 1
        
        db.commit()
        print(f"✓ Seeded {created} stock locations from products")
        return created
    
    except Exception as e:
        print(f"✗ Error seeding stock locations: {str(e)}")
        db.rollback()
        return 0
    
    finally:
        db.close()


def migrate_create_indexes():
    """Create performance indexes."""
    from sqlalchemy import text
    
    db = SessionLocal()
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_stock_location_product ON stock_locations(product_id, tenant_id);",
        "CREATE INDEX IF NOT EXISTS idx_stock_movement_product ON stock_movements(product_id, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_stock_movement_tenant ON stock_movements(tenant_id, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_stock_alert_product ON stock_alerts(product_id, status);",
        "CREATE INDEX IF NOT EXISTS idx_stock_alert_tenant ON stock_alerts(tenant_id, status);",
        "CREATE INDEX IF NOT EXISTS idx_demand_forecast_product ON demand_forecasts(product_id, forecast_date);",
        "CREATE INDEX IF NOT EXISTS idx_po_supplier ON purchase_orders(supplier_id, po_status);",
        "CREATE INDEX IF NOT EXISTS idx_fulfillment_order ON order_fulfillments(order_id, fulfillment_status);",
        "CREATE INDEX IF NOT EXISTS idx_fulfillment_tenant ON order_fulfillments(tenant_id);",
        "CREATE INDEX IF NOT EXISTS idx_barcode_product ON product_barcodes(barcode, product_id);",
        "CREATE INDEX IF NOT EXISTS idx_barcode_tenant ON product_barcodes(tenant_id);",
        "CREATE INDEX IF NOT EXISTS idx_backorder_order ON backorder_alerts(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_supplier_tenant ON suppliers(tenant_id, is_active);",
    ]
    
    try:
        for idx_sql in indexes:
            db.execute(text(idx_sql))
        db.commit()
        print(f"✓ Created {len(indexes)} performance indexes")
    
    except Exception as e:
        print(f"✗ Error creating indexes: {str(e)}")
        db.rollback()
    
    finally:
        db.close()


def run_migration():
    """Run complete migration."""
    print("=" * 60)
    print("INVENTORY MANAGEMENT SYSTEM - DATABASE MIGRATION")
    print("=" * 60)
    
    print("\n1. Creating Inventory Tables...")
    inv_created = migrate_inventory_tables()
    
    print("\n2. Creating Procurement Tables...")
    proc_created = migrate_procurement_tables()
    
    print("\n3. Seeding Stock Locations from Products...")
    seeded = migrate_stock_locations_from_products()
    
    print("\n4. Creating Performance Indexes...")
    migrate_create_indexes()
    
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Inventory tables created: {len(inv_created)}")
    print(f"Procurement tables created: {len(proc_created)}")
    print(f"Stock locations seeded: {seeded}")
    print("\n✓ Migration completed successfully!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
