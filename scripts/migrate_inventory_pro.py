import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def migrate():
    conn = psycopg2.connect(
        dbname="app_db",
        user="postgres",
        password="ViKram#2026",
        host="localhost",
        port="5432",
        options="-csearch_path=odoo_saas_retail_db"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    print("🚀 Starting Pro-Inventory & Warehouse Migration...")

    try:
        # 1. Update stock_locations for hierarchy
        print("Updating 'stock_locations' for hierarchy...")
        cur.execute("""
            ALTER TABLE stock_locations 
            ADD COLUMN IF NOT EXISTS parent_id INTEGER REFERENCES stock_locations(id),
            ADD COLUMN IF NOT EXISTS location_type VARCHAR(50) DEFAULT 'internal',
            ADD COLUMN IF NOT EXISTS name VARCHAR(100),
            ADD COLUMN IF NOT EXISTS is_scrap BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
        """)
        # Set default name for existing locations
        cur.execute("UPDATE stock_locations SET name = 'Location-' || id WHERE name IS NULL;")

        # 2. Create valuation tables
        print("Creating valuation and landed cost tables...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stock_valuation_layers (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR(255) REFERENCES tenants(tenant_id),
                product_id INTEGER REFERENCES products(id),
                sku VARCHAR(255),
                original_quantity FLOAT,
                remaining_quantity FLOAT,
                unit_cost FLOAT,
                total_value FLOAT,
                reference_id VARCHAR(255),
                reference_type VARCHAR(50),
                landed_cost_value FLOAT DEFAULT 0.0,
                is_fully_consumed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS landed_costs (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR(255) REFERENCES tenants(tenant_id),
                name VARCHAR(255),
                cost_type VARCHAR(50),
                amount FLOAT,
                status VARCHAR(50) DEFAULT 'draft',
                purchase_order_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                validated_at TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS landed_cost_assignments (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR(255) REFERENCES tenants(tenant_id),
                landed_cost_id INTEGER REFERENCES landed_costs(id),
                valuation_layer_id INTEGER REFERENCES stock_valuation_layers(id),
                allocated_amount FLOAT,
                allocation_method VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Create picking_batches and update fulfillments
        print("Creating picking batches infrastructure...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS picking_batches (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR(255) REFERENCES tenants(tenant_id),
                batch_name VARCHAR(100),
                status VARCHAR(50) DEFAULT 'draft',
                warehouse_id INTEGER REFERENCES warehouses(id),
                picker_id VARCHAR(255),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            ALTER TABLE order_fulfillments 
            ADD COLUMN IF NOT EXISTS batch_id INTEGER REFERENCES picking_batches(id),
            ADD COLUMN IF NOT EXISTS fulfillment_method VARCHAR(50) DEFAULT 'standard';
        """)

        print("✅ Migration completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
