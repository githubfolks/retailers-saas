"""
Configuration for Celery beat scheduled tasks for inventory management.
Add to celery_app.py or create separate celery_beat.py file.
"""

from celery.schedules import crontab
from app.core.celery_app import app

# Configure Celery beat schedule
app.conf.beat_schedule = {
    # Sync stock from Odoo every 15 minutes
    'sync-odoo-stock': {
        'task': 'app.tasks.inventory_tasks.sync_stock_from_odoo',
        'schedule': crontab(minute='*/15'),
        'args': ('tenant_id',),  # Will be set per tenant
    },
    
    # Check low stock alerts every hour
    'check-low-stock': {
        'task': 'app.tasks.inventory_tasks.check_low_stock_alerts',
        'schedule': crontab(minute=0),  # Every hour
        'args': ('tenant_id',),
    },
    
    # Send pending notifications every 5 minutes
    'send-notifications': {
        'task': 'app.tasks.inventory_tasks.send_pending_notifications',
        'schedule': crontab(minute='*/5'),
        'args': ('tenant_id',),
    },

    # Queue supplier email alerts for low stock (runs after check-low-stock)
    'notify-suppliers-low-stock': {
        'task': 'app.tasks.inventory_tasks.notify_suppliers_low_stock',
        'schedule': crontab(minute=5),  # 5 min after check-low-stock fires at :00
        'args': ('tenant_id',),
    },
    
    # Generate demand forecasts daily at 2 AM
    'generate-forecasts': {
        'task': 'app.tasks.inventory_tasks.generate_demand_forecasts',
        'schedule': crontab(hour=2, minute=0),
        'args': ('tenant_id',),
    },
    
    # Generate reorder suggestions daily at 3 AM
    'generate-reorders': {
        'task': 'app.tasks.inventory_tasks.generate_reorder_suggestions',
        'schedule': crontab(hour=3, minute=0),
        'args': ('tenant_id',),
    },
    
    # Cleanup old movements weekly
    'cleanup-old-movements': {
        'task': 'app.tasks.inventory_tasks.cleanup_old_movements',
        'schedule': crontab(day_of_week=0, hour=4, minute=0),  # Every Sunday at 4 AM
    },
    
    # Generate inventory report daily at 8 AM
    'generate-report': {
        'task': 'app.tasks.inventory_tasks.generate_inventory_report',
        'schedule': crontab(hour=8, minute=0),
    },
}

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
)


# Dynamic task registration for all tenants
def register_tenant_tasks():
    """Register background tasks for all active tenants."""
    from app.core.database import SessionLocal
    from app.models.tenant import Tenant
    
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        
        for tenant in tenants:
            # Register tasks for each tenant
            from app.tasks.inventory_tasks import (
                sync_stock_from_odoo,
                check_low_stock_alerts,
                send_pending_notifications,
                notify_suppliers_low_stock,
                generate_demand_forecasts,
                generate_reorder_suggestions
            )
            
            # These would typically be triggered via API endpoints
            # or a scheduler that iterates through all tenants
    
    finally:
        db.close()


if __name__ == "__main__":
    register_tenant_tasks()
