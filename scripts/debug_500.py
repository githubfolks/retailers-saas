import requests
import json

import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:9000")

def debug_api():
    # 1. Get token
    auth_res = requests.post(f"{BASE_URL}/auth/token", data={
        "username": "admin@acme-corp.com",
        "password": "password123"
    })
    token = auth_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test Analytics Comprehensive Report
    print("Testing /analytics/comprehensive-report...")
    res = requests.get(f"{BASE_URL}/analytics/comprehensive-report", headers=headers)
    print(f"Status: {res.status_code}")
    if res.status_code != 200:
        print(res.text)
    else:
        print("Success! Data received.")

if __name__ == "__main__":
    debug_api()
