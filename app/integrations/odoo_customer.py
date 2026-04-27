from typing import Optional, Dict, Any
from app.integrations.odoo_base import OdooClient
from app.core.logger import request_logger


def create_customer(
    name: str,
    email: str,
    phone: str,
    address: Optional[str] = None,
    odoo_url: str = None,
    odoo_db: str = None,
    odoo_user: str = None,
    odoo_password: str = None
) -> Optional[Dict[str, Any]]:
    try:
        client = OdooClient(odoo_url, odoo_db, odoo_user, odoo_password)
        
        if not client.authenticate():
            request_logger.error("Odoo authentication failed")
            return None
        
        customer_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "type": "contact",
        }
        
        if address:
            customer_data["street"] = address
        
        customer_id = client.execute_kw(
            "res.partner",
            "create",
            [customer_data]
        )
        
        if not customer_id:
            return None
        
        customer = client.execute_kw(
            "res.partner",
            "read",
            [customer_id],
            {"fields": ["id", "name", "email", "phone", "street"]}
        )
        
        if customer:
            return {
                "id": customer[0].get("id"),
                "name": customer[0].get("name"),
                "email": customer[0].get("email"),
                "phone": customer[0].get("phone"),
                "address": customer[0].get("street"),
            }
        
        return None
    
    except Exception as e:
        request_logger.error(f"Error creating customer in Odoo: {str(e)}")
        return None
