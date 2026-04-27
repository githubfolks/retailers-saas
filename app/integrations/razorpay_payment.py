import requests
from typing import Optional, Dict, Any
from base64 import b64encode


def create_payment_link(
    amount: float,
    description: str,
    customer_email: str,
    customer_phone: str,
    razorpay_key: str,
    razorpay_secret: str,
    notify_sms: bool = True,
    notify_email: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Create a payment link using Razorpay API.
    
    Args:
        amount: Amount in paise (multiply by 100)
        description: Payment description
        customer_email: Customer email
        customer_phone: Customer phone number
        razorpay_key: Razorpay API key
        razorpay_secret: Razorpay API secret
        notify_sms: Send SMS notification
        notify_email: Send email notification
    
    Returns:
        Payment link details or None
    """
    try:
        auth = b64encode(f"{razorpay_key}:{razorpay_secret}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "amount": int(amount * 100),
            "currency": "INR",
            "description": description,
            "customer_notify": 1 if notify_sms or notify_email else 0,
            "notify": {
                "sms": notify_sms,
                "email": notify_email
            },
            "upi_link": False,
            "first_min_partial_amount": int(amount * 100),
        }
        
        response = requests.post(
            "https://api.razorpay.com/v1/payment_links",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 201:
            print(f"Razorpay error: {response.text}")
            return None
        
        data = response.json()
        
        return {
            "id": data.get("id"),
            "short_url": data.get("short_url"),
            "user_id": data.get("user_id"),
            "amount": data.get("amount"),
            "currency": data.get("currency"),
            "description": data.get("description"),
            "status": data.get("status"),
            "created_at": data.get("created_at"),
            "expire_by": data.get("expire_by"),
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating payment link: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None
