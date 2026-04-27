from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.models.product import Product
from app.models.order import Order
from app.integrations.odoo_products import get_all_products
from app.integrations.odoo_order import get_all_orders
from app.core.logger import request_logger

class SyncService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()

    def sync_products(self) -> dict:
        """Sync products from Odoo to local DB."""
        if not self.tenant or not self.tenant.odoo_url:
            return {"status": "error", "message": "Odoo not configured"}

        odoo_products = get_all_products(
            self.tenant.odoo_url,
            self.tenant.odoo_db,
            self.tenant.odoo_user,
            self.tenant.odoo_password
        )

        if odoo_products is None:
            return {"status": "error", "message": "Odoo authentication failure"}

        synced_count = 0
        for p_data in odoo_products:
            # Check if product exists (by Odoo ID or SKU)
            existing = self.db.query(Product).filter(
                Product.tenant_id == self.tenant_id,
                Product.odoo_id == p_data["odoo_id"]
            ).first()

            if existing:
                existing.name = p_data["name"]
                existing.price = p_data["price"]
                existing.sku = p_data["sku"]
                existing.description = p_data["description"]
            else:
                new_product = Product(
                    tenant_id=self.tenant_id,
                    name=p_data["name"],
                    price=p_data["price"],
                    sku=p_data["sku"],
                    description=p_data["description"],
                    odoo_id=p_data["odoo_id"],
                    quantity=100  # Default initial quantity
                )
                self.db.add(new_product)
            synced_count += 1

        self.db.commit()
        request_logger.info(f"Synced {synced_count} products for tenant {self.tenant_id}")
        return {"status": "success", "count": synced_count}

    def sync_orders(self) -> dict:
        """Sync orders from Odoo to local DB."""
        if not self.tenant or not self.tenant.odoo_url:
            return {"status": "error", "message": "Odoo not configured"}

        odoo_orders = get_all_orders(
            self.tenant.odoo_url,
            self.tenant.odoo_db,
            self.tenant.odoo_user,
            self.tenant.odoo_password
        )

        if odoo_orders is None:
            return {"status": "error", "message": "Odoo authentication failure"}

        synced_count = 0
        for o_data in odoo_orders:
            existing = self.db.query(Order).filter(
                Order.tenant_id == self.tenant_id,
                Order.odoo_id == o_data["id"]
            ).first()

            if not existing:
                new_order = Order(
                    tenant_id=self.tenant_id,
                    customer_mobile="Odoo-Import", # Odoo orders might not have mobile in a standard way
                    product_name=o_data["name"],
                    quantity=1,
                    unit_price=o_data["amount_total"],
                    total_amount=o_data["amount_total"],
                    status=o_data["state"],
                    odoo_id=o_data["id"]
                )
                self.db.add(new_order)
                synced_count += 1

        self.db.commit()
        request_logger.info(f"Synced {synced_count} orders for tenant {self.tenant_id}")
        return {"status": "success", "count": synced_count}
