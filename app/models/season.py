from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Season(Base):
    """Garment seasons (e.g., 'Summer 2024', 'Winter 2025')"""
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    name = Column(String(100), index=True) # e.g., "Summer 2024"
    status = Column(String(20), default="active") # active, finished, archived
    discount_pct = Column(Float, default=0.0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    products = relationship("Product", back_populates="season_rel")
    collections = relationship("Collection", back_populates="season")

class Collection(Base):
    """Specific collections within a season (e.g., 'Essentials', 'Limited Edition')"""
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    name = Column(String(100), index=True)
    
    season = relationship("Season", back_populates="collections")
    products = relationship("Product", back_populates="collection_rel")
