import psycopg2
from app.core.config import settings

def check_schema():
    dsn = settings.postgres_url.replace('postgres-app', 'localhost')
    if dsn.startswith('postgresql://'):
        dsn = dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
    
    # We need the underlying dsn for psycopg2 if we use it, 
    # but let's use psycopg2's own dsn format if possible or just use the connection string.
    # Actually app.core.database uses sqlalchemy.
    
    from sqlalchemy import create_engine, inspect
    engine = create_engine(dsn)
    inspector = inspect(engine)
    
    tables = ['products', 'product_images', 'product_skus', 'orders', 'categories', 'brands', 'units']
    
    for table in tables:
        print(f"\n--- Table: {table} ---")
        found = False
        for schema in ['public', 'odoo_saas_retail_db']:
            if table in inspector.get_table_names(schema=schema):
                print(f"  Schema: {schema}")
                columns = inspector.get_columns(table, schema=schema)
                for col in columns:
                    print(f"    {col['name']}: {col['type']}")
                found = True
        if not found:
            print(f"  Table '{table}' NOT FOUND in any schema")

if __name__ == "__main__":
    check_schema()
