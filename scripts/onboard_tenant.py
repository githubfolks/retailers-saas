import os
import sys
import argparse
from typing import Optional

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.tenant import Tenant
from app.core.database import get_session
from app.integrations.odoo_base import OdooClient

def onboard_tenant(
    tenant_id: str,
    business_name: str,
    whatsapp_number: str,
    odoo_url: str,
    odoo_db: str,
    odoo_user: str,
    odoo_password: str,
    razorpay_key: str = "",
    razorpay_secret: str = "",
    n8n_webhook_url: Optional[str] = None
):
    print(f"\n--- Onboarding Tenant: {business_name} ---")
    
    # 1. Validate Odoo Connection
    print(f"[*] Validating Odoo connection at {odoo_url}...")
    odoo_client = OdooClient(odoo_url, odoo_db, odoo_user, odoo_password)
    uid = odoo_client.authenticate()
    
    if not uid:
        print("[!] Error: Could not authenticate with Odoo. Please check credentials and URL.")
        return False
    
    print(f"[+] Odoo authenticated successfully (UID: {uid})")
    
    # 2. Save to Database
    db = get_session()
    try:
        # Check if tenant already exists
        existing = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if existing:
            print(f"[!] Error: Tenant ID '{tenant_id}' already exists.")
            return False
        
        new_tenant = Tenant(
            tenant_id=tenant_id,
            business_name=business_name,
            whatsapp_number=whatsapp_number,
            odoo_url=odoo_url,
            odoo_db=odoo_db,
            odoo_user=odoo_user,
            odoo_password=odoo_password,
            razorpay_key=razorpay_key,
            razorpay_secret=razorpay_secret,
            n8n_webhook_url=n8n_webhook_url
        )
        
        db.add(new_tenant)
        db.commit()
        print(f"[+] Tenant '{business_name}' successfully registered in the portal.")
        return True
    except Exception as e:
        db.rollback()
        print(f"[!] Database error: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Onboard a new SME tenant.")
    parser.add_argument("--id", required=True, help="Unique Tenant ID (e.g. sme_001)")
    parser.add_argument("--name", required=True, help="Business Name")
    parser.add_argument("--whatsapp", required=True, help="WhatsApp Business Number")
    parser.add_argument("--odoo-url", required=True, help="Odoo Instance URL")
    parser.add_argument("--odoo-db", required=True, help="Odoo Database Name")
    parser.add_argument("--odoo-user", required=True, help="Odoo Username/Email")
    parser.add_argument("--odoo-pass", required=True, help="Odoo Password")
    parser.add_argument("--rzp-key", default="", help="Razorpay Key ID")
    parser.add_argument("--rzp-secret", default="", help="Razorpay Secret")
    parser.add_argument("--n8n-url", default=None, help="n8n Webhook URL")

    args = parser.parse_args()
    
    success = onboard_tenant(
        tenant_id=args.id,
        business_name=args.name,
        whatsapp_number=args.whatsapp,
        odoo_url=args.odoo_url,
        odoo_db=args.odoo_db,
        odoo_user=args.odoo_user,
        odoo_password=args.odoo_pass,
        razorpay_key=args.rzp_key,
        razorpay_secret=args.rzp_secret,
        n8n_webhook_url=args.n8n_url
    )
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
