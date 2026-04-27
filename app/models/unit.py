from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Unit(Base):
    """Unit of Measure (e.g., Kilogram, Piece, Literal)"""
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    name = Column(String(50), index=True) # e.g., "Kilogram"
    abbreviation = Column(String(10), index=True) # e.g., "kg"

    # Relationships
    products = relationship("Product", back_populates="unit_rel")
    skus = relationship("ProductSKU", back_populates="unit_rel")

    def __repr__(self):
        return f"<Unit {self.abbreviation}>"
