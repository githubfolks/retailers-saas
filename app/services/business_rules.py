from typing import Dict, List, Any, Tuple
from app.core.logger import request_logger


class BusinessRulesEngine:
    
    @staticmethod
    def validate_product_inquiry(
        product_keyword: str,
        available_products: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Validate product inquiry.
        
        Returns: (is_valid, message)
        """
        if not product_keyword or len(product_keyword.strip()) == 0:
            return False, "Product name cannot be empty"
        
        if len(product_keyword) < 2:
            return False, "Product name must be at least 2 characters"
        
        if len(product_keyword) > 100:
            return False, "Product name is too long (max 100 characters)"
        
        matching_products = [
            p for p in available_products 
            if product_keyword.lower() in p.get("name", "").lower()
        ]
        
        if not matching_products:
            return False, "No products found matching your inquiry"
        
        return True, f"Found {len(matching_products)} matching products"
    
    @staticmethod
    def validate_quantity(
        quantity: int,
        min_quantity: int = 1,
        max_quantity: int = 10000
    ) -> Tuple[bool, str]:
        """
        Validate order quantity.
        
        Returns: (is_valid, message)
        """
        if not isinstance(quantity, int):
            return False, "Quantity must be a number"
        
        if quantity < min_quantity:
            return False, f"Minimum quantity is {min_quantity}"
        
        if quantity > max_quantity:
            return False, f"Maximum quantity is {max_quantity}"
        
        return True, f"Valid quantity: {quantity} units"
    
    @staticmethod
    def validate_address(
        address: str,
        mobile: str
    ) -> Tuple[bool, str]:
        """
        Validate delivery address.
        
        Returns: (is_valid, message)
        """
        if not address or len(address.strip()) == 0:
            return False, "Address cannot be empty"
        
        if len(address) < 5:
            return False, "Address is too short (minimum 5 characters)"
        
        if len(address) > 500:
            return False, "Address is too long (maximum 500 characters)"
        
        if not mobile or len(mobile.strip()) == 0:
            return False, "Mobile number is required for address verification"
        
        if not mobile.isdigit() or len(mobile) != 10:
            return False, "Invalid mobile number format"
        
        return True, "Address is valid"
    
    @staticmethod
    def validate_payment(
        payment_amount: float,
        order_total: float,
        payment_status: str = "pending"
    ) -> Tuple[bool, str]:
        """
        Validate payment details.
        
        Returns: (is_valid, message)
        """
        if payment_amount <= 0:
            return False, "Payment amount must be greater than zero"
        
        if order_total <= 0:
            return False, "Order total must be greater than zero"
        
        tolerance = 1.0
        if abs(payment_amount - order_total) > tolerance:
            return False, f"Payment amount ({payment_amount}) does not match order total ({order_total})"
        
        valid_statuses = ["pending", "completed", "failed", "cancelled"]
        if payment_status not in valid_statuses:
            return False, f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}"
        
        return True, f"Payment validated: {payment_amount}"
    
    @staticmethod
    def validate_complete_order(
        product_name: str,
        quantity: int,
        address: str,
        mobile: str,
        order_total: float,
        available_products: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """
        Validate complete order against all business rules.
        
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        product_valid, product_msg = BusinessRulesEngine.validate_product_inquiry(
            product_name, 
            available_products
        )
        if not product_valid:
            errors.append(product_msg)
        
        quantity_valid, quantity_msg = BusinessRulesEngine.validate_quantity(quantity)
        if not quantity_valid:
            errors.append(quantity_msg)
        
        address_valid, address_msg = BusinessRulesEngine.validate_address(address, mobile)
        if not address_valid:
            errors.append(address_msg)
        
        payment_valid, payment_msg = BusinessRulesEngine.validate_payment(
            order_total, 
            order_total
        )
        if not payment_valid:
            errors.append(payment_msg)
        
        is_valid = len(errors) == 0
        
        if is_valid:
            request_logger.info(f"Order validation successful: {product_name} x{quantity}")
        else:
            request_logger.warning(f"Order validation failed: {errors}")
        
        return is_valid, errors
