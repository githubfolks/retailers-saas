from app.core.celery_app import celery_app
from app.core.database import get_task_db
from app.services.sync_service import SyncService
from app.core.logger import request_logger

@celery_app.task(name="app.tasks.sync_odoo_products_task")
def sync_odoo_products_task(tenant_id: str):
    """Background task to sync products from Odoo."""
    with get_task_db() as db:
        try:
            request_logger.info(f"Starting background product sync for tenant: {tenant_id}")
            sync_service = SyncService(db, tenant_id)
            result = sync_service.sync_products()
            request_logger.info(f"Completed background product sync for tenant: {tenant_id}")
            return result
        except Exception as e:
            request_logger.error(f"Background product sync failed for tenant {tenant_id}: {str(e)}")
            return {"status": "error", "message": str(e)}

@celery_app.task(name="app.tasks.sync_odoo_orders_task")
def sync_odoo_orders_task(tenant_id: str):
    """Background task to sync orders from Odoo."""
    with get_task_db() as db:
        try:
            request_logger.info(f"Starting background order sync for tenant: {tenant_id}")
            sync_service = SyncService(db, tenant_id)
            result = sync_service.sync_orders()
            request_logger.info(f"Completed background order sync for tenant: {tenant_id}")
            return result
        except Exception as e:
            request_logger.error(f"Background order sync failed for tenant {tenant_id}: {str(e)}")
            return {"status": "error", "message": str(e)}

@celery_app.task(name="app.tasks.process_bulk_upload_task")
def process_bulk_upload_task(tenant_id: str, file_content: bytes, filename: str):
    """Background task to process bulk product upload."""
    with get_task_db() as db:
        try:
            from app.services.bulk_service import BulkUploadService
            service = BulkUploadService(db, tenant_id)
            result = service.process_bulk_file(file_content, filename)
            return result
        except Exception as e:
            request_logger.error(f"Bulk upload task failed for tenant {tenant_id}: {str(e)}")
            return {"status": "error", "message": str(e)}
