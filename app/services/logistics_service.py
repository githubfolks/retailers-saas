import re
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.customer import Customer
from app.models.procurement import LogisticsPartner
from app.models.fulfillment import Fulfillment
from app.integrations.shiprocket import ShiprocketClient, ShiprocketError


def _extract_pincode(text: str) -> str:
    """Pull the first 6-digit Indian pincode out of a free-text address."""
    if not text:
        return ""
    match = re.search(r"\b([1-9][0-9]{5})\b", text)
    return match.group(1) if match else ""


def _parse_city_state(text: str) -> tuple[str, str]:
    """Best-effort parse of 'City, State' or 'City - PINCODE, State' from address."""
    if not text:
        return "", ""
    lines = [l.strip() for l in text.replace("\n", ",").split(",") if l.strip()]
    city = lines[-3] if len(lines) >= 3 else (lines[-2] if len(lines) >= 2 else "")
    state = lines[-1] if len(lines) >= 1 else ""
    city = re.sub(r"\s*-?\s*\d{6}", "", city).strip()
    state = re.sub(r"\s*-?\s*\d{6}", "", state).strip()
    return city, state


async def auto_assign_awb(
    order_id: int,
    logistics_partner_id: int,
    tenant_id: str,
    db: Session,
) -> Fulfillment:
    order = db.query(Order).filter(
        Order.id == order_id, Order.tenant_id == tenant_id
    ).first()
    if not order:
        raise ValueError("Order not found")

    partner = db.query(LogisticsPartner).filter(
        LogisticsPartner.id == logistics_partner_id,
        LogisticsPartner.tenant_id == tenant_id,
        LogisticsPartner.is_active == True,
    ).first()
    if not partner:
        raise ValueError("Logistics partner not found")

    if partner.provider_type not in ("shiprocket",):
        raise ValueError(f"Auto-AWB not supported for provider type '{partner.provider_type}'. Use 'shiprocket'.")

    if not partner.api_email or not partner.api_password:
        raise ValueError("API credentials not configured for this logistics partner")

    customer_name = order.customer_mobile
    if order.customer_id:
        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        if customer and customer.name:
            customer_name = customer.name

    address = order.shipping_address or ""
    pincode = _extract_pincode(address)
    city, state = _parse_city_state(address)

    if not pincode:
        raise ValueError("Cannot extract pincode from shipping address. Please update the order's shipping address.")

    weight_kg = 0.5
    if order.sku:
        from app.models.sku import ProductSKU
        sku_obj = db.query(ProductSKU).filter(
            ProductSKU.sku_code == order.sku,
            ProductSKU.tenant_id == tenant_id
        ).first()
        if sku_obj and getattr(sku_obj, "weight", None):
            weight_kg = float(sku_obj.weight)

    payment_method = "prepaid"
    if getattr(order, "payment_method", None) == "cod":
        payment_method = "cod"

    if partner.provider_type == "shiprocket":
        client = ShiprocketClient(partner.api_email, partner.api_password)
        result = await client.create_shipment(
            order_id=order.id,
            order_date=order.created_at.strftime("%Y-%m-%d %H:%M"),
            customer_name=customer_name,
            customer_phone=order.customer_mobile,
            customer_address=address,
            customer_city=city,
            customer_pincode=pincode,
            customer_state=state or (order.customer_state or ""),
            product_name=order.product_name,
            sku=order.sku or "",
            quantity=order.quantity,
            unit_price=order.unit_price,
            weight_kg=weight_kg,
            pickup_location=partner.pickup_location_name or "Primary",
            payment_method=payment_method,
        )

    fulfillment = Fulfillment(
        tenant_id=tenant_id,
        order_id=order_id,
        carrier_name=result["carrier_name"] or partner.name,
        tracking_number=result["awb"],
        shipping_label_url=result.get("label_url") or None,
        provider_shipment_id=result.get("shipment_id"),
        shipping_cost=result.get("shipping_cost"),
        status="shipped",
        shipped_at=datetime.utcnow(),
    )
    order.status = "completed"
    db.add(fulfillment)
    db.commit()
    db.refresh(fulfillment)
    return fulfillment
