import httpx
from datetime import datetime
from typing import Optional


SHIPROCKET_BASE = "https://apiv2.shiprocket.in/v1/external"


class ShiprocketError(Exception):
    pass


class ShiprocketClient:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self._token: Optional[str] = None

    async def _get_token(self) -> str:
        if self._token:
            return self._token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{SHIPROCKET_BASE}/auth/login",
                json={"email": self.email, "password": self.password},
                timeout=15,
            )
            data = resp.json()
            if resp.status_code != 200 or "token" not in data:
                raise ShiprocketError(f"Auth failed: {data.get('message', resp.text)}")
            self._token = data["token"]
            return self._token

    async def create_shipment(
        self,
        order_id: int,
        order_date: str,
        customer_name: str,
        customer_phone: str,
        customer_address: str,
        customer_city: str,
        customer_pincode: str,
        customer_state: str,
        product_name: str,
        sku: str,
        quantity: int,
        unit_price: float,
        weight_kg: float,
        pickup_location: str,
        payment_method: str = "prepaid",
        length_cm: float = 10,
        breadth_cm: float = 10,
        height_cm: float = 10,
    ) -> dict:
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        payload = {
            "order_id": f"ORD-{order_id}",
            "order_date": order_date,
            "pickup_location": pickup_location,
            "billing_customer_name": customer_name,
            "billing_last_name": "",
            "billing_address": customer_address,
            "billing_city": customer_city,
            "billing_pincode": customer_pincode,
            "billing_state": customer_state,
            "billing_country": "India",
            "billing_email": "",
            "billing_phone": customer_phone,
            "shipping_is_billing": 1,
            "order_items": [
                {
                    "name": product_name,
                    "sku": sku or f"SKU-{order_id}",
                    "units": quantity,
                    "selling_price": str(unit_price),
                    "discount": "",
                    "tax": "",
                    "hsn": "",
                }
            ],
            "payment_method": payment_method,
            "shipping_charges": 0,
            "giftwrap_charges": 0,
            "transaction_charges": 0,
            "total_discount": 0,
            "sub_total": unit_price * quantity,
            "length": length_cm,
            "breadth": breadth_cm,
            "height": height_cm,
            "weight": weight_kg,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{SHIPROCKET_BASE}/orders/create/adhoc",
                json=payload,
                headers=headers,
                timeout=20,
            )
            data = resp.json()
            if resp.status_code not in (200, 201):
                raise ShiprocketError(f"Create order failed: {data.get('message', resp.text)}")

            shipment_id = data.get("shipment_id")
            if not shipment_id:
                raise ShiprocketError("No shipment_id returned from Shiprocket")

            awb_resp = await client.post(
                f"{SHIPROCKET_BASE}/courier/assign/awb",
                json={"shipment_id": [shipment_id]},
                headers=headers,
                timeout=20,
            )
            awb_data = awb_resp.json()
            if awb_resp.status_code != 200:
                raise ShiprocketError(f"AWB assignment failed: {awb_data.get('message', awb_resp.text)}")

            awb_info = awb_data.get("response", {}).get("data", {})
            awb_code = awb_info.get("awb_code") or awb_data.get("awb_code")
            if not awb_code:
                raise ShiprocketError("AWB code not returned")

            return {
                "awb": awb_code,
                "carrier_name": awb_info.get("courier_name", ""),
                "shipment_id": str(shipment_id),
                "label_url": awb_info.get("label", ""),
                "shipping_cost": float(awb_info.get("rate", 0) or 0),
            }
