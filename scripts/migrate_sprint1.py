"""
Sprint 1 migration: add WhatsApp credentials and owner_mobile to tenants table.
Safe to run multiple times (uses IF NOT EXISTS pattern).
"""
from sqlalchemy import text
from app.core.database import get_session


def migrate():
    session = get_session()
    try:
        columns = [
            ("whatsapp_phone_id", "VARCHAR"),
            ("whatsapp_token", "VARCHAR"),
            ("owner_mobile", "VARCHAR"),
        ]
        for col_name, col_type in columns:
            session.execute(text(
                f"ALTER TABLE tenants ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
            ))
            print(f"  Added column: tenants.{col_name}")

        session.commit()
        print("Sprint 1 migration complete.")
    except Exception as e:
        session.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate()
