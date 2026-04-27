from typing import Optional, Dict, Any, List
from app.integrations.odoo_base import OdooClient
from app.core.logger import request_logger


def create_sale_order(
    customer_id: int,
    order_lines: List[Dict[str, Any]],
    odoo_url: str,
    odoo_db: str,
    odoo_user: str,
    odoo_password: str
) -> Optional[Dict[str, Any]]:
    """
    Create a sale order in Odoo.
    
    order_lines format:
    [
        {
            "product_id": 1,
            "quantity": 2,
            "price_unit": 100.0
        },
        ...
    ]
    """
    try:
        client = OdooClient(odoo_url, odoo_db, odoo_user, odoo_password)
        
        if not client.authenticate():
            request_logger.error("Odoo authentication failed")
            return None
        
        sale_order_data = {
            "partner_id": customer_id,
            "order_line": []
        }
        
        for line in order_lines:
            order_line = (0, 0, {
                "product_id": line.get("product_id"),
                "product_uom_qty": line.get("quantity"),
                "price_unit": line.get("price_unit", 0.0),
            })
            sale_order_data["order_line"].append(order_line)
        
        order_id = client.execute_kw(
            "sale.order",
            "create",
            [sale_order_data]
        )
        
        if not order_id:
            return None
        
        order = client.execute_kw(
            "sale.order",
            "read",
            [order_id],
            {
                "fields": ["id", "name", "partner_id", "amount_total", 
                          "amount_untaxed", "state", "date_order"]
            }
        )
        
        if order:
            return {
                "id": order[0].get("id"),
                "name": order[0].get("name"),
                "customer_id": order[0].get("partner_id"),
                "amount_total": order[0].get("amount_total"),
                "amount_untaxed": order[0].get("amount_untaxed"),
                "state": order[0].get("state"),
                "date_order": order[0].get("date_order"),
            }
        
        return None
    
    except Exception as e:
        request_logger.error(f"Error creating sale order in Odoo: {str(e)}")
        return None
def get_all_orders(
    odoo_url: str,
    odoo_db: str,
    odoo_user: str,
    odoo_password: str,
    limit: int = 50
) -> Optional[List[Dict[str, Any]]]:
    """Fetch recent orders from Odoo."""
    try:
        client = OdooClient(odoo_url, odoo_db, odoo_user, odoo_password)
        if not client.authenticate():
            return None
            
        order_ids = client.execute_kw(
            "sale.order",
            "search",
            [[]],
            {"limit": limit, "order": "date_order desc"}
        )
        
        if not order_ids:
            return []
            
        orders = client.execute_kw(
            "sale.order",
            "read",
            [order_ids],
            {"fields": ["id", "name", "partner_id", "amount_total", "state", "date_order"]}
        )
        
        return [{
            "id": o.get("id"),
            "name": o.get("name"),
            "customer_name": o.get("partner_id")[1] if o.get("partner_id") else "Unknown",
            "amount_total": o.get("amount_total"),
            "state": o.get("state"),
            "date_order": o.get("date_order")
        } for o in orders]
        
    except Exception as e:
        request_logger.error(f"Error fetching all orders: {str(e)}")
        return None
