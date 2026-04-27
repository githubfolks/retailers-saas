from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.api.auth import get_current_tenant_id
from app.services.return_service import ReturnService
from app.models.return_refund import OrderReturn, Refund

router = APIRouter(prefix="/returns", tags=["returns"])

class ReturnRequest(BaseModel):
    order_id: int
    quantity: int
    reason: str
    condition: str = "resellable"

class RefundRequest(BaseModel):
    return_id: int
    amount: Optional[float] = None

@router.post("/")
async def create_return(
    req: ReturnRequest,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Initiate a produce return."""
    try:
        service = ReturnService(db, current_tenant_id)
        result = service.process_return(
            req.order_id, req.quantity, req.reason, req.condition
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refund")
async def process_refund(
    req: RefundRequest,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Process financial refund for a return."""
    try:
        service = ReturnService(db, current_tenant_id)
        result = service.process_refund(req.return_id, req.amount)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
async def list_returns(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """List all returns for tenant."""
    returns = db.query(OrderReturn).filter(
        OrderReturn.tenant_id == current_tenant_id
    ).order_by(OrderReturn.return_date.desc()).all()
    
    return returns
