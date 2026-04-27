from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.sku import ProductSKU

class Category(Base):
    """Hierarchical category system (e.g., Electronics > Mobile > Android)"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    name = Column(String(100), index=True)
    code = Column(String(10), index=True, nullable=True) # e.g., "TSH" for T-Shirt
    description = Column(Text, nullable=True)
    
    # Parent-child relationship
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category_rel")
    skus = relationship("ProductSKU", back_populates="category_rel")
    
    def __repr__(self):
        return f"<Category {self.name}>"
