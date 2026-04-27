import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import SessionLocal
from app.models.tenant import Tenant
from app.models.category import Category
from app.models.brand import Brand
from app.models.unit import Unit
from app.models.attribute import Attribute, AttributeValue
from app.models.product import Product
from app.models.sku import ProductSKU, SKUInventoryMapping
from app.models.inventory import Warehouse, StockLocation
from app.models.customer import Customer
from app.models.procurement import Supplier
from app.models.order import Order
from app.models.season import Season, Collection

def seed():
    print("Starting Comprehensive Garment Retail Seed Data Script...")
    db = SessionLocal()
    tenant_id = 'thread-trend'
    
    try:
        # 1. Clear Existing Data for Tenant
        print(f"Clearing existing data for tenant: {tenant_id}...")
        # Don't delete Tenant, Customers, Suppliers to avoid FK issues with Users/etc.
        # Just delete the core inventory/product data to recreate
        db.query(Order).filter(Order.tenant_id == tenant_id).delete()
        db.query(SKUInventoryMapping).filter(SKUInventoryMapping.tenant_id == tenant_id).delete()
        db.query(StockLocation).filter(StockLocation.tenant_id == tenant_id).delete()
        db.query(Warehouse).filter(Warehouse.tenant_id == tenant_id).delete()
        db.query(ProductSKU).filter(ProductSKU.tenant_id == tenant_id).delete()
        db.query(Product).filter(Product.tenant_id == tenant_id).delete()
        db.query(AttributeValue).filter(AttributeValue.attribute_id.in_(
            db.query(Attribute.id).filter(Attribute.tenant_id == tenant_id)
        )).delete(synchronize_session=False)
        db.query(Attribute).filter(Attribute.tenant_id == tenant_id).delete()
        db.query(Category).filter(Category.tenant_id == tenant_id).delete()
        db.query(Brand).filter(Brand.tenant_id == tenant_id).delete()
        db.query(Unit).filter(Unit.tenant_id == tenant_id).delete()
        db.commit()

        # 2. Create Tenant if not exists
        print("Ensuring Tenant exists...")
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant:
            tenant = Tenant(
                tenant_id=tenant_id,
                business_name="Thread & Trend Garments",
                whatsapp_number="919888777666",
                odoo_url="https://garments.odoo.com",
                odoo_db="garment_prod",
                is_active=True
            )
            db.add(tenant)
            db.flush()

        # 3. Master Data
        print("Creating Master Data (Categories, Brands, Units)...")
        cat_men = Category(tenant_id=tenant_id, name="Men's Wear", description="Apparel for Men")
        cat_women = Category(tenant_id=tenant_id, name="Women's Wear", description="Apparel for Women")
        cat_acc = Category(tenant_id=tenant_id, name="Accessories", description="Bags, Belts, Hats")
        db.add_all([cat_men, cat_women, cat_acc])
        db.flush()

        brand_zara = Brand(tenant_id=tenant_id, name="Zara", description="Fast Fashion")
        brand_levis = Brand(tenant_id=tenant_id, name="Levi's", description="Denim Experts")
        db.add_all([brand_zara, brand_levis])
        db.flush()

        unit_pcs = Unit(tenant_id=tenant_id, name="Pieces", abbreviation="Pcs")
        db.add(unit_pcs)
        db.flush()

        # 4. Attributes & Values
        print("Creating Attributes (Size, Color)...")
        attr_size = Attribute(tenant_id=tenant_id, name="Size", display_type="select")
        attr_color = Attribute(tenant_id=tenant_id, name="Color", display_type="color_picker")
        db.add_all([attr_size, attr_color])
        db.flush()

        sizes = ['S', 'M', 'L', 'XL']
        colors = ['Black', 'White', 'Navy Blue', 'Crimson Red']
        
        size_vals = {}
        for s in sizes:
            av = AttributeValue(attribute_id=attr_size.id, value=s)
            db.add(av)
            size_vals[s] = av
            
        color_vals = {}
        for c in colors:
            av = AttributeValue(attribute_id=attr_color.id, value=c)
            db.add(av)
            color_vals[c] = av
        db.flush()

        # 5. Products & Variants (SKUs)
        print("Creating Products and SKUs...")
        products_data = [
            {"name": "Classic Crewneck T-Shirt", "cat": cat_men.id, "brand": brand_zara.id, "price": 1200, "cost": 400},
            {"name": "Slim Fit Denim Jeans", "cat": cat_men.id, "brand": brand_levis.id, "price": 4500, "cost": 1500},
            {"name": "Summer Floral Dress", "cat": cat_women.id, "brand": brand_zara.id, "price": 3200, "cost": 1000},
            {"name": "Leather Moto Jacket", "cat": cat_women.id, "brand": brand_zara.id, "price": 18500, "cost": 6000}
        ]

        skus_created = []
        for pdata in products_data:
            prod = Product(
                tenant_id=tenant_id,
                name=pdata["name"],
                description=f"Premium {pdata['name']}",
                price=pdata["price"],
                sku=f"TT-{pdata['name'][:3].upper()}-MASTER",
                category_id=pdata["cat"],
                brand_id=pdata["brand"],
                unit_id=unit_pcs.id
            )
            db.add(prod)
            db.flush()

            # Generate variants for each product
            for size in ['S', 'M', 'L']:
                for color in ['Black', 'White']:
                    sku_code = f"TT-{pdata['name'][:3].upper()}-{size}-{color[:3].upper()}"
                    sku = ProductSKU(
                        tenant_id=tenant_id,
                        sku=sku_code,
                        product_name=f"{pdata['name']} - {size} / {color}",
                        product_id=prod.id,
                        category_id=pdata["cat"],
                        brand_id=pdata["brand"],
                        unit_id=unit_pcs.id,
                        cost_price=pdata["cost"],
                        selling_price=pdata["price"],
                        minimum_selling_price=pdata["price"] * 0.8,
                        size=size,
                        color=color,
                        is_active=True
                    )
                    # Associate attribute values
                    sku.attribute_values.extend([size_vals[size], color_vals[color]])
                    db.add(sku)
                    skus_created.append((sku, pdata["price"], pdata["cost"]))
            db.flush()

        # 6. Warehouses & Inventory
        print("Setting up Warehouses and Inventory...")
        wh_main = Warehouse(tenant_id=tenant_id, warehouse_name="Main Distribution Center", warehouse_code="MDC", capacity=50000)
        wh_store = Warehouse(tenant_id=tenant_id, warehouse_name="Downtown Retail Store", warehouse_code="DRS", capacity=5000)
        db.add_all([wh_main, wh_store])
        db.flush()

        loc_tops = StockLocation(tenant_id=tenant_id, warehouse_id=wh_store.id, name="Zone A (Tops)")
        loc_bottoms = StockLocation(tenant_id=tenant_id, warehouse_id=wh_store.id, name="Zone B (Bottoms)")
        db.add_all([loc_tops, loc_bottoms])
        db.flush()

        for sku, price, cost in skus_created:
            qty = random.randint(10, 50)
            mapping = SKUInventoryMapping(
                tenant_id=tenant_id,
                sku=sku.sku,
                warehouse_id=wh_store.id,
                quantity_on_hand=qty,
                quantity_available=qty
            )
            db.add(mapping)
        db.flush()

        # 7. Customers & Suppliers
        print("Creating CRM Customers & Procurement Suppliers...")
        customers = [
            Customer(tenant_id=tenant_id, name="John Doe", mobile="919000000001", email="john@example.com", total_spend=0),
            Customer(tenant_id=tenant_id, name="Jane Smith", mobile="919000000002", email="jane@example.com", total_spend=0),
            Customer(tenant_id=tenant_id, name="Alice Brown", mobile="919000000003", email="alice@example.com", total_spend=0)
        ]
        db.add_all(customers)

        suppliers = [
            Supplier(tenant_id=tenant_id, supplier_name="Global Textiles Ltd.", phone="1800111222", lead_time_days=14),
            Supplier(tenant_id=tenant_id, supplier_name="Denim Works Inc.", phone="1800333444", lead_time_days=21)
        ]
        db.add_all(suppliers)
        db.flush()

        # 8. Orders
        print("Creating sample Orders...")
        for i in range(15):
            customer = random.choice(customers)
            sku, price, cost = random.choice(skus_created)
            qty = random.randint(1, 3)
            
            order = Order(
                tenant_id=tenant_id,
                customer_id=customer.id,
                customer_mobile=customer.mobile,
                sku=sku.sku,
                product_name=sku.product_name,
                quantity=qty,
                unit_price=price,
                total_amount=price * qty,
                status=random.choice(["completed", "completed", "completed", "pending"]),
                payment_status="completed",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10)),
                unit_cost_at_sale=cost
            )
            db.add(order)
            
            if order.status == "completed":
                customer.total_spend += order.total_amount
                
        db.commit()
        print("✅ Comprehensive Seed completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
