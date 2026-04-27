from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.image import ProductImage
    from app.models.brand import Brand
    from app.models.unit import Unit
    from app.models.season import Season, Collection


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    sku = Column(String, index=True)
    quantity = Column(Integer, default=0)
    odoo_id = Column(Integer, nullable=True)
    
    # New relationships
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True)
    
    category_rel = relationship("Category", back_populates="products")
    brand_rel = relationship("Brand", back_populates="products")
    unit_rel = relationship("Unit", back_populates="products")
    season_rel = relationship("Season", back_populates="products")
    collection_rel = relationship("Collection", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductSKU", back_populates="product_template", cascade="all, delete-orphan")
