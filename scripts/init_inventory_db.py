import os
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models import inventory, procurement
from app.core.logger import request_logger


def init_inventory_db():
    """Initialize inventory database tables."""
    try:
        # Import models to register them
        from app.models.inventory import (
            StockLocation, StockMovement, StockAlert, InventoryNotification,
            DemandForecast, ReorderSuggestion, Warehouse, StockTransfer, InventoryAuditLog
        )
        from app.models.procurement import (
            Supplier, PurchaseOrder, PurchaseOrderLine, SupplierPerformance,
            OrderFulfillment, BackorderAlert, InventoryRule, AutomationWorkflow,
            InventoryCount, CountLine, ProductBarcode
        )
        
        # Create tables
        inventory.Base.metadata.create_all(bind=engine)
        procurement.Base.metadata.create_all(bind=engine)
        
        request_logger.info("Inventory and procurement tables created successfully")
        return True
    
    except Exception as e:
        request_logger.error(f"Error initializing inventory DB: {str(e)}")
        return False


def seed_sample_data():
    """Seed sample inventory data for testing."""
    db = SessionLocal()
    try:
        from app.models.tenant import Tenant
        from app.models.product import Product
        from app.models.inventory import StockLocation, Warehouse
        from app.models.procurement import Supplier
        
        # Get first tenant
        tenant = db.query(Tenant).first()
        if not tenant:
            request_logger.warning("No tenant found for seeding")
            return False
        
        # Create sample warehouse
        warehouse = Warehouse(
            tenant_id=tenant.tenant_id,
            warehouse_name="Main Warehouse",
            warehouse_code="WH-001",
            location_address="123 Business Street",
            capacity=10000,
            manager_name="Warehouse Manager"
        )
        db.add(warehouse)
        db.commit()
        
        # Create sample suppliers
        suppliers_data = [
            {
                "supplier_name": "Fabric Supplier Inc",
                "phone": "9876543210",
                "whatsapp_number": "919876543210",
                "email": "supplier1@example.com",
                "lead_time_days": 7
            },
            {
                "supplier_name": "Accessories Co",
                "phone": "9876543211",
                "whatsapp_number": "919876543211",
                "email": "supplier2@example.com",
                "lead_time_days": 5
            }
        ]
        
        for sup_data in suppliers_data:
            supplier = Supplier(
                tenant_id=tenant.tenant_id,
                **sup_data,
                is_active=True
            )
            db.add(supplier)
        
        db.commit()
        
        # Create stock locations for existing products
        products = db.query(Product).filter(Product.tenant_id == tenant.tenant_id).limit(10).all()
        
        for product in products:
            location = StockLocation(
                tenant_id=tenant.tenant_id,
                product_id=product.id,
                warehouse_id=warehouse.id,
                zone_name="A1",
                quantity=50,
                reserved_quantity=0,
                available_quantity=50,
                reorder_point=10,
                reorder_quantity=50
            )
            db.add(location)
        
        db.commit()
        request_logger.info(f"Seeded sample data for tenant {tenant.tenant_id}")
        return True
    
    except Exception as e:
        request_logger.error(f"Error seeding data: {str(e)}")
        db.rollback()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    init_inventory_db()
    seed_sample_data()
    print("Inventory database initialized!")
