from sqlalchemy import text
from app.core.database import SessionLocal
from app.core.logger import request_logger


def create_database_views():
    """Create useful SQL views for reporting."""
    db = SessionLocal()
    
    views = [
        # Inventory snapshot view
        """
        CREATE OR REPLACE VIEW v_inventory_snapshot AS
        SELECT 
            sl.id,
            sl.tenant_id,
            sl.product_id,
            p.name as product_name,
            p.sku,
            p.price,
            sl.warehouse_id,
            sl.quantity,
            sl.reserved_quantity,
            (sl.quantity - sl.reserved_quantity) as available_quantity,
            sl.reorder_point,
            sl.reorder_quantity,
            CASE 
                WHEN sl.quantity = 0 THEN 'out_of_stock'
                WHEN sl.quantity <= sl.reorder_point THEN 'low_stock'
                ELSE 'healthy'
            END as stock_status,
            (p.price * sl.quantity) as inventory_value,
            NOW() as snapshot_date
        FROM stock_locations sl
        JOIN products p ON sl.product_id = p.id;
        """,
        
        # Sales velocity view
        """
        CREATE OR REPLACE VIEW v_sales_velocity AS
        SELECT 
            sm.tenant_id,
            sm.product_id,
            p.name as product_name,
            COUNT(*) as transaction_count,
            SUM(ABS(sm.quantity)) as total_units_moved,
            AVG(ABS(sm.quantity)) as avg_units_per_transaction,
            DATE(sm.created_at) as movement_date,
            CAST(SUM(ABS(sm.quantity)) as FLOAT) / CAST(DATEDIFF(DAY, MIN(sm.created_at), MAX(sm.created_at)) + 1 as FLOAT) as velocity_per_day
        FROM stock_movements sm
        JOIN products p ON sm.product_id = p.id
        WHERE sm.movement_type = 'out'
        GROUP BY sm.tenant_id, sm.product_id, p.name, DATE(sm.created_at);
        """,
        
        # Low stock alerts view
        """
        CREATE OR REPLACE VIEW v_low_stock_alerts AS
        SELECT 
            sl.tenant_id,
            sl.product_id,
            p.name as product_name,
            p.sku,
            sl.quantity as current_stock,
            sl.reorder_point,
            sl.reorder_quantity,
            (sl.reorder_point - sl.quantity) as units_short,
            DATEDIFF(DAY, NOW(), DATE_ADD(NOW(), INTERVAL (sl.reorder_quantity / COALESCE(
                (SELECT CAST(AVG(ABS(quantity)) as FLOAT) FROM stock_movements 
                 WHERE product_id = sl.product_id AND movement_type = 'out' 
                 AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)), 1
            ))) DAY)) as days_until_reorder
        FROM stock_locations sl
        JOIN products p ON sl.product_id = p.id
        WHERE sl.quantity <= sl.reorder_point;
        """,
        
        # Purchase order performance
        """
        CREATE OR REPLACE VIEW v_po_performance AS
        SELECT 
            s.id as supplier_id,
            s.supplier_name,
            COUNT(po.id) as total_pos,
            SUM(CASE WHEN po.po_status = 'received' THEN 1 ELSE 0 END) as completed_pos,
            SUM(CASE WHEN po.actual_delivery <= po.expected_delivery THEN 1 ELSE 0 END) as on_time_deliveries,
            CAST(SUM(CASE WHEN po.actual_delivery <= po.expected_delivery THEN 1 ELSE 0 END) as FLOAT) / 
            CAST(SUM(CASE WHEN po.po_status = 'received' THEN 1 ELSE 0 END) as FLOAT) as on_time_rate,
            AVG(DATEDIFF(DAY, po.po_date, po.actual_delivery)) as avg_lead_time,
            SUM(po.total_amount) as total_spend
        FROM suppliers s
        LEFT JOIN purchase_orders po ON s.id = po.supplier_id
        GROUP BY s.id, s.supplier_name;
        """
    ]
    
    try:
        for view_sql in views:
            db.execute(text(view_sql))
        db.commit()
        request_logger.info("Database views created successfully")
        return True
    
    except Exception as e:
        request_logger.error(f"Error creating views: {str(e)}")
        db.rollback()
        return False
    
    finally:
        db.close()


def create_indexes():
    """Create database indexes for performance."""
    db = SessionLocal()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_stock_location_product ON stock_locations(product_id, tenant_id);",
        "CREATE INDEX IF NOT EXISTS idx_stock_movement_product ON stock_movements(product_id, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_stock_alert_product ON stock_alerts(product_id, status);",
        "CREATE INDEX IF NOT EXISTS idx_demand_forecast_product ON demand_forecasts(product_id, forecast_date);",
        "CREATE INDEX IF NOT EXISTS idx_po_supplier ON purchase_orders(supplier_id, po_status);",
        "CREATE INDEX IF NOT EXISTS idx_fulfillment_order ON order_fulfillments(order_id, fulfillment_status);",
        "CREATE INDEX IF NOT EXISTS idx_barcode_product ON product_barcodes(barcode, product_id);",
    ]
    
    try:
        for index_sql in indexes:
            db.execute(text(index_sql))
        db.commit()
        request_logger.info("Database indexes created successfully")
        return True
    
    except Exception as e:
        request_logger.error(f"Error creating indexes: {str(e)}")
        db.rollback()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    create_database_views()
    create_indexes()
    print("Database optimization completed!")
