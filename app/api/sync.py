from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_tenant_id
from app.tasks import sync_odoo_products_task, sync_odoo_orders_task
from app.core.logger import request_logger

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/products")
async def sync_all_products(
    current_tenant_id: str = Depends(get_current_tenant_id),
):
    """Trigger a background product sync from Odoo."""
    task = sync_odoo_products_task.delay(current_tenant_id)
    return {
        "status": "pending",
        "task_id": task.id,
        "message": "Product sync started in background"
    }

@router.post("/orders")
async def sync_all_orders(
    current_tenant_id: str = Depends(get_current_tenant_id),
):
    """Trigger a background order sync from Odoo."""
    task = sync_odoo_orders_task.delay(current_tenant_id)
    return {
        "status": "pending",
        "task_id": task.id,
        "message": "Order sync started in background"
    }
