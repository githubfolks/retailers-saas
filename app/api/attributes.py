from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.auth import get_current_tenant_id
from app.models.attribute import Attribute, AttributeValue

router = APIRouter(prefix="/attributes", tags=["attributes"])

class AttributeValueBase(BaseModel):
    value: str
    hex_color: Optional[str] = None

class AttributeValueCreate(AttributeValueBase):
    pass

class AttributeValueResponse(AttributeValueBase):
    id: int
    attribute_id: int

    class Config:
        from_attributes = True

class AttributeResponse(BaseModel):
    id: int
    tenant_id: str
    name: str
    display_type: str
    values: List[AttributeValueResponse]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AttributeResponse])
async def list_attributes(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    return db.query(Attribute).filter(Attribute.tenant_id == current_tenant_id).all()

@router.post("/seed")
async def seed_standard_attributes(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Seed standard Sizes and Colors for garment business."""
    # 1. Size Attribute
    size_attr = db.query(Attribute).filter(
        Attribute.tenant_id == current_tenant_id, 
        Attribute.name == "Size"
    ).first()
    
    if not size_attr:
        size_attr = Attribute(tenant_id=current_tenant_id, name="Size", display_type="radio")
        db.add(size_attr)
        db.flush()
        
        standard_sizes = ["S", "M", "L", "XL", "XXL"]
        for s in standard_sizes:
            db.add(AttributeValue(attribute_id=size_attr.id, value=s))

    # 2. Color Attribute
    color_attr = db.query(Attribute).filter(
        Attribute.tenant_id == current_tenant_id, 
        Attribute.name == "Color"
    ).first()
    
    if not color_attr:
        color_attr = Attribute(tenant_id=current_tenant_id, name="Color", display_type="color_picker")
        db.add(color_attr)
        db.flush()
        
        standard_colors = [
            ("Red", "#FF0000"), ("Blue", "#0000FF"), 
            ("Black", "#000000"), ("White", "#FFFFFF"),
            ("Green", "#008000"), ("Navy", "#000080")
        ]
        for name, hex in standard_colors:
            db.add(AttributeValue(attribute_id=color_attr.id, value=name, hex_color=hex))

    db.commit()
    return {"status": "success", "message": "Standard attributes seeded"}
