from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Response
from fastapi.responses import StreamingResponse
from celery.result import AsyncResult
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_write_permission
from app.core.logger import request_logger
from app.models.image import ProductImage
import shutil
import os
import uuid
from app.models.category import Category
from app.models.brand import Brand
from app.models.attribute import AttributeValue
from app.models.sku import ProductSKU

router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(check_write_permission("inventory"))])


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    sku: str
    quantity: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    sku: Optional[str] = None
    quantity: Optional[int] = None


class ImageResponse(BaseModel):
    url: str
    is_primary: bool = False
    alt_text: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]

    class Config:
        from_attributes = True


class BrandResponse(BaseModel):
    id: int
    name: str
    logo_url: Optional[str]

    class Config:
        from_attributes = True


class UnitResponse(BaseModel):
    id: int
    name: str
    abbreviation: str

    class Config:
        from_attributes = True


class VariantResponse(BaseModel):
    id: int
    sku: str
    product_name: str
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    quantity: Optional[int] = None
    size: Optional[str] = None
    color: Optional[str] = None
    seasonal_price: Optional[float] = None
    seasonal_discount_pct: Optional[float] = 0.0
    
    class Config:
        from_attributes = True


class VariantInput(BaseModel):
    size_id: int
    color_id: int
    quantity: int
    cost_price: float
    selling_price: float
    sku_override: Optional[str] = None

class ProductWithVariantsCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    brand_id: int
    unit_id: int
    variants: List[VariantInput]
    image_urls: Optional[List[str]] = []


class ProductResponse(BaseModel):
    id: int
    tenant_id: str
    name: str
    description: Optional[str] = None
    price: float
    sku: str
    quantity: int
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None
    season_id: Optional[int] = None
    collection_id: Optional[int] = None
    category_rel: Optional[CategoryResponse] = None
    brand_rel: Optional[BrandResponse] = None
    unit_rel: Optional[UnitResponse] = None
    variants: List[VariantResponse] = []
    images: List[ImageResponse] = []
    
    class Config:
        from_attributes = True


def get_product_model():
    """Lazy load Product model to avoid circular imports."""
    from app.models.product import Product
    return Product


@router.post("/upload")
async def upload_product_image(
    file: UploadFile = File(...),
    current_tenant_id: str = Depends(get_current_tenant_id)
):
    """Upload a product image and return its URL."""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "app/static/uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"url": f"/static/uploads/{filename}"}

    except Exception as e:
        request_logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading image")


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    season_id: Optional[int] = None,
    collection_id: Optional[int] = None
):
    """List all products for current tenant."""
    try:
        Product = get_product_model()
        
        query = db.query(Product).filter(
            Product.tenant_id == current_tenant_id
        )
        
        if season_id:
            query = query.filter(Product.season_id == season_id)
        if collection_id:
            query = query.filter(Product.collection_id == collection_id)
            
        products = query.offset(skip).limit(limit).all()
        
        request_logger.info(
            f"Listed {len(products)} products for tenant: {current_tenant_id}"
        )
        
        return products
    
    except Exception as e:
        request_logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing products")


