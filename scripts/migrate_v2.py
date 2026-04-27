from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    # Attempt to use the same engine logic as the app
    db_url = settings.postgres_url
    if db_url.startswith('postgresql://'):
        # Try without +psycopg first in case environment uses psycopg2
        pass 
    
    # Let's try to find which driver and host is available
    base_urls = [
        settings.postgres_url,
        settings.postgres_url.replace('@postgres:', '@localhost:')
    ]
    drivers = ['postgresql+psycopg2://', 'postgresql+psycopg://', 'postgresql://']
    engine = None
    
    for base_url in base_urls:
        for driver in drivers:
            try:
                url = base_url.replace('postgresql://', driver, 1)
                engine = create_engine(url, connect_args={'connect_timeout': 2})
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                print(f"Success with {driver} on {url.split('@')[1]}")
                break
            except Exception:
                continue
        if engine:
            break
            
    if not engine:
        print("Failed to connect with any driver")
        return

    with engine.connect() as conn:
        # 1. Create new tables
        from app.models.category import Category
        from app.models.image import ProductImage
        from app.core.database import Base
        Base.metadata.create_all(bind=engine)
        print("New tables created (if missing)")

        # 2. Add missing columns to existing tables
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN category_id INTEGER REFERENCES categories(id)"))
            print("Added category_id to products")
        except Exception as e:
            print(f"Could not add category_id to products (might already exist): {e}")

        try:
            conn.execute(text("ALTER TABLE product_skus ADD COLUMN category_id INTEGER REFERENCES categories(id)"))
            print("Added category_id to product_skus")
        except Exception as e:
            print(f"Could not add category_id to product_skus (might already exist): {e}")
            
        conn.commit()

if __name__ == "__main__":
    migrate()
