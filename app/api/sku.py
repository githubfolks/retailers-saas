"""
SKU Management API Endpoints
Provides REST API for SKU operations and lookups
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.limiter import limiter
from app.models.sku import ProductSKU, SKUBarcode, SKUPlatformMapping
from app.services.sku_lookup_service import SKULookupService
from app.core.logger import get_logger
from app.api.auth import get_current_tenant_id as get_current_tenant, check_permission

logger = get_logger(__name__)
router = APIRouter(prefix="/sku", tags=["SKU Management"], dependencies=[Depends(check_permission("inventory"))])


# ========== PYDANTIC SCHEMAS ==========

class ProductSKUResponse(BaseModel):
    sku: str
    product_name: str
    category: Optional[str]
    cost_price: Optional[float]
    selling_price: Optional[float]
    seasonal_price: Optional[float] = None
    seasonal_discount_pct: Optional[float] = 0.0
    reorder_point: int
    odoo_product_id: Optional[int]
    shopify_product_id: Optional[str]
    woocommerce_product_id: Optional[int]
    amazon_asin: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class ProductSKUDetailResponse(ProductSKUResponse):
    description: Optional[str]
    unit_of_measure: str
    lead_time_days: int
    created_at: datetime
    updated_at: datetime


class BarcodeResponse(BaseModel):
    barcode: str
    barcode_type: str
    is_primary: bool
    is_active: bool
    scanned_count: int
    
    class Config:
        from_attributes = True


class SKULookupResponse(BaseModel):
    sku: str
    product_name: str
    total_stock: int
    available_stock: int
    platforms: dict


class PlatformMappingResponse(BaseModel):
    sku: str
    platform_name: str
    platform_product_id: str
    platform_stock_level: int
    sync_status: str
    last_synced: Optional[datetime]
    
    class Config:
        from_attributes = True


# ========== SKU LOOKUP ENDPOINTS ==========

@router.get("/lookup/{sku}", response_model=SKULookupResponse)
@limiter.limit("30/minute")
def lookup_sku(
    request: Request,
    sku: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Look up product by SKU (primary lookup method)
    Returns: Product details + current stock levels + platform mappings
    """
    try:
        service = SKULookupService(db)
        product = service.get_product_by_sku(sku, tenant_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SKU {sku} not found"
            )
        
        return SKULookupResponse(
            sku=product.sku,
            product_name=product.product_name,
            total_stock=service.get_total_stock_by_sku(sku, tenant_id),
            available_stock=service.get_available_stock_by_sku(sku, tenant_id),
            platforms=service.get_platform_ids_for_sku(sku, tenant_id)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up SKU {sku}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error looking up SKU"
        )


