from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.api.auth import get_current_tenant_id
from app.models.coupon import Coupon

router = APIRouter(prefix="/coupons", tags=["coupons"])

class CouponBase(BaseModel):
    code: str
    discount_type: str # "percentage" or "fixed"
    discount_value: float
    min_purchase_amount: float = 0.0
    max_discount_amount: Optional[float] = None
    valid_until: Optional[datetime] = None
    usage_limit: Optional[int] = None

class CouponCreate(CouponBase):
    pass

class CouponResponse(CouponBase):
    id: int
    tenant_id: str
    is_active: bool
    usage_count: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=CouponResponse)
async def create_coupon(
    coupon_data: CouponCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new discount coupon."""
    # Check if code already exists for this tenant
    existing = db.query(Coupon).filter(
        Coupon.tenant_id == current_tenant_id,
        Coupon.code == coupon_data.code.upper()
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    
    coupon_dict = coupon_data.dict()
    coupon_dict["code"] = coupon_data.code.upper()
    new_coupon = Coupon(tenant_id=current_tenant_id, **coupon_dict)
    
    db.add(new_coupon)
    db.commit()
    db.refresh(new_coupon)
    return new_coupon

@router.get("/", response_model=List[CouponResponse])
async def list_coupons(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    active_only: bool = False
):
    """List all coupons for the tenant."""
    query = db.query(Coupon).filter(Coupon.tenant_id == current_tenant_id)
    if active_only:
        query = query.filter(Coupon.is_active == True)
    
    return query.all()

@router.delete("/{coupon_id}")
async def delete_coupon(
    coupon_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Deactivate a coupon."""
    coupon = db.query(Coupon).filter(
        Coupon.id == coupon_id,
        Coupon.tenant_id == current_tenant_id
    ).first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    coupon.is_active = False
    db.commit()
    return {"status": "deactivated"}

@router.get("/validate/{code}")
async def validate_coupon(
    code: str,
    purchase_amount: float,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Validate a coupon code and return discount amount."""
    coupon = db.query(Coupon).filter(
        Coupon.tenant_id == current_tenant_id,
        Coupon.code == code.upper(),
        Coupon.is_active == True
    ).first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon code")
    
    if coupon.valid_until and coupon.valid_until < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Coupon has expired")
        
    if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
        
    if purchase_amount < coupon.min_purchase_amount:
        raise HTTPException(
            status_code=400, 
            detail=f"Minimum purchase of ₹{coupon.min_purchase_amount} required"
        )
    
    # Calculate discount
    discount = 0.0
    if coupon.discount_type == "percentage":
        discount = purchase_amount * (coupon.discount_value / 100)
        if coupon.max_discount_amount:
            discount = min(discount, coupon.max_discount_amount)
    else:
        discount = min(coupon.discount_value, purchase_amount)
        
    return {
        "valid": True,
        "discount_amount": round(discount, 2),
        "coupon_id": coupon.id
    }
