import requests
import json
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:9000")
TENANT_ID = "acme-corp"

# Mock order data to link to existing SKUs
MOCK_ORDERS = [
    {
        "customer_mobile": "9876543210",
        "product_name": "Premium Cotton Shirt (Blue)",
        "sku": "SHIRT-BLUE-001",
        "quantity": 2,
        "unit_price": 299.0,
        "total_amount": 598.0,
        "tax_type": "CGST/SGST",
        "tax_amount": 107.64, # 18% of 598
        "grand_total": 705.64,
        "customer_state": "Maharashtra"
    },
    {
        "customer_mobile": "9876543210", # Same customer
        "product_name": "Running Shoes (Blue)",
        "sku": "SHOE-RUNNING-001",
        "quantity": 1,
        "unit_price": 4999.0,
        "total_amount": 4999.0,
        "tax_type": "IGST",
        "tax_amount": 899.82,
        "grand_total": 5898.82,
        "customer_state": "Karnataka"
    },
    {
        "customer_mobile": "9000000001", # New customer
        "product_name": "Baseball Hat",
        "sku": "HAT-BASEBALL-001",
        "quantity": 5,
        "unit_price": 199.0,
        "total_amount": 995.0,
        "tax_type": "CGST/SGST",
        "tax_amount": 179.1,
        "grand_total": 1174.1,
        "customer_state": "Maharashtra"
    }
]

def seed_financial_data():
    print("Testing Financial & CRM Logic...")
    
    # 1. Get token
    auth_res = requests.post(f"{BASE_URL}/auth/token", data={
        "username": "admin@acme-corp.com",
        "password": "password123"
    })
    token = auth_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Inject orders
    for order in MOCK_ORDERS:
        res = requests.post(f"{BASE_URL}/orders/", json=order, headers=headers)
        if res.status_code == 200:
            print(f"Created order for {order['sku']} - Linked to {order['customer_mobile']}")
            
            # Manually set status to 'completed' for P&L calculation
            order_id = res.json().get("id")
            requests.patch(f"{BASE_URL}/orders/{order_id}", json={"status": "completed"}, headers=headers)
            
    print("\nData seeding complete. Verify Analytics Dashboard now.")

if __name__ == "__main__":
    seed_financial_data()