@router.get("/lookup/barcode/{barcode}", response_model=SKULookupResponse)
@limiter.limit("30/minute")
def lookup_by_barcode(
    request: Request,
    barcode: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Look up product by scanning barcode
    Returns: Product details + stock levels
    """
    try:
        service = SKULookupService(db)
        product = service.get_product_by_barcode(barcode, tenant_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No product found for barcode {barcode}"
            )
        
        sku = product.sku
        return SKULookupResponse(
            sku=sku,
            product_name=product.product_name,
            total_stock=service.get_total_stock_by_sku(sku, tenant_id),
            available_stock=service.get_available_stock_by_sku(sku, tenant_id),
            platforms=service.get_platform_ids_for_sku(sku, tenant_id)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up barcode {barcode}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error looking up barcode"
        )


@router.get("/lookup/odoo/{odoo_product_id}", response_model=SKULookupResponse)
@limiter.limit("30/minute")
def lookup_by_odoo_id(
    request: Request,
    odoo_product_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Look up product by Odoo product ID"""
    try:
        service = SKULookupService(db)
        product = service.get_product_by_odoo_id(odoo_product_id, tenant_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with Odoo ID {odoo_product_id} not found"
            )
        
        sku = product.sku
        return SKULookupResponse(
            sku=sku,
            product_name=product.product_name,
            total_stock=service.get_total_stock_by_sku(sku, tenant_id),
            available_stock=service.get_available_stock_by_sku(sku, tenant_id),
            platforms=service.get_platform_ids_for_sku(sku, tenant_id)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up Odoo product {odoo_product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error looking up product"
        )


@router.get("/lookup/shopify/{shopify_product_id}", response_model=SKULookupResponse)
@limiter.limit("30/minute")
def lookup_by_shopify_id(
    request: Request,
    shopify_product_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Look up product by Shopify product ID"""
    try:
        service = SKULookupService(db)
        product = service.get_product_by_shopify_id(shopify_product_id, tenant_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with Shopify ID {shopify_product_id} not found"
            )
        
        sku = product.sku
        return SKULookupResponse(
            sku=sku,
            product_name=product.product_name,
            total_stock=service.get_total_stock_by_sku(sku, tenant_id),
            available_stock=service.get_available_stock_by_sku(sku, tenant_id),
            platforms=service.get_platform_ids_for_sku(sku, tenant_id)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up Shopify product {shopify_product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error looking up product"
        )


@router.get("/lookup/amazon/{asin}", response_model=SKULookupResponse)
@limiter.limit("30/minute")
def lookup_by_amazon_asin(
    request: Request,
    asin: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Look up product by Amazon ASIN"""
    try:
        service = SKULookupService(db)
        product = service.get_product_by_amazon_asin(asin, tenant_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ASIN {asin} not found"
            )
        
        sku = product.sku
        return SKULookupResponse(
            sku=sku,
            product_name=product.product_name,
            total_stock=service.get_total_stock_by_sku(sku, tenant_id),
            available_stock=service.get_available_stock_by_sku(sku, tenant_id),
            platforms=service.get_platform_ids_for_sku(sku, tenant_id)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up Amazon product {asin}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error looking up product"
        )


# ========== DETAIL ENDPOINTS ==========

@router.get("/detail/{sku}", response_model=ProductSKUDetailResponse)
@limiter.limit("30/minute")
def get_sku_details(
    request: Request,
    sku: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get complete product details including all metadata"""
    try:
        service = SKULookupService(db)
        product = service.get_product_by_sku(sku, tenant_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SKU {sku} not found"
            )
        
        return ProductSKUDetailResponse.from_orm(product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching SKU details {sku}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching SKU details"
        )


@router.get("/{sku}/barcodes", response_model=List[BarcodeResponse])
@limiter.limit("30/minute")
def get_sku_barcodes(
    request: Request,
    sku: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get all barcodes associated with SKU (primary + alternate)"""
    try:
        service = SKULookupService(db)
        barcodes = service.get_all_barcodes_for_sku(sku, tenant_id)
        
        return [BarcodeResponse.from_orm(bc) for bc in barcodes]
    except Exception as e:
        logger.error(f"Error fetching barcodes for {sku}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching barcodes"
        )


@router.get("/{sku}/platforms", response_model=List[PlatformMappingResponse])
@limiter.limit("30/minute")
def get_sku_platform_mappings(
    request: Request,
    sku: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get all platform mappings for SKU (Odoo, Shopify, Amazon, etc)"""
    try:
        mappings = db.query(SKUPlatformMapping).filter(
            SKUPlatformMapping.sku == sku,
            SKUPlatformMapping.tenant_id == tenant_id
        ).all()
        
        return [PlatformMappingResponse.from_orm(m) for m in mappings]
    except Exception as e:
        logger.error(f"Error fetching platform mappings for {sku}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching platform mappings"
        )


# ========== SEARCH ENDPOINTS ==========

@router.get("/search", response_model=List[ProductSKUResponse])
@limiter.limit("30/minute")
def search_products(
    request: Request,
    q: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Search products by SKU, name, or other attributes
    Query can be partial (e.g., "shirt" matches "SHIRT-BLUE-001")
    """
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )
    
    try:
        service = SKULookupService(db)
        products = service.search_products(q, tenant_id)
        
        return [ProductSKUResponse.from_orm(p) for p in products]
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching products"
        )


@router.get("/category/{category}", response_model=List[ProductSKUResponse])
@limiter.limit("30/minute")
def get_category_products(
    request: Request,
    category: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get all active products in a category"""
    try:
        service = SKULookupService(db)
        products = service.get_products_by_category(category, tenant_id)
        
        return [ProductSKUResponse.from_orm(p) for p in products]
    except Exception as e:
        logger.error(f"Error fetching category {category}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching category products"
        )


# ========== STATUS ENDPOINTS ==========

@router.get("/low-stock/list", response_model=List[dict])
@limiter.limit("30/minute")
def get_low_stock_products(
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get all products currently below reorder point"""
    try:
        service = SKULookupService(db)
        low_stock = service.get_low_stock_products(tenant_id)
        
        return low_stock
    except Exception as e:
        logger.error(f"Error fetching low stock products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching low stock products"
        )


@router.get("/sync-status/{platform}", response_model=List[dict])
@limiter.limit("30/minute")
def get_pending_syncs(
    request: Request,
    platform: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get all SKUs pending sync to a specific platform"""
    try:
        service = SKULookupService(db)
        pending = service.get_pending_syncs(platform, tenant_id)
        
        return [
            {
                'sku': p.sku,
                'platform': p.platform_name,
                'status': p.sync_status,
                'last_synced': p.last_synced
            }
            for p in pending
        ]
    except Exception as e:
        logger.error(f"Error fetching pending syncs for {platform}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching pending syncs"
        )
