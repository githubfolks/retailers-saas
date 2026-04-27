import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def migrate():
    # Production DB connection (from .env)
    # Using localhost as we are outside the Docker network
    dsn = os.getenv("POSTGRES_URL")
    conn = psycopg2.connect(dsn)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    print("🚀 Starting Sales & Order Management Migration...")

    try:
        # 1. Update orders table
        print("Updating 'orders' table...")
        cur.execute("""
            ALTER TABLE orders 
            ADD COLUMN IF NOT EXISTS unit_cost_at_sale FLOAT,
            ADD COLUMN IF NOT EXISTS discount_amount FLOAT DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS coupon_code VARCHAR(50),
            ADD COLUMN IF NOT EXISTS commitment_date TIMESTAMP,
            ADD COLUMN IF NOT EXISTS effective_delivery_date TIMESTAMP;
        """)

        # 2. Create coupons table
        print("Creating 'coupons' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR(255) REFERENCES tenants(tenant_id),
                code VARCHAR(50) NOT NULL,
                discount_type VARCHAR(20) NOT NULL,
                discount_value FLOAT NOT NULL,
                min_purchase_amount FLOAT DEFAULT 0.0,
                max_discount_amount FLOAT,
                is_active BOOLEAN DEFAULT TRUE,
                valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                valid_until TIMESTAMP,
                usage_limit INTEGER,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 3. Add index for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_coupons_tenant_code ON coupons(tenant_id, code);")

        print("✅ Migration completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
