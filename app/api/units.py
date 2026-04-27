from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.auth import get_current_tenant_id
from app.models.unit import Unit

router = APIRouter(prefix="/units", tags=["units"])

class UnitBase(BaseModel):
    name: str
    abbreviation: str

class UnitCreate(UnitBase):
    pass

class UnitUpdate(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None

class UnitResponse(UnitBase):
    id: int
    tenant_id: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UnitResponse])
async def list_units(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    return db.query(Unit).filter(Unit.tenant_id == current_tenant_id).all()

@router.post("/", response_model=UnitResponse)
async def create_unit(
    unit: UnitCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    db_unit = Unit(
        tenant_id=current_tenant_id,
        name=unit.name,
        abbreviation=unit.abbreviation
    )
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

@router.put("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_update: UnitUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    db_unit = db.query(Unit).filter(
        Unit.id == unit_id,
        Unit.tenant_id == current_tenant_id
    ).first()
    
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    update_data = unit_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_unit, key, value)
    
    db.commit()
    db.refresh(db_unit)
    return db_unit

@router.delete("/{unit_id}")
async def delete_unit(
    unit_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    db_unit = db.query(Unit).filter(
        Unit.id == unit_id,
        Unit.tenant_id == current_tenant_id
    ).first()
    
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    db.delete(db_unit)
    db.commit()
    return {"status": "success", "message": "Unit deleted"}
