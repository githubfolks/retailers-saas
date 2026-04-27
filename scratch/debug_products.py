
import os
import sys

# Add app to path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.products import list_products, ProductResponse
from app.models.product import Product
from app.core.database import Base
from pydantic import TypeAdapter
from typing import List

# Mock DB
engine = create_engine("postgresql://postgres:ViKram#2026@localhost:5432/app_db?options=-csearch_path%3Dodoo_saas_retail_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    tenant_id = "acme-corp"
    # Try to fetch and validate
    products = db.query(Product).filter(Product.tenant_id == tenant_id).all()
    print(f"Found {len(products)} products")
    
    adapter = TypeAdapter(List[ProductResponse])
    validated = adapter.validate_python(products)
    print("Validation successful")
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
