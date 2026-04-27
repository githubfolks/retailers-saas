from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    OWNER = "owner"
    MANAGER = "manager"
    CASHIER = "cashier"
    WAREHOUSE = "warehouse"
    ACCOUNTANT = "accountant"
    STAFF = "staff" # Legacy

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRole.STAFF)
    pin = Column(String(4), nullable=True) # 4-digit PIN for POS login
    
    # Comma-separated list of module permissions: pos,inventory,procurement,reports,settings
    permissions = Column(String, nullable=True)
    
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), nullable=False)
    tenant = relationship("Tenant", backref="users")
