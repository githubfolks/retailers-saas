from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.core.database import get_db
from app.api.auth import get_current_user, get_current_tenant_id, check_permission
from app.models.shift import Shift
from app.models.order import Order
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/shifts", tags=["shifts"])

class ShiftOpen(BaseModel):
    opening_cash: float
    notes: Optional[str] = None

class ShiftClose(BaseModel):
    closing_cash: float
    notes: Optional[str] = None

@router.get("/", response_model=List[dict])
async def list_shifts(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    user: dict = Depends(check_permission("reports"))
):
    """List all shifts for reporting."""
    shifts = db.query(Shift).filter(Shift.tenant_id == current_tenant_id).order_by(Shift.start_time.desc()).all()
    return shifts

@router.get("/current")
async def get_current_shift(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the active shift for the current user."""
    shift = db.query(Shift).filter(
        Shift.tenant_id == user["tenant_id"],
        Shift.user_id == user["user_id"],
        Shift.status == "open"
    ).first()
    return shift

@router.post("/open")
async def open_shift(
    data: ShiftOpen,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Open a new POS shift."""
    # Check if a shift is already open
    existing = db.query(Shift).filter(
        Shift.tenant_id == user["tenant_id"],
        Shift.user_id == user["user_id"],
        Shift.status == "open"
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="A shift is already open for this user")
        
    new_shift = Shift(
        tenant_id=user["tenant_id"],
        user_id=user["user_id"],
        opening_cash=data.opening_cash,
        expected_cash=data.opening_cash,
        notes=data.notes,
        status="open"
    )
    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)
    return new_shift

@router.post("/close")
async def close_shift(
    data: ShiftClose,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close the current POS shift and reconcile financials."""
    shift = db.query(Shift).filter(
        Shift.tenant_id == user["tenant_id"],
        Shift.user_id == user["user_id"],
        Shift.status == "open"
    ).first()
    
    if not shift:
        raise HTTPException(status_code=404, detail="No open shift found")
        
    # Reconcile sales since shift start
    sales_data = db.query(
        func.sum(Order.total_amount).label("total_sales"),
        func.sum(Order.tax_amount).label("total_tax")
    ).filter(
        Order.tenant_id == user["tenant_id"],
        Order.created_at >= shift.start_time,
        Order.status == "completed"
    ).first()
    
    total_sales = float(sales_data.total_sales or 0.0)
    total_tax = float(sales_data.total_tax or 0.0)
    
    shift.total_sales = total_sales
    shift.total_tax = total_tax
    shift.expected_cash = shift.opening_cash + total_sales
    shift.closing_cash = data.closing_cash
    shift.end_time = datetime.utcnow()
    shift.status = "closed"
    shift.notes = data.notes
    
    db.commit()
    db.refresh(shift)
    return shift

@router.get("/sales-report")
async def staff_sales_report(
    days: int = 1,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    user_payload: dict = Depends(check_permission("reports"))
):
    """Staff-wise sales report."""
    since = datetime.utcnow() - timedelta(days=days)
    
    # We need to join Shift with User to get names
    from app.models.user import User
    
    results = db.query(
        User.name,
        User.email,
        func.sum(Shift.total_sales).label("total_sales"),
        func.count(Shift.id).label("shift_count")
    ).join(Shift, User.id == Shift.user_id).filter(
        Shift.tenant_id == current_tenant_id,
        Shift.end_time >= since
    ).group_by(User.id).all()
    
    return [
        {
            "staff_name": r.name or r.email,
            "total_sales": round(float(r.total_sales or 0.0), 2),
            "shifts": r.shift_count
        } for r in results
    ]
