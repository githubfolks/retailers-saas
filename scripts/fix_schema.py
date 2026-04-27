import psycopg2
import os

def fix():
    from dotenv import load_dotenv
    load_dotenv()
    dsn = os.getenv("POSTGRES_URL")
    
    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Connected to database on postgres-app")
        
        # 0. Ensure schema exists
        cur.execute("CREATE SCHEMA IF NOT EXISTS odoo_saas_retail_db")
        print("Schema 'odoo_saas_retail_db' ensured")

        
        # 1. Create Categories table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR,
                name VARCHAR,
                code VARCHAR(10),
                description TEXT,
                parent_id INTEGER REFERENCES categories(id)
            )
        """)
        print("Table 'categories' ensured")
        
        # 2. Create Product Images table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_images (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR,
                product_id INTEGER REFERENCES products(id),
                url VARCHAR,
                alt_text VARCHAR,
                is_primary BOOLEAN,
                position INTEGER
            )
        """)
        print("Table 'product_images' ensured")

        # 2b. Create Attributes & Values tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS attributes (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR,
                name VARCHAR(100),
                display_type VARCHAR(50) DEFAULT 'select'
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS attribute_values (
                id SERIAL PRIMARY KEY,
                attribute_id INTEGER REFERENCES attributes(id),
                value VARCHAR(255),
                hex_color VARCHAR(10)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sku_attribute_values (
                sku_id INTEGER REFERENCES product_skus(id),
                value_id INTEGER REFERENCES attribute_values(id),
                PRIMARY KEY (sku_id, value_id)
            )
        """)
        print("Tables 'attributes', 'attribute_values', 'sku_attribute_values' ensured")

        # 2c. Create Seasons & Collections tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS seasons (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR,
                name VARCHAR(100),
                status VARCHAR(20) DEFAULT 'active',
                discount_pct FLOAT DEFAULT 0.0,
                start_date TIMESTAMP,
                end_date TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR,
                season_id INTEGER REFERENCES seasons(id),
                name VARCHAR(100)
            )
        """)
        print("Tables 'seasons' and 'collections' ensured")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shifts (
                id SERIAL PRIMARY KEY,
                tenant_id VARCHAR,
                user_id INTEGER REFERENCES users(id),
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                opening_cash FLOAT DEFAULT 0.0,
                closing_cash FLOAT,
                total_sales FLOAT DEFAULT 0.0,
                total_returns FLOAT DEFAULT 0.0,
                total_tax FLOAT DEFAULT 0.0,
                expected_cash FLOAT DEFAULT 0.0,
                status VARCHAR(20) DEFAULT 'open',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Table 'shifts' ensured")
        try:
            cur.execute("ALTER TABLE categories ADD COLUMN code VARCHAR(10)")
            cur.execute("CREATE INDEX idx_categories_code ON categories(code)")
            print("Added code to categories")
        except Exception as e:
            print(f"Skipped categories.code: {e}")

        # 4. Add columns to products
        try:
            cur.execute("ALTER TABLE products ADD COLUMN category_id INTEGER REFERENCES categories(id)")
            print("Added category_id to products")
        except Exception as e:
            print(f"Skipped products.category_id: {e}")

        try:
            cur.execute("ALTER TABLE seasons ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
            cur.execute("ALTER TABLE seasons ADD COLUMN discount_pct FLOAT DEFAULT 0.0")
            print("Added status and discount_pct to seasons")
        except Exception as e:
            print(f"Skipped seasons.status/discount: {e}")

        try:
            cur.execute("ALTER TABLE products ADD COLUMN season_id INTEGER REFERENCES seasons(id)")
            cur.execute("ALTER TABLE products ADD COLUMN collection_id INTEGER REFERENCES collections(id)")
            print("Added season_id and collection_id to products")
        except Exception as e:
            print(f"Skipped products.season/collection: {e}")
            
        # 4. Add columns to product_skus
        try:
            cur.execute("ALTER TABLE product_skus ADD COLUMN category_id INTEGER REFERENCES categories(id)")
            print("Added category_id to product_skus")
        except Exception as e:
            print(f"Skipped product_skus.category_id: {e}")

        try:
            cur.execute("ALTER TABLE product_skus ADD COLUMN hsn_code VARCHAR(10)")
            print("Added hsn_code to product_skus")
        except Exception as e:
            print(f"Skipped product_skus.hsn_code: {e}")
            
        try:
            cur.execute("ALTER TABLE product_skus ADD COLUMN seasonal_price FLOAT")
            print("Added seasonal_price to product_skus")
        except Exception: pass
        try:
            cur.execute("ALTER TABLE product_skus ADD COLUMN seasonal_discount_pct FLOAT DEFAULT 0.0")
            print("Added seasonal_discount_pct to product_skus")
        except Exception: pass
        try:
            cur.execute("ALTER TABLE product_skus ADD COLUMN season_id INTEGER REFERENCES seasons(id)")
            print("Added season_id to product_skus")
        except Exception: pass
        try:
            cur.execute("ALTER TABLE product_skus ADD COLUMN collection_id INTEGER REFERENCES collections(id)")
            print("Added collection_id to product_skus")
        except Exception: pass
            
        try:
            cur.execute("ALTER TABLE conversation_states ADD COLUMN current_state VARCHAR(50) DEFAULT 'IDLE'")
            cur.execute("ALTER TABLE conversation_states ADD COLUMN selected_product_id INTEGER")
            cur.execute("ALTER TABLE conversation_states ADD COLUMN selected_sku VARCHAR(255)")
            cur.execute("ALTER TABLE conversation_states ADD COLUMN context JSONB DEFAULT '{}'")
            cur.execute("ALTER TABLE conversation_states ADD COLUMN last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            cur.execute("ALTER TABLE conversation_states ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("Upgraded conversation_states for WhatsApp Bot")
        except Exception: pass

        try:
            cur.execute("ALTER TABLE users ADD COLUMN name VARCHAR(255)")
            cur.execute("ALTER TABLE users ADD COLUMN pin VARCHAR(4)")
            cur.execute("ALTER TABLE users ADD COLUMN permissions TEXT")
            print("Added name, pin, permissions to users")
        except Exception as e:
            print(f"Skipped users columns: {e}")

        try:
            cur.execute("ALTER TABLE stock_locations ADD COLUMN is_clearance BOOLEAN DEFAULT FALSE")
            print("Added is_clearance to stock_locations")
        except Exception as e:
            print(f"Skipped stock_locations is_clearance: {e}")

        # 5. Updated missing primary_color for tenants
        try:
            cur.execute("UPDATE tenants SET primary_color = '#0d9488' WHERE primary_color IS NULL")
            print("Updated missing primary_color for tenants")
        except Exception as e:
            print(f"Skipped tenants.primary_color update: {e}")

        # 6. Populate missing order fields
        try:
            cur.execute("ALTER TABLE orders ADD COLUMN notes TEXT")
            cur.execute("UPDATE orders SET discount_amount = 0.0 WHERE discount_amount IS NULL")
            cur.execute("UPDATE orders SET unit_cost_at_sale = 0.0 WHERE unit_cost_at_sale IS NULL")
            print("Updated missing discount_amount, unit_cost, and notes for orders")
        except Exception as e:
            print(f"Skipped orders update: {e}")

        # Add missing GST columns to orders
        for col, col_type in [
            ('gst_rate', 'DOUBLE PRECISION'),
            ('cgst_amount', 'DOUBLE PRECISION'),
            ('sgst_amount', 'DOUBLE PRECISION'),
            ('igst_amount', 'DOUBLE PRECISION'),
            ('customer_gstin', 'VARCHAR(15)'),
            ('hsn_code', 'VARCHAR(10)')
        ]:
            try:
                cur.execute(f"ALTER TABLE orders ADD COLUMN {col} {col_type}")
                print(f"Added {col} to orders")
            except Exception as e:
                print(f"Skipped orders.{col}: {e}")

        # 7. Populate missing warehouse fields
        try:
            cur.execute("UPDATE warehouses SET location_address = 'Default Address' WHERE location_address IS NULL")
            print("Updated missing location_address for warehouses")
        except Exception as e:
            print(f"Skipped warehouses update: {e}")

        cur.close()
        conn.close()
        print("Schema fix completed")
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    fix()
