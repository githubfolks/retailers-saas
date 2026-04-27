from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from app.models.season import Season, Collection
from app.models.product import Product
from app.models.sku import ProductSKU
from app.models.inventory import StockLocation, StockMovement
from app.core.logger import request_logger

class SeasonService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def apply_seasonal_discount(self, season_id: int, discount_pct: float) -> Dict[str, Any]:
        """Apply a markdown to all SKUs associated with a season."""
        season = self.db.query(Season).filter(
            Season.id == season_id, 
            Season.tenant_id == self.tenant_id
        ).first()
        
        if not season:
            return {"status": "error", "message": "Season not found"}

        # Find all products in this season
        products = self.db.query(Product).filter(
            Product.season_id == season_id,
            Product.tenant_id == self.tenant_id
        ).all()
        product_ids = [p.id for p in products]

        if not product_ids:
            return {"status": "success", "updated_skus": 0, "message": "No products found for this season"}

        # Update all SKUs for these products
        skus = self.db.query(ProductSKU).filter(
            ProductSKU.product_id.in_(product_ids)
        ).all()

        for sku in skus:
            sku.seasonal_discount_pct = discount_pct
            if sku.selling_price:
                sku.seasonal_price = round(sku.selling_price * (1 - discount_pct / 100), 2)
        
        season.discount_pct = discount_pct
        self.db.commit()

        return {
            "status": "success",
            "updated_skus": len(skus),
            "discount_applied": discount_pct,
            "season": season.name
        }

    def close_season(self, season_id: int, clearance_location_id: Optional[int] = 0) -> Dict[str, Any]:
        """Move remaining stock of a season to a clearance location and finish the season."""
        season = self.db.query(Season).filter(
            Season.id == season_id, 
            Season.tenant_id == self.tenant_id
        ).first()
        
        if not season:
            return {"status": "error", "message": "Season not found"}

        clearance_loc = None
        if clearance_location_id and clearance_location_id > 0:
            clearance_loc = self.db.query(StockLocation).filter(
                StockLocation.id == clearance_location_id,
                StockLocation.tenant_id == self.tenant_id
            ).first()

        # Find all products in this season
        products = self.db.query(Product).filter(
            Product.season_id == season_id,
            Product.tenant_id == self.tenant_id
        ).all()
        product_ids = [p.id for p in products]

        # Find all current stock for these products that is NOT already in the clearance location
        stock_items = self.db.query(StockLocation).filter(
            StockLocation.product_id.in_(product_ids),
            StockLocation.id != clearance_location_id,
            StockLocation.quantity > 0
        ).all()

        total_moved = 0
        for item in stock_items:
            qty_to_move = item.quantity
            
            # 1. Deduct from current location
            item.quantity = 0
            
            # 2. Add to clearance location
            # Note: StockLocation in this system seems to be per-product. 
            # If so, I need to find the specific Clearance StockLocation for EACH product.
            # Wait, looking at StockLocation model: product_id is a column. 
            # This means StockLocation is actually a (Location x Product) record.
            
            target_loc = self.db.query(StockLocation).filter(
                StockLocation.tenant_id == self.tenant_id,
                StockLocation.product_id == item.product_id,
                StockLocation.is_clearance == True
            ).first()

            if not target_loc:
                # Create a clearance record for this product
                target_loc = StockLocation(
                    tenant_id=self.tenant_id,
                    product_id=item.product_id,
                    name="Clearance Shelf",
                    is_clearance=True,
                    quantity=0
                )
                self.db.add(target_loc)
                self.db.flush()

            target_loc.quantity += qty_to_move
            
            # 3. Log Movement
            movement = StockMovement(
                tenant_id=self.tenant_id,
                product_id=item.product_id,
                location_id=target_loc.id,
                movement_type="transfer",
                quantity=qty_to_move,
                reason="Season Close Transfer",
                notes=f"Moved from {item.name} to Clearance"
            )
            self.db.add(movement)
            total_moved += qty_to_move

        season.status = "finished"
        self.db.commit()

        return {
            "status": "success",
            "total_items_moved": total_moved,
            "season": season.name,
            "new_status": season.status
        }
