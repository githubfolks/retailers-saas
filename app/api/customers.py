from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.api.auth import get_current_tenant_id
from app.models.customer import Customer
from app.models.order import Order

router = APIRouter(prefix="/customers", tags=["customers"])

class CustomerResponse(BaseModel):
    id: int
    mobile: str
    name: Optional[str]
    email: Optional[str]
    address: Optional[str]
    total_spend: float
    order_count: int
    last_order_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class CustomerDetailResponse(CustomerResponse):
    orders: List[dict] # Simplified order objects

@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None
):
    """List customers for current tenant with search and sorting."""
    query = db.query(Customer).filter(Customer.tenant_id == current_tenant_id)
    
    if search:
        query = query.filter(
            (Customer.mobile.contains(search)) | 
            (Customer.name.contains(search)) | 
            (Customer.email.contains(search))
        )
        
    return query.order_by(Customer.total_spend.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: dict,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Manually add a customer."""
    existing = db.query(Customer).filter(
        Customer.mobile == customer_data.get("mobile"),
        Customer.tenant_id == current_tenant_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Customer already exists")
    
    db_customer = Customer(
        tenant_id=current_tenant_id,
        mobile=customer_data.get("mobile"),
        name=customer_data.get("name"),
        email=customer_data.get("email"),
        address=customer_data.get("address"),
        total_spend=0.0,
        order_count=0
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: dict,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Update customer profile."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == current_tenant_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    for key, value in customer_data.items():
        if hasattr(customer, key) and value is not None:
            setattr(customer, key, value)
            
    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Remove a customer record."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == current_tenant_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    db.delete(customer)
    db.commit()
    return {"status": "deleted"}


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer_details(
    customer_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get detailed customer profile with order history."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == current_tenant_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    orders = db.query(Order).filter(
        Order.customer_id == customer_id,
        Order.tenant_id == current_tenant_id
    ).order_by(Order.created_at.desc()).limit(10).all()
    
    # Map orders to simple dicts for response
    order_list = []
    for o in orders:
        order_list.append({
            "id": o.id,
            "product_name": o.product_name,
            "total_amount": o.total_amount,
            "status": o.status,
            "created_at": o.created_at
        })
        
    response_data = CustomerResponse.from_orm(customer).dict()
    response_data["orders"] = order_list
    
    return response_data
