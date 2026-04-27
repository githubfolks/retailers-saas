import sys
import os

# Add the project root to sys.path
sys.path.append('/Users/vikram/workspace/odoo-saas')

import traceback
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.analytics_service import AnalyticsService

def test_debug():
    db = SessionLocal()
    tenant_id = "acme-corp"
    try:
        service = AnalyticsService(db, tenant_id)
        print("Executing get_inventory_report...")
        report = service.get_inventory_report()
        print("Success!")
    except Exception as e:
        print("\n--- ERROR DETECTED ---")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_debug()
