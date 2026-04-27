from app.integrations.odoo_base import OdooClient


def authenticate_odoo(
    odoo_url: str,
    odoo_db: str,
    odoo_user: str,
    odoo_password: str
) -> int:
    """Authenticate with Odoo and return uid."""
    client = OdooClient(odoo_url, odoo_db, odoo_user, odoo_password)
    return client.authenticate()


def validate_session(
    odoo_url: str,
    odoo_db: str,
    uid: int,
    odoo_password: str
) -> bool:
    """Validate Odoo session is active."""
    try:
        client = OdooClient(odoo_url, odoo_db, "admin", odoo_password)
        result = client.execute_kw(
            "res.users",
            "search",
            [[["id", "=", uid]]]
        )
        return len(result) > 0
    except Exception:
        return False
