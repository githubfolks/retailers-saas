from sqlalchemy import text
from app.core.database import get_session
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.api.auth import pwd_context

def migrate():
    session = get_session()
    try:
        # 1. Fetch tenants
        tenants = session.query(Tenant).all()
        print(f"Found {len(tenants)} tenants to migrate.")
        
        for t in tenants:
            email = f"admin@{t.tenant_id}.com"
            
            # Check if user already exists
            exists = session.query(User).filter(User.email == email).first()
            if exists:
                print(f"Skipping {t.tenant_id} (User already exists)")
                continue
                
            # Use odoo_password as the migration password
            hashed_password = pwd_context.hash(t.odoo_password)
            
            # 2. Create Owner User
            new_user = User(
                email=email,
                hashed_password=hashed_password,
                role=UserRole.OWNER,
                tenant_id=t.tenant_id
            )
            session.add(new_user)
            print(f"Migrated {t.tenant_id} -> {email}")
            
        session.commit()
        print("Migration complete.")
    except Exception as e:
        session.rollback()
        print(f"Migration failed: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    migrate()
