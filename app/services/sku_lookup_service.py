"""
SKU Lookup Service
Central service for finding products across all platforms using SKU
"""

from sqlalchemy.orm import Session
from app.models.sku import (
    ProductSKU, SKUBarcode, SKUPlatformMapping, 
    SKUInventoryMapping, SKUAlertRule
)
from app.models.procurement import ProductBarcode as OldProductBarcode
from app.core.logger import get_logger
from typing import Optional, List, Dict

logger = get_logger(__name__)


class SKULookupService:
    """
    Service for SKU-based product lookups
    Provides unified interface for finding products across all platforms
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========== BASIC SKU LOOKUPS ==========
    
    def get_product_by_sku(self, sku: str, tenant_id: str) -> Optional[ProductSKU]:
        """
        Get product master record by SKU
        Primary lookup method - SKU is the universal identifier
        """
        try:
            return self.db.query(ProductSKU).filter(
                ProductSKU.sku == sku,
                ProductSKU.tenant_id == tenant_id
            ).first()
        except Exception as e:
            logger.error(f"Error fetching SKU {sku}: {str(e)}")
            return None
    
    def get_product_by_barcode(self, barcode: str, tenant_id: str) -> Optional[ProductSKU]:
        """
        Get product by scanning barcode
        Barcode → SKU → Product
        """
        try:
            barcode_record = self.db.query(SKUBarcode).filter(
                SKUBarcode.barcode == barcode,
                SKUBarcode.tenant_id == tenant_id,
                SKUBarcode.is_active == True
            ).first()
            
            if barcode_record:
                return self.get_product_by_sku(barcode_record.sku, tenant_id)
            return None
        except Exception as e:
            logger.error(f"Error fetching product by barcode {barcode}: {str(e)}")
            return None
    
    def get_sku_by_barcode(self, barcode: str, tenant_id: str) -> Optional[str]:
        """Quick lookup: barcode → SKU only"""
        try:
            record = self.db.query(SKUBarcode).filter(
                SKUBarcode.barcode == barcode,
                SKUBarcode.tenant_id == tenant_id
            ).first()
            return record.sku if record else None
        except Exception as e:
            logger.error(f"Error looking up SKU for barcode {barcode}: {str(e)}")
            return None
    
    # ========== PLATFORM-SPECIFIC LOOKUPS ==========
    
    def get_product_by_odoo_id(self, odoo_product_id: int, tenant_id: str) -> Optional[ProductSKU]:
        """Get product by Odoo product ID"""
        try:
            return self.db.query(ProductSKU).filter(
                ProductSKU.odoo_product_id == odoo_product_id,
                ProductSKU.tenant_id == tenant_id
            ).first()
        except Exception as e:
            logger.error(f"Error fetching product by Odoo ID {odoo_product_id}: {str(e)}")
            return None
    
    def get_product_by_shopify_id(self, shopify_product_id: str, tenant_id: str) -> Optional[ProductSKU]:
        """Get product by Shopify product ID"""
        try:
            return self.db.query(ProductSKU).filter(
                ProductSKU.shopify_product_id == shopify_product_id,
                ProductSKU.tenant_id == tenant_id
            ).first()
        except Exception as e:
            logger.error(f"Error fetching product by Shopify ID {shopify_product_id}: {str(e)}")
            return None
    
    def get_product_by_woocommerce_id(self, wc_product_id: int, tenant_id: str) -> Optional[ProductSKU]:
        """Get product by WooCommerce product ID"""
        try:
            return self.db.query(ProductSKU).filter(
                ProductSKU.woocommerce_product_id == wc_product_id,
                ProductSKU.tenant_id == tenant_id
            ).first()
        except Exception as e:
            logger.error(f"Error fetching product by WooCommerce ID {wc_product_id}: {str(e)}")
            return None
    
    def get_product_by_amazon_asin(self, asin: str, tenant_id: str) -> Optional[ProductSKU]:
        """Get product by Amazon ASIN"""
        try:
            return self.db.query(ProductSKU).filter(
                ProductSKU.amazon_asin == asin,
                ProductSKU.tenant_id == tenant_id
            ).first()
        except Exception as e:
            logger.error(f"Error fetching product by Amazon ASIN {asin}: {str(e)}")
            return None
    
    def get_product_by_ebay_id(self, ebay_item_id: str, tenant_id: str) -> Optional[ProductSKU]:
        """Get product by eBay item ID"""
        try:
            return self.db.query(ProductSKU).filter(
                ProductSKU.ebay_item_id == ebay_item_id,
                ProductSKU.tenant_id == tenant_id
            ).first()
        except Exception as e:
            logger.error(f"Error fetching product by eBay ID {ebay_item_id}: {str(e)}")
            return None
    
    # ========== INVENTORY LOOKUPS ==========
    
    def get_inventory_by_sku(self, sku: str, tenant_id: str) -> List[SKUInventoryMapping]:
        """Get all inventory locations for SKU"""
        try:
            return self.db.query(SKUInventoryMapping).filter(
                SKUInventoryMapping.sku == sku,
                SKUInventoryMapping.tenant_id == tenant_id
            ).all()
        except Exception as e:
            logger.error(f"Error fetching inventory for SKU {sku}: {str(e)}")
            return []
    
    def get_total_stock_by_sku(self, sku: str, tenant_id: str) -> int:
        """Get total stock across all locations for SKU"""
        try:
            locations = self.get_inventory_by_sku(sku, tenant_id)
            return sum(loc.quantity_on_hand for loc in locations)
        except Exception as e:
            logger.error(f"Error calculating total stock for SKU {sku}: {str(e)}")
            return 0
    
    def get_available_stock_by_sku(self, sku: str, tenant_id: str) -> int:
        """Get available stock (on-hand - reserved) for SKU"""
        try:
            locations = self.get_inventory_by_sku(sku, tenant_id)
            return sum(loc.quantity_available for loc in locations)
        except Exception as e:
            logger.error(f"Error calculating available stock for SKU {sku}: {str(e)}")
            return 0
    
    def get_inventory_by_warehouse(self, sku: str, warehouse_id: int, 
                                   tenant_id: str) -> Optional[SKUInventoryMapping]:
        """Get SKU inventory at specific warehouse"""
        try:
            return self.db.query(SKUInventoryMapping).filter(
                SKUInventoryMapping.sku == sku,
                SKUInventoryMapping.warehouse_id == warehouse_id,
                SKUInventoryMapping.tenant_id == tenant_id
            ).first()
        except Exception as e:
            logger.error(f"Error fetching inventory for {sku} at warehouse {warehouse_id}: {str(e)}")
            return None
    
    # ========== PLATFORM MAPPING LOOKUPS ==========
    
    def get_platform_ids_for_sku(self, sku: str, tenant_id: str) -> Dict[str, str]:
        """
        Get all platform IDs mapped to SKU
        Returns: {'odoo': id, 'shopify': id, 'woocommerce': id, etc}
        """
        try:
            product = self.get_product_by_sku(sku, tenant_id)
            if not product:
                return {}
            
            mapping = {
                'sku': product.sku,
                'odoo': product.odoo_product_id,
                'shopify': product.shopify_product_id,
                'woocommerce': product.woocommerce_product_id,
                'amazon': product.amazon_asin,
                'ebay': product.ebay_item_id,
            }
            return {k: v for k, v in mapping.items() if v}  # Remove None values
        except Exception as e:
            logger.error(f"Error fetching platform IDs for SKU {sku}: {str(e)}")
            return {}
    
    def get_sku_by_platform_id(self, platform: str, platform_id: str, 
                               tenant_id: str) -> Optional[str]:
        """
        Reverse lookup: platform ID → SKU
        Fast lookup by platform-specific ID
        """
        try:
            mapping = self.db.query(SKUPlatformMapping).filter(
                SKUPlatformMapping.platform_name == platform,
                SKUPlatformMapping.platform_product_id == platform_id,
                SKUPlatformMapping.tenant_id == tenant_id
            ).first()
            return mapping.sku if mapping else None
        except Exception as e:
            logger.error(f"Error fetching SKU for {platform} ID {platform_id}: {str(e)}")
            return None
    
    # ========== BATCH LOOKUPS ==========
    
    def get_products_by_skus(self, skus: List[str], tenant_id: str) -> List[ProductSKU]:
        """Get multiple products by list of SKUs"""
        try:
            return self.db.query(ProductSKU).filter(
                ProductSKU.sku.in_(skus),
                ProductSKU.tenant_id == tenant_id
            ).all()
        except Exception as e:
            logger.error(f"Error fetching products by SKU list: {str(e)}")
            return []
    
    def get_products_by_category(self, category: str, tenant_id: str, 
                                 active_only: bool = True) -> List[ProductSKU]:
        """Get all products in a category"""
        try:
            query = self.db.query(ProductSKU).filter(
                ProductSKU.category == category,
                ProductSKU.tenant_id == tenant_id
            )
            if active_only:
                query = query.filter(ProductSKU.is_active == True)
            return query.all()
        except Exception as e:
            logger.error(f"Error fetching products by category {category}: {str(e)}")
            return []
    
    # ========== BARCODE OPERATIONS ==========
    
    def get_all_barcodes_for_sku(self, sku: str, tenant_id: str) -> List[SKUBarcode]:
        """Get all barcodes (primary and alternate) for SKU"""
        try:
            return self.db.query(SKUBarcode).filter(
                SKUBarcode.sku == sku,
                SKUBarcode.tenant_id == tenant_id,
                SKUBarcode.is_active == True
            ).all()
        except Exception as e:
            logger.error(f"Error fetching barcodes for SKU {sku}: {str(e)}")
            return []
    
    def get_primary_barcode_for_sku(self, sku: str, tenant_id: str) -> Optional[str]:
        """Get primary barcode for SKU"""
        try:
            record = self.db.query(SKUBarcode).filter(
                SKUBarcode.sku == sku,
                SKUBarcode.tenant_id == tenant_id,
                SKUBarcode.is_primary == True
            ).first()
            return record.barcode if record else None
        except Exception as e:
            logger.error(f"Error fetching primary barcode for SKU {sku}: {str(e)}")
            return None
    
    # ========== SEARCH & FILTER ==========
    
    def search_products(self, query: str, tenant_id: str) -> List[ProductSKU]:
        """
        Search products by SKU, name, or barcode
        Full-text search support
        """
        try:
            search_term = f"%{query}%"
            
            # Search in SKU, product name, and barcodes
            skus_found = self.db.query(ProductSKU).filter(
                ProductSKU.tenant_id == tenant_id,
                (ProductSKU.sku.ilike(search_term) | 
                 ProductSKU.product_name.ilike(search_term))
            ).all()
            
            return skus_found
        except Exception as e:
            logger.error(f"Error searching products with query '{query}': {str(e)}")
            return []
    
    def get_low_stock_products(self, tenant_id: str) -> List[Dict]:
        """Get all products below reorder point"""
        try:
            mappings = self.db.query(SKUInventoryMapping).filter(
                SKUInventoryMapping.tenant_id == tenant_id
            ).all()
            
            low_stock = []
            for mapping in mappings:
                if mapping.quantity_available <= 0:  # Below 0 means out of stock
                    product = self.get_product_by_sku(mapping.sku, tenant_id)
                    if product:
                        low_stock.append({
                            'sku': product.sku,
                            'name': product.product_name,
                            'current_stock': mapping.quantity_available,
                            'reorder_point': product.reorder_point,
                            'reorder_quantity': product.reorder_quantity
                        })
            
            return low_stock
        except Exception as e:
            logger.error(f"Error fetching low stock products: {str(e)}")
            return []
    
    # ========== SYNC HELPERS ==========
    
    def mark_platform_synced(self, sku: str, platform: str, tenant_id: str):
        """Mark platform mapping as synced"""
        try:
            from datetime import datetime
            self.db.query(SKUPlatformMapping).filter(
                SKUPlatformMapping.sku == sku,
                SKUPlatformMapping.platform_name == platform,
                SKUPlatformMapping.tenant_id == tenant_id
            ).update({
                'last_synced': datetime.utcnow(),
                'sync_status': 'synced'
            })
            self.db.commit()
        except Exception as e:
            logger.error(f"Error marking platform sync for {sku} on {platform}: {str(e)}")
    
    def get_pending_syncs(self, platform: str, tenant_id: str) -> List[SKUPlatformMapping]:
        """Get all SKUs pending sync to a platform"""
        try:
            return self.db.query(SKUPlatformMapping).filter(
                SKUPlatformMapping.platform_name == platform,
                SKUPlatformMapping.sync_status != 'synced',
                SKUPlatformMapping.tenant_id == tenant_id
            ).all()
        except Exception as e:
            logger.error(f"Error fetching pending syncs for {platform}: {str(e)}")
            return []
