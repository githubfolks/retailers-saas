import sys
import os
from sqlalchemy import text

# Add the app directory to the path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal

def seed_data():
    print("Seeding database with products and orders...")
    
    sql_file_path = os.path.join(os.path.dirname(__file__), 'seed_data.sql')
    
    if not os.path.exists(sql_file_path):
        print(f"Error: SQL file not found at {sql_file_path}")
        sys.exit(1)
    
    try:
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        db = SessionLocal()
        try:
            for statement in statements:
                print(f"Executing: {statement[:50]}...")
                db.execute(text(statement))
            
            db.commit()
            print("Successfully seeded products and orders!")
        except Exception as e:
            print(f"Error executing SQL: {e}")
            db.rollback()
            sys.exit(1)
        finally:
            db.close()
            
    except Exception as e:
        print(f"File Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    seed_data()
