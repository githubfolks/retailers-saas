import os
import sys
import argparse
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.tenant import Tenant
from app.core.database import get_session


def onboard_tenant(
    tenant_id: str,
    business_name: str,
    whatsapp_number: str,
    razorpay_key: str = "",
    razorpay_secret: str = "",
    n8n_webhook_url: Optional[str] = None
):
    print(f"\n--- Onboarding Tenant: {business_name} ---")

    db = get_session()
    try:
        existing = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if existing:
            print(f"[!] Error: Tenant ID '{tenant_id}' already exists.")
            return False

        new_tenant = Tenant(
            tenant_id=tenant_id,
            business_name=business_name,
            whatsapp_number=whatsapp_number,
            razorpay_key=razorpay_key,
            razorpay_secret=razorpay_secret,
            n8n_webhook_url=n8n_webhook_url,
        )

        db.add(new_tenant)
        db.commit()
        print(f"[+] Tenant '{business_name}' successfully registered.")
        return True
    except Exception as e:
        db.rollback()
        print(f"[!] Database error: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Onboard a new tenant.")
    parser.add_argument("--id", required=True, help="Unique Tenant ID (e.g. store_001)")
    parser.add_argument("--name", required=True, help="Business Name")
    parser.add_argument("--whatsapp", required=True, help="WhatsApp Business Number")
    parser.add_argument("--rzp-key", default="", help="Razorpay Key ID")
    parser.add_argument("--rzp-secret", default="", help="Razorpay Secret")
    parser.add_argument("--n8n-url", default=None, help="n8n Webhook URL")

    args = parser.parse_args()

    success = onboard_tenant(
        tenant_id=args.id,
        business_name=args.name,
        whatsapp_number=args.whatsapp,
        razorpay_key=args.rzp_key,
        razorpay_secret=args.rzp_secret,
        n8n_webhook_url=args.n8n_url,
    )

    sys.exit(0 if success else 1)
