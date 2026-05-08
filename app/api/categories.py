from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_write_permission
from app.models.category import Category

router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(check_write_permission("inventory"))])

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    tenant_id: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    return db.query(Category).filter(Category.tenant_id == current_tenant_id).all()

@router.post("/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    db_category = Category(
        tenant_id=current_tenant_id,
        name=category.name,
        description=category.description,
        parent_id=category.parent_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    db_category = db.query(Category).filter(
        Category.id == category_id,
        Category.tenant_id == current_tenant_id
    ).first()
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    db_category = db.query(Category).filter(
        Category.id == category_id,
        Category.tenant_id == current_tenant_id
    ).first()
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    return {"status": "success", "message": "Category deleted"}
