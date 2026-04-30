import asyncio
import json
from celery import shared_task
from datetime import datetime, timedelta
from app.core.database import get_task_db
from app.models.product import Product
from app.models.inventory import StockLocation, StockAlert, DemandForecast, ReorderSuggestion
from app.models.tenant import Tenant
from app.services.llm_inventory_bot import LLMDemandForecaster, LLMReorderOptimizer
from app.core.logger import request_logger


@shared_task(bind=True, max_retries=3)
def sync_stock_from_odoo(self, tenant_id: str):
    """Sync stock levels from Odoo in real-time."""
    with get_task_db() as db:
        try:
            tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
            if not tenant:
                return {"status": "error", "message": "Tenant not found"}

            from app.integrations.odoo_products import get_all_products
            odoo_products = get_all_products(
                tenant.odoo_url, tenant.odoo_db, tenant.odoo_user, tenant.odoo_password, limit=1000
            )
            if not odoo_products:
                return {"status": "error", "message": "Failed to fetch from Odoo"}

            # Batch-load all products and locations in two queries instead of 2N
            odoo_ids = [p.get("odoo_id") for p in odoo_products if p.get("odoo_id")]
            products_map = {
                p.odoo_id: p for p in db.query(Product).filter(
                    Product.tenant_id == tenant_id,
                    Product.odoo_id.in_(odoo_ids)
                ).all()
            }
            product_ids = [p.id for p in products_map.values()]
            locations_map = {
                loc.product_id: loc for loc in db.query(StockLocation).filter(
                    StockLocation.tenant_id == tenant_id,
                    StockLocation.product_id.in_(product_ids)
                ).all()
            }

            synced = 0
            new_locations = []
            now = datetime.utcnow()
            for odoo_product in odoo_products:
                product = products_map.get(odoo_product.get("odoo_id"))
                if not product:
                    continue

                new_qty = odoo_product.get("quantity", 0)
                location = locations_map.get(product.id)
                if location:
                    if location.quantity != new_qty:
                        location.quantity = new_qty
                        location.last_stock_check = now
                        synced += 1
                else:
                    new_locations.append(StockLocation(
                        tenant_id=tenant_id,
                        product_id=product.id,
                        quantity=new_qty,
                        reorder_point=odoo_product.get("reorder_point", 10),
                        reorder_quantity=odoo_product.get("reorder_qty", 50)
                    ))
                    synced += 1

            if new_locations:
                db.bulk_save_objects(new_locations)
            db.commit()
            request_logger.info(f"Synced {synced} stock levels from Odoo for {tenant_id}")
            return {"status": "success", "synced": synced}

        except Exception as exc:
            request_logger.error(f"Stock sync error: {str(exc)}")
            raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def check_low_stock_alerts(self, tenant_id: str):
    """Check inventory levels and create alerts."""
    with get_task_db() as db:
        try:
            # Single query for all low-stock locations
            low_stock_locs = db.query(StockLocation).filter(
                StockLocation.tenant_id == tenant_id,
                StockLocation.quantity <= StockLocation.reorder_point
            ).all()

            # Fetch all product_ids that already have an active alert (one query)
            alerted_ids = {
                row[0] for row in db.query(StockAlert.product_id).filter(
                    StockAlert.tenant_id == tenant_id,
                    StockAlert.status == "active"
                ).all()
            }

            now = datetime.utcnow()
            new_alerts = []
            for loc in low_stock_locs:
                if loc.product_id in alerted_ids:
                    continue
                new_alerts.append(StockAlert(
                    tenant_id=tenant_id,
                    product_id=loc.product_id,
                    alert_type="out_of_stock" if loc.quantity == 0 else "low_stock",
                    alert_level="critical" if loc.quantity == 0 else "warning",
                    threshold_value=loc.reorder_point,
                    current_value=loc.quantity,
                    status="active",
                    triggered_at=now,
                ))
                alerted_ids.add(loc.product_id)

            if new_alerts:
                db.bulk_save_objects(new_alerts)
            db.commit()

            alerts_created = len(new_alerts)
            request_logger.info(f"Created {alerts_created} stock alerts for {tenant_id}")
            return {"status": "success", "alerts": alerts_created}

        except Exception as exc:
            request_logger.error(f"Alert check error: {str(exc)}")
            raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_pending_notifications(self, tenant_id: str):
    """Send pending inventory notifications via WhatsApp or email based on channel."""
    with get_task_db() as db:
        try:
            from app.models.inventory import InventoryNotification
            from app.integrations.whatsapp_sender import send_whatsapp_message
            from app.integrations.email_sender import send_email

            tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
            if not tenant:
                return

            pending_notifs = db.query(InventoryNotification).filter(
                InventoryNotification.tenant_id == tenant_id,
                InventoryNotification.status == "pending"
            ).limit(10).all()

            sent = 0
            now = datetime.utcnow()
            for notif in pending_notifs:
                if notif.channel == "email":
                    success = send_email(
                        to_email=notif.recipient,
                        subject="Low Stock Alert — Action Required",
                        html_body=notif.message,
                        plain_body=notif.message,
                    )
                else:
                    result = send_whatsapp_message(
                        recipient_number=notif.recipient,
                        message_text=notif.message,
                        phone_number_id=getattr(tenant, 'whatsapp_phone_id', None),
                        whatsapp_token=getattr(tenant, 'whatsapp_token', None)
                    )
                    success = result is not None

                if success:
                    notif.status = "sent"
                    notif.sent_at = now
                    sent += 1
                else:
                    notif.retries += 1
                    if notif.retries > 3:
                        notif.status = "failed"

            db.commit()
            request_logger.info(f"Sent {sent} inventory notifications for {tenant_id}")
            return {"status": "success", "sent": sent}

        except Exception as exc:
            request_logger.error(f"Notification send error: {str(exc)}")
            raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def notify_suppliers_low_stock(self, tenant_id: str):
    """Queue email notifications to suppliers when their products hit low stock."""
    with get_task_db() as db:
        try:
            from app.models.inventory import InventoryNotification, StockAlert
            from app.models.procurement import (
                PurchaseOrder, PurchaseOrderLine, Supplier, SupplierEmailSettings,
            )
            from app.integrations.email_sender import build_low_stock_email

            tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
            if not tenant:
                return {"status": "error", "message": "Tenant not found"}

            email_settings = db.query(SupplierEmailSettings).filter(
                SupplierEmailSettings.tenant_id == tenant_id
            ).first()

            # Respect per-tenant on/off toggle (default enabled if not configured yet)
            if email_settings and not email_settings.is_enabled:
                request_logger.info(f"Supplier email notifications disabled for {tenant_id}")
                return {"status": "skipped", "reason": "notifications disabled"}

            cooldown_hours = email_settings.cooldown_hours if email_settings else 24
            cooldown_cutoff = datetime.utcnow() - timedelta(hours=cooldown_hours)

            # Active alerts that don't already have a pending/sent email notification
            notified_alert_ids = {
                row[0] for row in db.query(InventoryNotification.alert_id).filter(
                    InventoryNotification.tenant_id == tenant_id,
                    InventoryNotification.channel == "email",
                    InventoryNotification.status.in_(["pending", "sent"]),
                    InventoryNotification.alert_id.isnot(None),
                ).all()
            }

            active_alerts = db.query(StockAlert).filter(
                StockAlert.tenant_id == tenant_id,
                StockAlert.status == "active",
                StockAlert.alert_type.in_(["low_stock", "out_of_stock"]),
            ).all()

            queued = 0
            new_notifications = []
            for alert in active_alerts:
                if alert.id in notified_alert_ids:
                    continue

                # Find the most recent supplier with an email for this product
                supplier = (
                    db.query(Supplier)
                    .join(PurchaseOrder, PurchaseOrder.supplier_id == Supplier.id)
                    .join(PurchaseOrderLine, PurchaseOrderLine.po_id == PurchaseOrder.id)
                    .filter(
                        PurchaseOrder.tenant_id == tenant_id,
                        PurchaseOrderLine.product_id == alert.product_id,
                        Supplier.email.isnot(None),
                        Supplier.is_active == True,
                    )
                    .order_by(PurchaseOrder.po_date.desc())
                    .first()
                )

                if not supplier:
                    request_logger.info(
                        f"No supplier with email found for product_id={alert.product_id}, skipping"
                    )
                    continue

                # Cooldown: skip if this supplier already got an email for this product recently
                recent_sent = db.query(InventoryNotification).join(
                    StockAlert, StockAlert.id == InventoryNotification.alert_id
                ).filter(
                    InventoryNotification.tenant_id == tenant_id,
                    InventoryNotification.channel == "email",
                    InventoryNotification.status == "sent",
                    InventoryNotification.recipient == supplier.email,
                    StockAlert.product_id == alert.product_id,
                    InventoryNotification.sent_at > cooldown_cutoff,
                ).first()

                if recent_sent:
                    request_logger.info(
                        f"Cooldown active for supplier {supplier.email} / product_id={alert.product_id}, skipping"
                    )
                    continue

                product = db.query(Product).filter(Product.id == alert.product_id).first()
                product_name = product.name if product else f"Product #{alert.product_id}"

                location = db.query(StockLocation).filter(
                    StockLocation.tenant_id == tenant_id,
                    StockLocation.product_id == alert.product_id,
                ).first()
                reorder_qty = location.reorder_quantity if location else 50

                subject, html_body, plain_body = build_low_stock_email(
                    product_name=product_name,
                    current_qty=alert.current_value,
                    reorder_point=alert.threshold_value,
                    reorder_qty=reorder_qty,
                    tenant_name=tenant.business_name,
                )

                new_notifications.append(InventoryNotification(
                    tenant_id=tenant_id,
                    alert_id=alert.id,
                    recipient=supplier.email,
                    notification_type=alert.alert_type,
                    channel="email",
                    message=html_body,
                    status="pending",
                ))
                queued += 1

            if new_notifications:
                db.bulk_save_objects(new_notifications)
            db.commit()

            request_logger.info(f"Queued {queued} supplier email notifications for {tenant_id}")
            return {"status": "success", "queued": queued}

        except Exception as exc:
            request_logger.error(f"Supplier notification error: {str(exc)}")
            raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_demand_forecasts(self, tenant_id: str):
    """Generate demand forecasts for all products."""
    with get_task_db() as db:
        try:
            products = db.query(Product).filter(Product.tenant_id == tenant_id).all()
            forecaster = LLMDemandForecaster(db, tenant_id)

            # Single event loop for the whole task instead of one per product
            loop = asyncio.new_event_loop()
            forecasts_created = 0
            try:
                for product in products:
                    forecast_result = loop.run_until_complete(
                        forecaster.forecast_demand(product.id, days_ahead=30)
                    )
                    if forecast_result:
                        db.add(DemandForecast(
                            tenant_id=tenant_id,
                            product_id=product.id,
                            forecast_date=datetime.utcnow() + timedelta(days=30),
                            forecast_period="monthly",
                            predicted_demand=forecast_result.get("predicted_demand", 0),
                            confidence_level=forecast_result.get("confidence_level", 0),
                            model_type="llm",
                            lower_bound=forecast_result.get("lower_bound", 0),
                            upper_bound=forecast_result.get("upper_bound", 0)
                        ))
                        forecasts_created += 1
            finally:
                loop.close()

            db.commit()
            request_logger.info(f"Generated {forecasts_created} demand forecasts for {tenant_id}")
            return {"status": "success", "forecasts": forecasts_created}

        except Exception as exc:
            request_logger.error(f"Forecast generation error: {str(exc)}")
            raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_reorder_suggestions(self, tenant_id: str):
    """Generate AI-optimized reorder suggestions."""
    with get_task_db() as db:
        try:
            products = db.query(Product).filter(Product.tenant_id == tenant_id).all()
            optimizer = LLMReorderOptimizer(db, tenant_id)

            # Pre-fetch product_ids that already have a recent pending suggestion (one query)
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            already_suggested = {
                row[0] for row in db.query(ReorderSuggestion.product_id).filter(
                    ReorderSuggestion.tenant_id == tenant_id,
                    ReorderSuggestion.status == "pending",
                    ReorderSuggestion.created_at > recent_cutoff
                ).all()
            }

            loop = asyncio.new_event_loop()
            suggestions_created = 0
            try:
                for product in products:
                    if product.id in already_suggested:
                        continue
                    reorder_result = loop.run_until_complete(optimizer.optimize_reorder(product.id))
                    if reorder_result and reorder_result.get("suggested_quantity", 0) > 0:
                        db.add(ReorderSuggestion(
                            tenant_id=tenant_id,
                            product_id=product.id,
                            suggested_quantity=int(reorder_result.get("suggested_quantity", 50)),
                            reorder_point=10,
                            lead_time_days=7,
                            forecast_demand=reorder_result.get("forecast_demand", 50),
                            rationale=reorder_result.get("rationale", "Optimized order quantity"),
                            ai_confidence=reorder_result.get("ai_confidence", 0),
                            expires_at=datetime.utcnow() + timedelta(days=7)
                        ))
                        suggestions_created += 1
            finally:
                loop.close()

            db.commit()
            request_logger.info(f"Generated {suggestions_created} reorder suggestions for {tenant_id}")
            return {"status": "success", "suggestions": suggestions_created}

        except Exception as exc:
            request_logger.error(f"Reorder suggestion error: {str(exc)}")
            raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_old_movements():
    """Archive old stock movements (older than 1 year)."""
    with get_task_db() as db:
        try:
            from app.models.inventory import StockMovement
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            count = db.query(StockMovement).filter(
                StockMovement.created_at < cutoff_date
            ).delete(synchronize_session=False)
            db.commit()
            request_logger.info(f"Cleaned up {count} old stock movements")
            return {"status": "success", "cleaned": count}

        except Exception as exc:
            request_logger.error(f"Cleanup error: {str(exc)}")


@shared_task
def generate_inventory_report():
    """Generate daily inventory health report."""
    with get_task_db() as db:
        try:
            from app.services.analytics_service import AnalyticsService
            tenants = db.query(Tenant).all()
            for tenant in tenants:
                svc = AnalyticsService(db, tenant.tenant_id)
                valuation = svc.get_inventory_valuation()
                request_logger.info(
                    f"Inventory Report for {tenant.tenant_id}: "
                    f"{json.dumps({'value': valuation['total_inventory_value'], 'products': valuation['product_count']})}"
                )
            return {"status": "success", "tenants_reported": len(tenants)}

        except Exception as exc:
            request_logger.error(f"Report generation error: {str(exc)}")
