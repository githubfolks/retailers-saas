from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product

class ProductImage(Base):
    """Gallery model for multiple product images"""
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    
    url = Column(String(500)) # External URL (S3/Cloudinary/etc)
    alt_text = Column(String(200), nullable=True)
    is_primary = Column(Boolean, default=False)
    position = Column(Integer, default=0) # For ordering the gallery
    
    product = relationship("Product", back_populates="images")
