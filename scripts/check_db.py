from app.core.database import engine, Base
from sqlalchemy import text, inspect

def check_schema():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Current tables: {tables}")
    
    for table in ['products', 'product_skus']:
        if table in tables:
            columns = [c['name'] for c in inspector.get_columns(table)]
            print(f"Columns for {table}: {columns}")

if __name__ == "__main__":
    check_schema()
