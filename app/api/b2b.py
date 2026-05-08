import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_permission
from app.models.b2b import B2BCustomer, WholesalePriceList, B2BOrder
from app.models.sku import ProductSKU

router = APIRouter(prefix="/b2b", tags=["b2b"], dependencies=[Depends(check_permission("procurement"))])


# ── Schemas ───────────────────────────────────────────────────────────────────

class B2BCustomerCreate(BaseModel):
    business_name: str
    mobile: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    gstin: Optional[str] = None
    address: Optional[str] = None
    credit_limit: float = 0.0
    payment_terms_days: int = 30
    customer_tier: str = "bronze"


class B2BCustomerUpdate(BaseModel):
    business_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    gstin: Optional[str] = None
    address: Optional[str] = None
    credit_limit: Optional[float] = None
    payment_terms_days: Optional[int] = None
    customer_tier: Optional[str] = None
    is_active: Optional[bool] = None


class PriceListCreate(BaseModel):
    tier: str
    sku: str
    min_qty: int = 1
    unit_price: float
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class OrderItemIn(BaseModel):
    sku: str
    qty: int


class B2BOrderCreate(BaseModel):
    b2b_customer_id: int
    items: List[OrderItemIn]
    po_reference: Optional[str] = None
    shipping_address: Optional[str] = None
    notes: Optional[str] = None
    discount_amount: float = 0.0


class PaymentRecord(BaseModel):
    amount: float
    notes: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_wholesale_price(
    db: Session, tenant_id: str, sku: str, tier: str, qty: int
) -> Optional[float]:
    """Return the best matching wholesale unit price for (sku, tier, qty)."""
    now = datetime.utcnow()
    entry = (
        db.query(WholesalePriceList)
        .filter(
            WholesalePriceList.tenant_id == tenant_id,
            WholesalePriceList.sku == sku,
            WholesalePriceList.tier == tier,
            WholesalePriceList.min_qty <= qty,
        )
        .filter(
            (WholesalePriceList.valid_from == None)
            | (WholesalePriceList.valid_from <= now)
        )
        .filter(
            (WholesalePriceList.valid_to == None)
            | (WholesalePriceList.valid_to >= now)
        )
        .order_by(WholesalePriceList.min_qty.desc())
        .first()
    )
    return entry.unit_price if entry else None


# ── B2B Customers ─────────────────────────────────────────────────────────────

