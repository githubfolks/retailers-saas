import re
from typing import Dict, Any, Optional


# ── HSN Master for Garments ──────────────────────────────────────────────────
# Source: GST Council notifications for textiles (Chapter 61/62)
GARMENT_HSN_MAP = {
    "6101": ("Men's overcoats, knitted", 12),
    "6102": ("Women's overcoats, knitted", 12),
    "6103": ("Men's suits, knitted", 12),
    "6104": ("Women's suits, knitted", 12),
    "6105": ("Men's shirts, knitted", 12),   # default for most shirts
    "6106": ("Women's blouses, knitted", 12),
    "6107": ("Men's underwear/pyjamas, knitted", 12),
    "6108": ("Women's underwear/nightwear, knitted", 12),
    "6109": ("T-shirts, singlets, knitted", 12),
    "6110": ("Jerseys, pullovers, sweatshirts, knitted", 12),
    "6111": ("Babies' garments, knitted", 12),
    "6201": ("Men's overcoats, woven", 12),
    "6202": ("Women's overcoats, woven", 12),
    "6203": ("Men's suits/trousers, woven", 12),
    "6204": ("Women's suits/dresses, woven", 12),
    "6205": ("Men's shirts, woven", 12),
    "6206": ("Women's blouses, woven", 12),
    "6207": ("Men's singlets/underwear, woven", 12),
    "6208": ("Women's singlets/nightwear, woven", 12),
    "6209": ("Babies' garments, woven", 12),
    "6210": ("Garments of felt/nonwovens", 12),
    "6211": ("Track-suits, ski-suits", 12),
    "6216": ("Gloves, mittens", 12),
    "6301": ("Blankets/travelling rugs", 5),
    "5007": ("Woven fabrics of silk", 5),
    "5208": ("Woven cotton fabrics", 5),
    "5209": ("Woven cotton fabrics >200g", 5),
    "5512": ("Woven synthetic fabrics", 5),
}

# GST slab thresholds for garments (per piece selling price)
_GARMENT_LOW_SLAB_THRESHOLD = 1000.0   # items ≤ ₹1000 → 5%
_GARMENT_LOW_RATE = 5.0
_GARMENT_HIGH_RATE = 12.0


def get_garment_gst_rate(selling_price: float) -> float:
    """
    Returns the correct GST rate for a garment based on its selling price.
    GST Council Notification: 5% for garments ≤ ₹1000, 12% above ₹1000.
    """
    if selling_price <= _GARMENT_LOW_SLAB_THRESHOLD:
        return _GARMENT_LOW_RATE
    return _GARMENT_HIGH_RATE


def validate_gstin(gstin: str) -> bool:
    """
    Validates Indian GSTIN format: 15-char alphanumeric.
    Format: 2-digit state code + 10-char PAN + 1 entity + 1 Z + 1 checksum
    """
    if not gstin:
        return False
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    return bool(re.match(pattern, gstin.upper().strip()))


def get_hsn_info(hsn_code: str) -> Dict[str, Any]:
    """Returns HSN description and standard GST rate for a given code."""
    if hsn_code in GARMENT_HSN_MAP:
        desc, rate = GARMENT_HSN_MAP[hsn_code]
        return {"hsn_code": hsn_code, "description": desc, "standard_rate": rate}
    return {"hsn_code": hsn_code, "description": "Garment", "standard_rate": 12}


def calculate_gst(
    base_amount: float,
    merchant_state: Optional[str],
    customer_state: Optional[str],
    gst_rate: Optional[float] = None,
    selling_price_per_unit: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculates GST breakdown for a garment order.

    - If gst_rate is not provided, auto-detects from selling_price_per_unit.
    - Applies IGST for interstate, CGST+SGST for intrastate.
    - Returns full breakdown dict including individual tax component amounts.
    """
    # Auto-detect slab if rate not explicitly provided
    if gst_rate is None:
        price_ref = selling_price_per_unit if selling_price_per_unit is not None else base_amount
        gst_rate = get_garment_gst_rate(price_ref)

    is_interstate = (
        str(merchant_state or "").strip().lower()
        != str(customer_state or "").strip().lower()
    ) or not customer_state

    total_tax_rate = gst_rate / 100
    tax_amount = round(base_amount * total_tax_rate, 2)
    grand_total = round(base_amount + tax_amount, 2)

    if is_interstate:
        return {
            "tax_type": "IGST",
            "gst_rate": gst_rate,
            "tax_amount": tax_amount,
            "igst_rate": gst_rate,
            "igst_amount": tax_amount,
            "cgst_rate": 0,
            "cgst_amount": 0.0,
            "sgst_rate": 0,
            "sgst_amount": 0.0,
            "grand_total": grand_total,
        }
    else:
        half_rate = round(gst_rate / 2, 2)
        half_tax = round(tax_amount / 2, 2)
        return {
            "tax_type": "CGST/SGST",
            "gst_rate": gst_rate,
            "tax_amount": tax_amount,
            "igst_rate": 0,
            "igst_amount": 0.0,
            "cgst_rate": half_rate,
            "cgst_amount": half_tax,
            "sgst_rate": half_rate,
            "sgst_amount": round(tax_amount - half_tax, 2),  # handle rounding
            "grand_total": grand_total,
        }
