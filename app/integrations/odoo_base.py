import xmlrpc.client
from typing import Optional
from app.core.logger import request_logger


class OdooClient:
    """Reusable Odoo XMLRPC client."""
    
    def __init__(self, odoo_url: str, odoo_db: str, odoo_user: str, odoo_password: str):
        self.odoo_url = odoo_url
        self.odoo_db = odoo_db
        self.odoo_user = odoo_user
        self.odoo_password = odoo_password
        self.uid = None
        self.common = None
        self.models = None
    
    def authenticate(self) -> Optional[int]:
        """Authenticate and return uid."""
        try:
            self.common = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/common")
            
            self.uid = self.common.authenticate(
                self.odoo_db,
                self.odoo_user,
                self.odoo_password,
                {}
            )
            
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/object")
                request_logger.info(f"Odoo authenticated with UID: {self.uid}")
            else:
                request_logger.error("Odoo authentication failed")
            
            return self.uid
        
        except Exception as e:
            request_logger.error(f"Odoo authentication error: {str(e)}")
            return None
    
    def execute_kw(self, model: str, method: str, args: list, kwargs: dict = None):
        """Execute XMLRPC method."""
        if not self.uid or not self.models:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            kwargs = kwargs or {}
            result = self.models.execute_kw(
                self.odoo_db,
                self.uid,
                self.odoo_password,
                model,
                method,
                args,
                kwargs
            )
            return result
        except Exception as e:
            request_logger.error(f"Odoo execute_kw error: {str(e)}")
            raise