@router.post("/customers")
async def create_b2b_customer(
    req: B2BCustomerCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Register a new wholesale buyer."""
    existing = db.query(B2BCustomer).filter(
        B2BCustomer.tenant_id == current_tenant_id,
        B2BCustomer.mobile == req.mobile,
    ).first()
    if existing:
        raise HTTPException(
            status_code=409, detail="B2B customer already registered with this mobile"
        )

    customer = B2BCustomer(
        tenant_id=current_tenant_id,
        business_name=req.business_name,
        mobile=req.mobile,
        contact_person=req.contact_person,
        email=req.email,
        gstin=req.gstin,
        address=req.address,
        credit_limit=req.credit_limit,
        payment_terms_days=req.payment_terms_days,
        customer_tier=req.customer_tier,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/customers")
async def list_b2b_customers(
    active_only: bool = True,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """List all wholesale buyers for the tenant."""
    query = db.query(B2BCustomer).filter(B2BCustomer.tenant_id == current_tenant_id)
    if active_only:
        query = query.filter(B2BCustomer.is_active == True)
    return query.order_by(B2BCustomer.business_name).all()


@router.get("/customers/{customer_id}")
async def get_b2b_customer(
    customer_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Get a wholesale buyer with available credit info."""
    customer = db.query(B2BCustomer).filter(
        B2BCustomer.id == customer_id,
        B2BCustomer.tenant_id == current_tenant_id,
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="B2B customer not found")

    return {
        "id": customer.id,
        "tenant_id": customer.tenant_id,
        "business_name": customer.business_name,
        "contact_person": customer.contact_person,
        "mobile": customer.mobile,
        "email": customer.email,
        "gstin": customer.gstin,
        "address": customer.address,
        "credit_limit": customer.credit_limit,
        "credit_used": customer.credit_used,
        "credit_available": customer.credit_limit - customer.credit_used,
        "payment_terms_days": customer.payment_terms_days,
        "customer_tier": customer.customer_tier,
        "is_active": customer.is_active,
        "created_at": customer.created_at,
    }


@router.put("/customers/{customer_id}")
async def update_b2b_customer(
    customer_id: int,
    req: B2BCustomerUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Update a wholesale buyer's profile."""
    customer = db.query(B2BCustomer).filter(
        B2BCustomer.id == customer_id,
        B2BCustomer.tenant_id == current_tenant_id,
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="B2B customer not found")

    for field, value in req.dict(exclude_none=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


# ── Wholesale Price Lists ─────────────────────────────────────────────────────

@router.post("/price-lists")
async def create_price_list_entry(
    req: PriceListCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Set a tier-based wholesale price for a SKU."""
    entry = WholesalePriceList(
        tenant_id=current_tenant_id,
        tier=req.tier,
        sku=req.sku,
        min_qty=req.min_qty,
        unit_price=req.unit_price,
        valid_from=req.valid_from,
        valid_to=req.valid_to,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/price-lists/{sku}")
async def get_tier_prices(
    sku: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Get all tier prices for a given SKU."""
    return (
        db.query(WholesalePriceList)
        .filter(
            WholesalePriceList.tenant_id == current_tenant_id,
            WholesalePriceList.sku == sku,
        )
        .order_by(WholesalePriceList.tier, WholesalePriceList.min_qty)
        .all()
    )


# ── B2B Orders ────────────────────────────────────────────────────────────────

@router.post("/orders")
async def create_b2b_order(
    req: B2BOrderCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a wholesale order with tier pricing and credit check."""
    customer = db.query(B2BCustomer).filter(
        B2BCustomer.id == req.b2b_customer_id,
        B2BCustomer.tenant_id == current_tenant_id,
        B2BCustomer.is_active == True,
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="B2B customer not found")

    line_items = []
    total_amount = 0.0
    for item in req.items:
        sku_rec = db.query(ProductSKU).filter(
            ProductSKU.sku == item.sku,
            ProductSKU.tenant_id == current_tenant_id,
        ).first()
        if not sku_rec:
            raise HTTPException(status_code=400, detail=f"SKU '{item.sku}' not found")

        unit_price = _get_wholesale_price(
            db, current_tenant_id, item.sku, customer.customer_tier, item.qty
        )
        if unit_price is None:
            unit_price = float(sku_rec.seasonal_price or sku_rec.selling_price)

        subtotal = unit_price * item.qty
        total_amount += subtotal
        line_items.append({
            "sku": item.sku,
            "product_name": sku_rec.product_name,
            "qty": item.qty,
            "unit_price": unit_price,
            "subtotal": subtotal,
        })

    grand_total = total_amount - req.discount_amount

    credit_available = customer.credit_limit - customer.credit_used
    if customer.credit_limit > 0 and grand_total > credit_available:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Order exceeds available credit. "
                f"Available: Rs.{credit_available:.0f}, Order: Rs.{grand_total:.0f}"
            ),
        )

    due_date = datetime.utcnow() + timedelta(days=customer.payment_terms_days)
    order = B2BOrder(
        tenant_id=current_tenant_id,
        b2b_customer_id=customer.id,
        po_reference=req.po_reference,
        items=json.dumps(line_items),
        total_amount=total_amount,
        discount_amount=req.discount_amount,
        grand_total=grand_total,
        payment_terms_days=customer.payment_terms_days,
        due_date=due_date,
        shipping_address=req.shipping_address or customer.address,
        notes=req.notes,
    )
    db.add(order)
    customer.credit_used += grand_total
    db.commit()
    db.refresh(order)

    import asyncio
    from app.models.tenant import Tenant
    from app.services.whatsapp_bot_service import WhatsAppBotService

    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    if tenant:
        asyncio.create_task(
            WhatsAppBotService.send_b2b_order_alert(
                tenant, order.id, customer.business_name,
                grand_total, customer.payment_terms_days,
            )
        )

    return {
        "id": order.id,
        "b2b_customer_id": order.b2b_customer_id,
        "po_reference": order.po_reference,
        "status": order.status,
        "payment_status": order.payment_status,
        "grand_total": order.grand_total,
        "due_date": order.due_date,
        "items": line_items,
        "created_at": order.created_at,
    }


@router.get("/orders")
async def list_b2b_orders(
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """List B2B orders with overdue flag for credit aging."""
    query = (
        db.query(B2BOrder, B2BCustomer)
        .join(B2BCustomer, B2BOrder.b2b_customer_id == B2BCustomer.id)
        .filter(B2BOrder.tenant_id == current_tenant_id)
    )
    if status:
        query = query.filter(B2BOrder.status == status)
    if payment_status:
        query = query.filter(B2BOrder.payment_status == payment_status)

    now = datetime.utcnow()
    result = []
    for order, customer in query.order_by(B2BOrder.created_at.desc()).all():
        is_overdue = (
            order.payment_status != "paid"
            and order.due_date is not None
            and order.due_date < now
        )
        result.append({
            "id": order.id,
            "business_name": customer.business_name,
            "b2b_customer_id": order.b2b_customer_id,
            "po_reference": order.po_reference,
            "status": order.status,
            "payment_status": order.payment_status,
            "grand_total": order.grand_total,
            "due_date": order.due_date,
            "is_overdue": is_overdue,
            "created_at": order.created_at,
        })
    return result


@router.get("/orders/{order_id}")
async def get_b2b_order(
    order_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Get full B2B order detail."""
    order = db.query(B2BOrder).filter(
        B2BOrder.id == order_id,
        B2BOrder.tenant_id == current_tenant_id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="B2B order not found")

    items = json.loads(order.items) if order.items else []
    return {
        "id": order.id,
        "tenant_id": order.tenant_id,
        "b2b_customer_id": order.b2b_customer_id,
        "po_reference": order.po_reference,
        "status": order.status,
        "payment_status": order.payment_status,
        "payment_terms_days": order.payment_terms_days,
        "due_date": order.due_date,
        "items": items,
        "total_amount": order.total_amount,
        "discount_amount": order.discount_amount,
        "grand_total": order.grand_total,
        "shipping_address": order.shipping_address,
        "notes": order.notes,
        "created_at": order.created_at,
    }


@router.post("/orders/{order_id}/invoice")
async def generate_b2b_invoice(
    order_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Generate a B2B invoice document for an order."""
    order = db.query(B2BOrder).filter(
        B2BOrder.id == order_id,
        B2BOrder.tenant_id == current_tenant_id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="B2B order not found")

    customer = db.query(B2BCustomer).filter(B2BCustomer.id == order.b2b_customer_id).first()
    items = json.loads(order.items) if order.items else []

    return {
        "invoice_number": f"B2B-INV-{order.id:06d}",
        "order_id": order.id,
        "customer": {
            "business_name": customer.business_name if customer else "",
            "gstin": customer.gstin if customer else "",
            "address": customer.address if customer else "",
            "mobile": customer.mobile if customer else "",
        },
        "po_reference": order.po_reference,
        "items": items,
        "total_amount": order.total_amount,
        "discount_amount": order.discount_amount,
        "grand_total": order.grand_total,
        "payment_terms_days": order.payment_terms_days,
        "due_date": order.due_date,
        "status": order.status,
        "payment_status": order.payment_status,
        "created_at": order.created_at,
    }


@router.post("/orders/{order_id}/record-payment")
async def record_b2b_payment(
    order_id: int,
    req: PaymentRecord,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Record a partial or full payment against a B2B order, releasing credit."""
    order = db.query(B2BOrder).filter(
        B2BOrder.id == order_id,
        B2BOrder.tenant_id == current_tenant_id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="B2B order not found")

    customer = db.query(B2BCustomer).filter(B2BCustomer.id == order.b2b_customer_id).first()
    if customer:
        customer.credit_used = max(0.0, customer.credit_used - req.amount)

    order.payment_status = "paid" if req.amount >= order.grand_total else "partial"

    if req.notes:
        order.notes = (
            f"{order.notes}\nPayment Rs.{req.amount:.0f}: {req.notes}".strip()
            if order.notes
            else f"Payment Rs.{req.amount:.0f}: {req.notes}"
        )

    db.commit()
    return {
        "status": "ok",
        "payment_status": order.payment_status,
        "amount_recorded": req.amount,
    }
