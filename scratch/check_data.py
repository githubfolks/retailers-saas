import psycopg2
import sys

def check_data():
    dsn = "postgresql://postgres:ViKram#2026@localhost:5432/app_db"
    try:
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');")
        schemas = [s[0] for s in cur.fetchall() if not s[0].startswith('pg_')]
        
        for schema in schemas:
            print(f"\n--- Checking Schema: {schema} ---")
            cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}';")
            tables = cur.fetchall()
            
            if not tables:
                print(f"No tables found in schema {schema}")
                continue
                
            for (table_name,) in tables:
                try:
                    cur.execute(f'SELECT count(*) FROM "{schema}"."{table_name}"')
                    count = cur.fetchone()[0]
                    if count > 0:
                        print(f"Table {table_name}: {count} rows")
                except Exception as e:
                    # print(f"Could not check {table_name} in {schema}: {e}")
                    conn.rollback()
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_data()
