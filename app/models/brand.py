from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    name = Column(String(100), index=True)
    code = Column(String(10), index=True, nullable=True) # e.g., "ADI" for Adidas
    description = Column(Text, nullable=True)
    logo_url = Column(String(255), nullable=True)

    # Relationships
    products = relationship("Product", back_populates="brand_rel")
    skus = relationship("ProductSKU", back_populates="brand_rel")

    def __repr__(self):
        return f"<Brand {self.name}>"
