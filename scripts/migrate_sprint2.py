"""
Sprint 2 migration: add COD columns to orders, reorder_suggestion_id to purchase_orders.
Safe to run multiple times (uses IF NOT EXISTS pattern).
"""
from sqlalchemy import text
from app.core.database import get_session


def migrate():
    session = get_session()
    try:
        changes = [
            ("orders", "cod_amount_collected", "FLOAT"),
            ("orders", "cod_collected_at", "TIMESTAMP"),
            ("purchase_orders", "reorder_suggestion_id", "INTEGER"),
        ]
        for table, col_name, col_type in changes:
            session.execute(text(
                f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
            ))
            print(f"  Added column: {table}.{col_name}")

        session.commit()
        print("Sprint 2 migration complete.")
    except Exception as e:
        session.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate()
