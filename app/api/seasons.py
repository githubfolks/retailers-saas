from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_write_permission
from app.models.season import Season, Collection
from app.services.season_service import SeasonService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/seasons", tags=["seasons"], dependencies=[Depends(check_write_permission("inventory"))])

class SeasonCreate(BaseModel):
    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CollectionCreate(BaseModel):
    name: str
    season_id: int

@router.get("/")
async def list_seasons(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """List all seasons for the current tenant."""
    return db.query(Season).filter(Season.tenant_id == current_tenant_id).all()

@router.post("/")
async def create_season(
    season_data: SeasonCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new season."""
    new_season = Season(
        tenant_id=current_tenant_id,
        name=season_data.name,
        start_date=season_data.start_date,
        end_date=season_data.end_date
    )
    db.add(new_season)
    db.commit()
    db.refresh(new_season)
    return new_season

@router.post("/{id}/apply-discount")
async def apply_discount(
    id: int,
    discount_pct: float,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Apply an end-of-season markdown."""
    service = SeasonService(db, current_tenant_id)
    result = service.apply_seasonal_discount(id, discount_pct)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.post("/{id}/close")
async def close_season(
    id: int,
    clearance_location_id: Optional[int] = None,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Close a season and move unsold stock to clearance."""
    # If no location ID provided, we'll let the service create/find one
    service = SeasonService(db, current_tenant_id)
    # Note: I'll modify the service slightly to handle None location_id by looking for ANY is_clearance=True location
    
    # Actually, let's just use 0 as a flag or find one here
    from app.models.inventory import StockLocation
    if not clearance_location_id:
        loc = db.query(StockLocation).filter(
            StockLocation.tenant_id == current_tenant_id,
            StockLocation.is_clearance == True
        ).first()
        if loc:
            clearance_location_id = loc.id
        else:
            # Service will handle creating one if we pass a special ID or similar
            # For now, let's just pass 0 if none found
            clearance_location_id = 0 

    result = service.close_season(id, clearance_location_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.get("/{id}/collections")
async def list_collections(
    id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """List collections in a season."""
    return db.query(Collection).filter(
        Collection.season_id == id,
        Collection.tenant_id == current_tenant_id
    ).all()

@router.post("/collections")
async def create_collection(
    coll_data: CollectionCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new collection."""
    new_coll = Collection(
        tenant_id=current_tenant_id,
        season_id=coll_data.season_id,
        name=coll_data.name
    )
    db.add(new_coll)
    db.commit()
    db.refresh(new_coll)
    return new_coll
