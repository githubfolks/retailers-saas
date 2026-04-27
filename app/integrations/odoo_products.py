from typing import List, Dict, Any, Optional
from app.integrations.odoo_base import OdooClient
from app.core.logger import request_logger


def search_products(
    keyword: str,
    odoo_url: str,
    odoo_db: str,
    odoo_user: str,
    odoo_password: str
) -> Optional[List[Dict[str, Any]]]:
    try:
        client = OdooClient(odoo_url, odoo_db, odoo_user, odoo_password)
        
        if not client.authenticate():
            request_logger.error("Odoo authentication failed")
            return None
        
        product_ids = client.execute_kw(
            "product.product",
            "search",
            [[
                ["name", "ilike", keyword],
                ["sale_ok", "=", True]
            ]],
            {"limit": 10}
        )
        
        if not product_ids:
            return []
        
        products = client.execute_kw(
            "product.product",
            "read",
            [product_ids],
            {"fields": ["id", "name", "list_price", "default_code", "image_1920"]}
        )
        
        product_list = []
        for product in products:
            product_list.append({
                "id": product.get("id"),
                "name": product.get("name"),
                "price": product.get("list_price"),
                "code": product.get("default_code"),
                "image": product.get("image_1920")
            })
        
        return product_list
    
    except Exception as e:
        request_logger.error(f"Error searching products: {str(e)}")
        return None
def get_all_products(
    odoo_url: str,
    odoo_db: str,
    odoo_user: str,
    odoo_password: str,
    limit: int = 100
) -> Optional[List[Dict[str, Any]]]:
    """Fetch all sellable products from Odoo."""
    try:
        client = OdooClient(odoo_url, odoo_db, odoo_user, odoo_password)
        if not client.authenticate():
            return None
            
        product_ids = client.execute_kw(
            "product.product",
            "search",
            [[["sale_ok", "=", True]]],
            {"limit": limit}
        )
        
        if not product_ids:
            return []
            
        products = client.execute_kw(
            "product.product",
            "read",
            [product_ids],
            {"fields": ["id", "name", "list_price", "default_code", "description_sale"]}
        )
        
        return [{
            "odoo_id": p.get("id"),
            "name": p.get("name"),
            "price": p.get("list_price"),
            "sku": p.get("default_code") or f"ODOO-{p.get('id')}",
            "description": p.get("description_sale")
        } for p in products]
        
    except Exception as e:
        request_logger.error(f"Error fetching all products: {str(e)}")
        return None
