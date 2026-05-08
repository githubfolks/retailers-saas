from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_write_permission
from app.models.brand import Brand

router = APIRouter(prefix="/brands", tags=["brands"], dependencies=[Depends(check_write_permission("inventory"))])

class BrandBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None

class BrandResponse(BrandBase):
    id: int
    tenant_id: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[BrandResponse])
async def list_brands(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    return db.query(Brand).filter(Brand.tenant_id == current_tenant_id).all()

@router.post("/", response_model=BrandResponse)
async def create_brand(
    brand: BrandCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    db_brand = Brand(
        tenant_id=current_tenant_id,
        name=brand.name,
        description=brand.description,
        logo_url=brand.logo_url
    )
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: int,
    brand_update: BrandUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    db_brand = db.query(Brand).filter(
        Brand.id == brand_id,
        Brand.tenant_id == current_tenant_id
    ).first()
    
    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    update_data = brand_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_brand, key, value)
    
    db.commit()
    db.refresh(db_brand)
    return db_brand

@router.delete("/{brand_id}")
async def delete_brand(
    brand_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    db_brand = db.query(Brand).filter(
        Brand.id == brand_id,
        Brand.tenant_id == current_tenant_id
    ).first()
    
    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    db.delete(db_brand)
    db.commit()
    return {"status": "success", "message": "Brand deleted"}
