import sys
import os
from sqlalchemy import text

# Add the app directory to the path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal

def sync_garments():
    print("🚀 Initializing Garment Vertical Sync for 'Thread & Trend'...")
    
    sql_file_path = os.path.join(os.path.dirname(__file__), 'seed_garments.sql')
    
    if not os.path.exists(sql_file_path):
        print(f"❌ Error: SQL file not found at {sql_file_path}")
        sys.exit(1)
    
    try:
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        # Split by semicolon to execute individual statements
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        db = SessionLocal()
        try:
            # First, clean up any existing data for this tenant to ensure a clean sync
            print("🧹 Cleaning existing demo data for 'thread-trend'...")
            db.execute(text("DELETE FROM orders WHERE tenant_id = 'thread-trend'"))
            db.execute(text("DELETE FROM products WHERE tenant_id = 'thread-trend'"))
            db.execute(text("DELETE FROM tenants WHERE tenant_id = 'thread-trend'"))
            
            for statement in statements:
                print(f"📥 Syncing: {statement[:60]}...")
                db.execute(text(statement))
            
            db.commit()
            print("\n✅ Garment Sync Complete!")
            print("Brand: Thread & Trend Garments")
            print("Products: 5 | Orders: 5 | Status: ACTIVE")
        except Exception as e:
            print(f"❌ Error executing sync SQL: {e}")
            db.rollback()
            sys.exit(1)
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ File System Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_garments()