@router.post("/with-variants", response_model=ProductResponse)
async def create_product_with_variants(
    data: ProductWithVariantsCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a product template and its variants in bulk."""
    Product = get_product_model()
    
    # 1. Verify Category and Brand codes
    cat = db.query(Category).get(data.category_id)
    brand = db.query(Brand).get(data.brand_id)
    
    cat_code = cat.code if cat and cat.code else "GEN"
    brand_code = brand.code if brand and brand.code else "GEN"

    # 2. Create Template
    db_product = Product(
        tenant_id=current_tenant_id,
        name=data.name,
        description=data.description,
        price=data.price,
        category_id=data.category_id,
        brand_id=data.brand_id,
        unit_id=data.unit_id,
        quantity=sum(v.quantity for v in data.variants)
    )
    db.add(db_product)
    db.flush()

    # 3. Create Variants
    for v_input in data.variants:
        size_val = db.query(AttributeValue).get(v_input.size_id)
        color_val = db.query(AttributeValue).get(v_input.color_id)
        
        size_code = size_val.value if size_val else "NA"
        color_code = color_val.value if color_val else "NA"
        
        # Generate SKU: CAT-BRAND-SIZE-COLOR
        if v_input.sku_override:
            variant_sku = v_input.sku_override
        else:
            variant_sku = f"{cat_code}-{brand_code}-{size_code}-{color_code}".upper()

        new_variant = ProductSKU(
            tenant_id=current_tenant_id,
           product_id=db_product.id,
           product_name=f"{data.name} ({size_code}/{color_code})",
           sku=variant_sku,
           category_id=data.category_id,
           brand_id=data.brand_id,
           unit_id=data.unit_id,
           cost_price=v_input.cost_price,
           selling_price=v_input.selling_price,
           size=size_code,
           color=color_code
        )
        db.add(new_variant)
        # Link attribute values
        if size_val: new_variant.attribute_values.append(size_val)
        if color_val: new_variant.attribute_values.append(color_val)

    # 4. Handle Images
    if data.image_urls:
        for idx, url in enumerate(data.image_urls):
            db_image = ProductImage(
                tenant_id=current_tenant_id,
                product_id=db_product.id,
                url=url,
                is_primary=(idx == 0),
                position=idx
            )
            db.add(db_image)

    db.commit()
    db.refresh(db_product)
    return db_product

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new product for current tenant."""
    try:
        Product = get_product_model()
        
        existing = db.query(Product).filter(
            Product.tenant_id == current_tenant_id,
            Product.sku == product.sku
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Product with SKU {product.sku} already exists"
            )
        
        db_product = Product(
            tenant_id=current_tenant_id,
            name=product.name,
            description=product.description,
            price=product.price,
            sku=product.sku,
            quantity=product.quantity
        )
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        request_logger.info(
            f"Created product {db_product.id} for tenant: {current_tenant_id}"
        )
        
        return db_product
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        request_logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating product")


@router.get("/template")
async def get_bulk_template(
    format: str = "csv",
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Download a template for bulk product upload."""
    from app.services.bulk_service import BulkUploadService
    service = BulkUploadService(db, current_tenant_id)
    template_file = service.get_template(format)
    
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if format == "xlsx" else "text/csv"
    filename = f"product_template.{format}"
    
    return StreamingResponse(
        template_file,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/bulk")
async def bulk_upload_products(
    file: UploadFile = File(...),
    current_tenant_id: str = Depends(get_current_tenant_id)
):
    """Trigger async bulk create/update products from CSV/Excel."""
    from app.tasks import process_bulk_upload_task
    
    content = await file.read()
    task = process_bulk_upload_task.delay(current_tenant_id, content, file.filename)
    
    return {
        "status": "accepted",
        "task_id": task.id,
        "message": "Bulk upload started in background"
    }

@router.get("/bulk/status/{task_id}")
async def get_bulk_status(
    task_id: str,
    current_tenant_id: str = Depends(get_current_tenant_id)
):
    """Check the status of a bulk upload task."""
    task_result = AsyncResult(task_id)
    
    result = {
        "task_id": task_id,
        "status": task_result.status,
    }
    
    if task_result.ready():
        result["result"] = task_result.result
        
    return result


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get a specific product for current tenant."""
    try:
        Product = get_product_model()
        
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.tenant_id == current_tenant_id
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product
    
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error(f"Error getting product: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting product")


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Update a product for current tenant."""
    try:
        Product = get_product_model()
        
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.tenant_id == current_tenant_id
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        update_data = product_update.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            if value is not None:
                setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        
        request_logger.info(
            f"Updated product {product_id} for tenant: {current_tenant_id}"
        )
        
        return product
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        request_logger.error(f"Error updating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating product")


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Delete a product for current tenant."""
    try:
        Product = get_product_model()
        
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.tenant_id == current_tenant_id
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        db.delete(product)
        db.commit()
        
        request_logger.info(
            f"Deleted product {product_id} for tenant: {current_tenant_id}"
        )
        
        return {
            "status": "deleted",
            "product_id": product_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        request_logger.error(f"Error deleting product: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting product")
