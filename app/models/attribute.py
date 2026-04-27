from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

# Many-to-Many link between SKUs and their specific attribute values
sku_attribute_link = Table(
    'sku_attribute_values',
    Base.metadata,
    Column('sku_id', Integer, ForeignKey('product_skus.id'), primary_key=True),
    Column('value_id', Integer, ForeignKey('attribute_values.id'), primary_key=True)
)

class Attribute(Base):
    """Defines a product attribute type (e.g., 'Size', 'Color', 'Material')"""
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    name = Column(String(100), index=True) # e.g., "Color"
    display_type = Column(String(50), default="select") # select, radio, color_picker
    
    values = relationship("AttributeValue", back_populates="attribute", cascade="all, delete-orphan")

class AttributeValue(Base):
    """Specific values for an attribute (e.g., 'Red', 'XL', 'Cotton')"""
    __tablename__ = "attribute_values"

    id = Column(Integer, primary_key=True, index=True)
    attribute_id = Column(Integer, ForeignKey("attributes.id"), index=True)
    value = Column(String(255), index=True) # e.g., "Red"
    hex_color = Column(String(10), nullable=True) # Optional for color pickers
    
    attribute = relationship("Attribute", back_populates="values")
    skus = relationship("ProductSKU", secondary=sku_attribute_link, back_populates="attribute_values")
