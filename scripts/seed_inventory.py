import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import SessionLocal
from app.models.tenant import Tenant
from app.models.product import Product
from app.models.inventory import Warehouse, StockLocation
from app.models.sku import ProductSKU, SKUInventoryMapping

def seed_inventory():
    print("Seeding inventory data (Warehouses & Locations) for all tenants...")
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        for tenant in tenants:
            # 1. Create Main Warehouse for tenant
            warehouse = db.query(Warehouse).filter(Warehouse.tenant_id == tenant.tenant_id).first()
            if not warehouse:
                print(f"Creating warehouse for {tenant.tenant_id}")
                warehouse = Warehouse(
                    tenant_id=tenant.tenant_id,
                    warehouse_name="Main Warehouse",
                    warehouse_code=f"WH-{tenant.tenant_id[:4].upper()}",
                    capacity=10000,
                    is_active=True
                )
                db.add(warehouse)
                db.flush() # Get ID
            
            # 2. Create Stock Locations for all products of this tenant
            products = db.query(Product).filter(Product.tenant_id == tenant.tenant_id).all()
            for prod in products:
                # Check if location exists
                loc = db.query(StockLocation).filter(
                    StockLocation.tenant_id == tenant.tenant_id,
                    StockLocation.product_id == prod.id
                ).first()
                
                if not loc:
                    print(f"  Creating location for product {prod.sku}")
                    loc = StockLocation(
                        tenant_id=tenant.tenant_id,
                        product_id=prod.id,
                        warehouse_id=warehouse.id,
                        name=f"Shelf-{prod.sku[-2:]}",
                        quantity=prod.quantity or 100,
                        available_quantity=prod.quantity or 100
                    )
                    db.add(loc)
                    db.flush()
                
                # 3. Create SKU Inventory Mapping
                sku_mapping = db.query(SKUInventoryMapping).filter(
                    SKUInventoryMapping.sku == prod.sku,
                    SKUInventoryMapping.warehouse_id == warehouse.id
                ).first()
                
                if not sku_mapping:
                    print(f"  Mapping SKU {prod.sku} to warehouse")
                    sku_mapping = SKUInventoryMapping(
                        tenant_id=tenant.tenant_id,
                        sku=prod.sku,
                        warehouse_id=warehouse.id,
                        quantity_on_hand=prod.quantity or 100,
                        quantity_available=prod.quantity or 100
                    )
                    db.add(sku_mapping)
        
        db.commit()
        print("✅ Inventory seeding completed!")
    except Exception as e:
        print(f"❌ Error seeding inventory: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_inventory()
