#!/usr/bin/env python3
"""
SKU System Migration Script
Initializes SKU tables and migrates existing products to SKU-based system
"""

import sys
import os
sys.path.insert(0, '/Users/vikram/workspace/odoo-saas')

# Handle localhost connection
os.environ['POSTGRES_URL'] = os.environ.get('POSTGRES_URL', 'postgresql://postgres:ViKram#2026@postgres-app:5432/app_db?options=-csearch_path%3Dodoo_saas_retail_db')

from app.core.database import engine, SessionLocal
from app.models.sku import (
    ProductSKU, SKUBarcode, SKUInventoryMapping,
    SKUMovementLog, SKUAlertRule, SKUPlatformMapping
)
from app.models.product import Product
from app.models.inventory import StockLocation, StockMovement, StockAlert
from app.core.logger import get_logger
from datetime import datetime
import json

logger = get_logger(__name__)


def create_sku_tables():
    """Create all SKU-related tables"""
    try:
        logger.info("Creating SKU tables...")
        
        # Create tables with checkfirst=True to avoid errors
        # Drop existing if needed (for clean re-runs)
        try:
            ProductSKU.__table__.drop(engine, checkfirst=True)
            SKUBarcode.__table__.drop(engine, checkfirst=True)
            SKUInventoryMapping.__table__.drop(engine, checkfirst=True)
            SKUMovementLog.__table__.drop(engine, checkfirst=True)
            SKUAlertRule.__table__.drop(engine, checkfirst=True)
            SKUPlatformMapping.__table__.drop(engine, checkfirst=True)
            logger.info("Dropped existing SKU tables")
        except:
            pass  # Tables don't exist yet
        
        # Create in correct order
        ProductSKU.__table__.create(engine, checkfirst=True)
        logger.info("  ✓ Created product_skus")
        SKUBarcode.__table__.create(engine, checkfirst=True)
        logger.info("  ✓ Created sku_barcodes")
        SKUInventoryMapping.__table__.create(engine, checkfirst=True)
        logger.info("  ✓ Created sku_inventory_mappings")
        SKUMovementLog.__table__.create(engine, checkfirst=True)
        logger.info("  ✓ Created sku_movement_logs")
        SKUAlertRule.__table__.create(engine, checkfirst=True)
        logger.info("  ✓ Created sku_alert_rules")
        SKUPlatformMapping.__table__.create(engine, checkfirst=True)
        logger.info("  ✓ Created sku_platform_mappings")
        
        logger.info("✓ SKU tables created successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Error creating SKU tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def migrate_products_to_sku():
    """
    Migrate existing products to SKU-based system
    Maps old product_id references to new SKU references
    """
    try:
        logger.info("Migrating products to SKU system...")
        db = SessionLocal()
        
        # 1. Migrate actual products from database
        db_products = db.query(Product).all()
        created_count = 0
        
        for prod in db_products:
            # Check if SKU already exists for this product
            existing = db.query(ProductSKU).filter(
                ProductSKU.sku == prod.sku
            ).first()
            
            if not existing:
                product_sku = ProductSKU(
                    tenant_id=prod.tenant_id,
                    sku=prod.sku,
                    product_name=prod.name,
                    description=prod.description,
                    product_id=prod.id,
                    selling_price=prod.price,
                    cost_price=prod.price * 0.7, # Default estimate
                    reorder_point=prod.quantity // 10 if prod.quantity else 10,
                    reorder_quantity=prod.quantity // 2 if prod.quantity else 50,
                    lead_time_days=7,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(product_sku)
                created_count += 1
        
        db.commit()
        logger.info(f"✓ Migrated {created_count} database products to SKU system")
        
        # 2. Add sample SKUs for demonstration if they don't exist
        sample_skus = [
            {
                'sku': 'SHIRT-BLUE-001',
                'product_name': 'Blue T-Shirt',
                'category': 'Apparel',
                'cost_price': 150.0,
                'selling_price': 299.0,
                'reorder_point': 20,
                'reorder_quantity': 100,
                'lead_time_days': 7
            },
            {
                'sku': 'SHIRT-RED-001',
                'product_name': 'Red T-Shirt',
                'category': 'Apparel',
                'cost_price': 150.0,
                'selling_price': 299.0,
                'reorder_point': 20,
                'reorder_quantity': 100,
                'lead_time_days': 7
            },
            {
                'sku': 'PANTS-BLACK-001',
                'product_name': 'Black Jeans',
                'category': 'Apparel',
                'cost_price': 400.0,
                'selling_price': 899.0,
                'reorder_point': 15,
                'reorder_quantity': 50,
                'lead_time_days': 5
            },
            {
                'sku': 'HAT-BASEBALL-001',
                'product_name': 'Baseball Cap',
                'category': 'Accessories',
                'cost_price': 100.0,
                'selling_price': 199.0,
                'reorder_point': 30,
                'reorder_quantity': 200,
                'lead_time_days': 10
            },
            {
                'sku': 'SHOE-RUNNING-001',
                'product_name': 'Running Shoes',
                'category': 'Footwear',
                'cost_price': 2000.0,
                'selling_price': 4999.0,
                'reorder_point': 10,
                'reorder_quantity': 50,
                'lead_time_days': 14
            }
        ]
        
        created_count = 0
        for sku_data in sample_skus:
            # Check if SKU already exists
            existing = db.query(ProductSKU).filter(
                ProductSKU.sku == sku_data['sku']
            ).first()
            
            if not existing:
                product_sku = ProductSKU(
                    tenant_id='default',  # Default tenant
                    **sku_data,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(product_sku)
                created_count += 1
        
        db.commit()
        logger.info(f"✓ Migrated {created_count} products to SKU system")
        
        # Create sample barcodes
        create_sample_barcodes(db)
        
        db.close()
        return True
    except Exception as e:
        logger.error(f"✗ Error migrating products: {str(e)}")
        db.rollback()
        return False


def create_sample_barcodes(db):
    """Create sample barcodes for SKUs"""
    try:
        sample_barcodes = [
            {'sku': 'SHIRT-BLUE-001', 'barcode': '1234567890001', 'barcode_type': 'EAN-13', 'is_primary': True},
            {'sku': 'SHIRT-BLUE-001', 'barcode': '0001234567890', 'barcode_type': 'UPC-A', 'is_primary': False},
            {'sku': 'SHIRT-RED-001', 'barcode': '1234567890002', 'barcode_type': 'EAN-13', 'is_primary': True},
            {'sku': 'PANTS-BLACK-001', 'barcode': '1234567890003', 'barcode_type': 'EAN-13', 'is_primary': True},
            {'sku': 'HAT-BASEBALL-001', 'barcode': '1234567890004', 'barcode_type': 'EAN-13', 'is_primary': True},
            {'sku': 'SHOE-RUNNING-001', 'barcode': '1234567890005', 'barcode_type': 'EAN-13', 'is_primary': True},
        ]
        
        created_count = 0
        for bc_data in sample_barcodes:
            existing = db.query(SKUBarcode).filter(
                SKUBarcode.barcode == bc_data['barcode']
            ).first()
            
            if not existing:
                barcode = SKUBarcode(
                    tenant_id='default',
                    sku=bc_data['sku'],
                    barcode=bc_data['barcode'],
                    barcode_type=bc_data['barcode_type'],
                    barcode_format='linear' if bc_data['barcode_type'] != 'QR' else '2d',
                    is_primary=bc_data['is_primary'],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(barcode)
                created_count += 1
        
        db.commit()
        logger.info(f"✓ Created {created_count} sample barcodes")
    except Exception as e:
        logger.error(f"✗ Error creating barcodes: {str(e)}")
        db.rollback()


def create_sample_inventory_mappings(db):
    """Create sample inventory mappings to SKU"""
    try:
        logger.info("Creating sample inventory mappings...")
        
        sample_mappings = [
            {'sku': 'SHIRT-BLUE-001', 'warehouse_id': 1, 'zone_name': 'A', 'bin_number': 'A1', 'quantity_on_hand': 50, 'quantity_reserved': 10},
            {'sku': 'SHIRT-RED-001', 'warehouse_id': 1, 'zone_name': 'A', 'bin_number': 'A2', 'quantity_on_hand': 35, 'quantity_reserved': 5},
            {'sku': 'PANTS-BLACK-001', 'warehouse_id': 1, 'zone_name': 'B', 'bin_number': 'B1', 'quantity_on_hand': 25, 'quantity_reserved': 3},
            {'sku': 'HAT-BASEBALL-001', 'warehouse_id': 2, 'zone_name': 'C', 'bin_number': 'C1', 'quantity_on_hand': 150, 'quantity_reserved': 20},
            {'sku': 'SHOE-RUNNING-001', 'warehouse_id': 2, 'zone_name': 'D', 'bin_number': 'D1', 'quantity_on_hand': 30, 'quantity_reserved': 5},
        ]
        
        created_count = 0
        for mapping_data in sample_mappings:
            mapping_data['quantity_available'] = mapping_data['quantity_on_hand'] - mapping_data['quantity_reserved']
            
            existing = db.query(SKUInventoryMapping).filter(
                SKUInventoryMapping.sku == mapping_data['sku'],
                SKUInventoryMapping.warehouse_id == mapping_data['warehouse_id']
            ).first()
            
            if not existing:
                mapping = SKUInventoryMapping(
                    tenant_id='default',
                    **mapping_data,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(mapping)
                created_count += 1
        
        db.commit()
        logger.info(f"✓ Created {created_count} inventory mappings")
    except Exception as e:
        logger.error(f"✗ Error creating inventory mappings: {str(e)}")
        db.rollback()


def create_sample_platform_mappings(db):
    """Create sample platform mappings for multi-channel sync"""
    try:
        logger.info("Creating sample platform mappings...")
        
        sample_mappings = [
            {
                'sku': 'SHIRT-BLUE-001',
                'platform_name': 'odoo',
                'platform_product_id': '1001',
                'platform_stock_level': 50
            },
            {
                'sku': 'SHIRT-BLUE-001',
                'platform_name': 'shopify',
                'platform_product_id': 'gid://shopify/Product/5678',
                'platform_stock_level': 15
            },
            {
                'sku': 'SHIRT-BLUE-001',
                'platform_name': 'woocommerce',
                'platform_product_id': '2001',
                'platform_stock_level': 20
            },
            {
                'sku': 'PANTS-BLACK-001',
                'platform_name': 'amazon',
                'platform_product_id': 'B0ABC123DE',
                'platform_stock_level': 25
            },
        ]
        
        created_count = 0
        for mapping_data in sample_mappings:
            existing = db.query(SKUPlatformMapping).filter(
                SKUPlatformMapping.sku == mapping_data['sku'],
                SKUPlatformMapping.platform_name == mapping_data['platform_name']
            ).first()
            
            if not existing:
                mapping = SKUPlatformMapping(
                    tenant_id='default',
                    **mapping_data,
                    sync_status='pending',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(mapping)
                created_count += 1
        
        db.commit()
        logger.info(f"✓ Created {created_count} platform mappings")
    except Exception as e:
        logger.error(f"✗ Error creating platform mappings: {str(e)}")
        db.rollback()


def main():
    """Run SKU migration"""
    print("=" * 60)
    print("SKU SYSTEM MIGRATION")
    print("=" * 60)
    print()
    
    # Step 1: Create tables
    if not create_sku_tables():
        print("Migration failed at table creation")
        return False
    
    print()
    
    # Step 2: Migrate products
    if not migrate_products_to_sku():
        print("Migration failed at product migration")
        return False
    
    print()
    
    # Step 3: Create sample data
    db = SessionLocal()
    try:
        create_sample_inventory_mappings(db)
        print()
        create_sample_platform_mappings(db)
        print()
        logger.info("✓ SKU migration completed successfully!")
        print()
        print("=" * 60)
        print("SKU SYSTEM READY")
        print("=" * 60)
        print()
        print("New endpoints available:")
        print("  GET  /sku/lookup/{sku}")
        print("  GET  /sku/lookup/barcode/{barcode}")
        print("  GET  /sku/lookup/odoo/{odoo_id}")
        print("  GET  /sku/detail/{sku}")
        print("  GET  /sku/{sku}/barcodes")
        print("  GET  /sku/{sku}/platforms")
        print("  GET  /sku/search?q=<query>")
        print("  GET  /sku/low-stock/list")
        print()
        return True
    except Exception as e:
        logger.error(f"✗ Error in migration: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
