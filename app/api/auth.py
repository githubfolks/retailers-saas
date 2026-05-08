from fastapi import APIRouter, HTTPException, Depends, Header, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from datetime import datetime, timedelta
from typing import Optional
import jwt
import uuid
from passlib.context import CryptContext
from app.core.config import settings
from app.core.logger import request_logger
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

# Types
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    business_name: str
    email: EmailStr
    password: str

class SignupResponse(BaseModel):
    status: str
    message: str
    tenant_id: str

class POSLoginRequest(BaseModel):
    email: EmailStr
    pin: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    tenant_id: str
    role: str
    name: Optional[str] = None
    permissions: Optional[str] = None

# Helpers
def create_access_token(
    user_id: int,
    tenant_id: str,
    role: str,
    permissions: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token with user payload."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "role": str(role),
        "permissions": permissions,
        "exp": expire
    }
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except Exception:
        return None

# Dependencies
def get_current_user(authorization: str = Header(None)) -> dict:
    """Dependency for protected routes returning user payload."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

def get_current_tenant_id(user: dict = Depends(get_current_user)) -> str:
    return user["tenant_id"]

def check_owner(user: dict = Depends(get_current_user)):
    """Dependency to ensure the user is an OWNER."""
    if user["role"] != UserRole.OWNER:
        request_logger.warning(f"Unauthorized access attempt by {user['role']} to owner resource")
        raise HTTPException(status_code=403, detail="Only the Merchant Owner can perform this action")
    return user

def check_permission(required_module: str):
    """Dependency to check granular module permissions."""
    def permission_dependency(user: dict = Depends(get_current_user)):
        role = user.get("role")
        permissions = user.get("permissions") or ""

        # Owner has all permissions
        if role == UserRole.OWNER:
            return user

        # Check specific module permission
        if required_module in permissions.split(","):
            return user

        request_logger.warning(f"Access denied for {role} to module: {required_module}")
        raise HTTPException(
            status_code=403,
            detail=f"You do not have permission to access the {required_module} module"
        )
    return permission_dependency

def check_plan_module(required_module: str):
    """Block access if the tenant's subscription plan does not include this module."""
    from app.core.database import get_db
    from sqlalchemy.orm import Session

    def _dep(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
        from app.services.subscription_service import SubscriptionService
        svc = SubscriptionService(db, user["tenant_id"])
        sub = svc.get_or_create()
        if not svc.can_access_module(sub, required_module):
            raise HTTPException(
                status_code=402,
                detail=f"The '{required_module}' module requires a higher plan. Current plan: {sub.plan}",
            )
        return user
    return _dep

def check_write_permission(required_module: str):
    """Allow GET/HEAD to any authenticated user; restrict mutating methods to module permission."""
    def _dep(request: Request, user: dict = Depends(get_current_user)):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            role = user.get("role")
            permissions = user.get("permissions") or ""
            if role != UserRole.OWNER and required_module not in permissions.split(","):
                request_logger.warning(f"Access denied for {role} writing to {required_module}")
                raise HTTPException(
                    status_code=403,
                    detail=f"You do not have permission to modify {required_module} data"
                )
        return user
    return _dep

# Endpoints
@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """Verifies credentials and returns JWT with role."""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not pwd_context.verify(login_data.password, user.hashed_password):
        request_logger.warning(f"Failed login attempt for email: {login_data.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    request_logger.info(f"Login successful for user: {user.email}")
    access_token = create_access_token(user.id, user.tenant_id, user.role, user.permissions)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "tenant_id": user.tenant_id,
        "role": user.role,
        "name": user.name,
        "permissions": user.permissions
    }

@router.post("/pos-login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def pos_login(request: Request, login_data: POSLoginRequest, db: Session = Depends(get_db)):
    """Quick switch login using PIN for POS terminals."""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or user.pin != login_data.pin:
        request_logger.warning(f"Failed POS login attempt for email: {login_data.email}")
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    request_logger.info(f"POS Login successful for user: {user.email}")
    access_token = create_access_token(user.id, user.tenant_id, user.role, user.permissions)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "tenant_id": user.tenant_id,
        "role": user.role,
        "name": user.name,
        "permissions": user.permissions
    }

@router.post("/signup", response_model=SignupResponse)
async def signup(signup_data: SignupRequest, db: Session = Depends(get_db)):
    """Automated Tenant Onboarding."""
    try:
        if db.query(User).filter(User.email == signup_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        tenant_id = signup_data.business_name.lower().replace(" ", "-")
        original_id = tenant_id
        counter = 1
        while db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first():
            tenant_id = f"{original_id}-{counter}"
            counter += 1
            
        new_tenant = Tenant(tenant_id=tenant_id, business_name=signup_data.business_name)
        db.add(new_tenant)
        
        new_user = User(
            email=signup_data.email,
            hashed_password=pwd_context.hash(signup_data.password),
            role=UserRole.OWNER,
            tenant_id=tenant_id
        )
        db.add(new_user)
        db.commit()

        # Start 14-day free trial automatically
        from app.services.subscription_service import SubscriptionService
        SubscriptionService(db, tenant_id).get_or_create()

        request_logger.info(f"New merchant: {signup_data.business_name} (ID: {tenant_id})")
        return {"status": "success", "message": "Business registered successfully", "tenant_id": tenant_id}
        
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        request_logger.error(f"Onboarding error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(user: dict = Depends(get_current_user)):
    """Refresh session token with current user context."""
    new_token = create_access_token(user["user_id"], user["tenant_id"], user["role"])
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "tenant_id": user["tenant_id"],
        "role": user["role"]
    }

@router.post("/verify")
async def verify(current_tenant_id: str = Depends(get_current_tenant_id)):
    return {"status": "valid", "tenant_id": current_tenant_id}

@router.post("/logout")
async def logout(current_tenant_id: str = Depends(get_current_tenant_id)):
    request_logger.info(f"Logout for tenant: {current_tenant_id}")
    return {"status": "logged_out", "message": "Successfully logged out"}
