import psycopg2
import os

def run_sql_file(cur, file_path):
    print(f"Executing {file_path}...")
    with open(file_path, 'r') as f:
        sql = f.read()
        cur.execute(sql)

def populate():
    dsn = {
        "dbname": "app_db",
        "user": "postgres",
        "password": "ViKram#2026",
        "host": "localhost",
        "port": "5432",
        "options": "-csearch_path=odoo_saas_retail_db"
    }
    
    try:
        conn = psycopg2.connect(**dsn)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Clear existing sample data to avoid conflicts if re-run
        # (Though we might want to keep some, usually seeding works best on clean start)
        # cur.execute("TRUNCATE tenants, products, orders CASCADE;")
        
        files = [
            'scripts/seed_tenants.sql',
            'scripts/seed_data.sql',
            'scripts/seed_garments.sql'
        ]
        
        for f in files:
            if os.path.exists(f):
                run_sql_file(cur, f)
            else:
                print(f"Warning: {f} not found")
        
        cur.close()
        conn.close()
        print("✅ Data population completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    populate()
