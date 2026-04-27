from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.database import get_db
from app.api.auth import get_current_tenant_id, check_permission
from app.core.logger import request_logger
from app.core.billing import calculate_gst
from app.models.tenant import Tenant
from app.models.order import Order
from app.models.customer import Customer
from app.models.fulfillment import Fulfillment

router = APIRouter(
    prefix="/orders", 
    tags=["orders"],
    dependencies=[Depends(check_permission("pos"))]
)


class OrderResponse(BaseModel):
    id: int
    tenant_id: str
    customer_id: Optional[int]
    customer_mobile: str
    product_name: str
    quantity: int
    unit_price: float
    total_amount: float
    status: str
    payment_status: str
    payment_id: Optional[str]
    invoice_number: Optional[str]
    shipping_address: Optional[str]
    customer_state: Optional[str]
    customer_gstin: Optional[str] = None
    tax_type: Optional[str]
    gst_rate: Optional[float] = None
    tax_amount: Optional[float]
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    grand_total: Optional[float]
    hsn_code: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    # New pro fields
    unit_cost_at_sale: Optional[float] = None
    discount_amount: Optional[float] = 0.0
    coupon_code: Optional[str] = None
    commitment_date: Optional[datetime] = None
    effective_delivery_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class FulfillmentResponse(BaseModel):
    id: int
    carrier_name: Optional[str]
    tracking_number: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    order_id: int
    invoice_number: Optional[str]
    business_details: dict
    customer_details: dict
    items: List[dict]
    tax_breakdown: dict
    grand_total: float


class OrderSummary(BaseModel):
    total_orders: int
    total_revenue: float
    pending_orders: int
    completed_orders: int

class POSSummary(BaseModel):
    today_sales: float
    today_order_count: int
    payment_breakdown: Dict[str, float]
    top_items: List[Dict[str, Any]]


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    payment_status: Optional[str] = None
):
    """List all orders for current tenant with optional filtering."""
    try:
        query = db.query(Order).filter(
            Order.tenant_id == current_tenant_id
        )
        
        if status:
            query = query.filter(Order.status == status)
        
        if payment_status:
            query = query.filter(Order.payment_status == payment_status)
        
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        
        request_logger.info(
            f"Listed {len(orders)} orders for tenant: {current_tenant_id}"
        )
        
        return orders
    
    except Exception as e:
        request_logger.error(f"Error listing orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing orders")

@router.get("/summary", response_model=OrderSummary)
async def get_order_summary(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get order summary for current tenant."""
    try:
        total_orders = db.query(func.count(Order.id)).filter(
            Order.tenant_id == current_tenant_id
        ).scalar() or 0

        completed_orders = db.query(func.count(Order.id)).filter(
            Order.tenant_id == current_tenant_id,
            Order.status == "completed"
        ).scalar() or 0

        pending_orders = db.query(func.count(Order.id)).filter(
            Order.tenant_id == current_tenant_id,
            Order.status == "pending"
        ).scalar() or 0

        total_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.tenant_id == current_tenant_id,
            Order.status == "completed"
        ).scalar() or 0.0

        return {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "pending_orders": pending_orders,
            "completed_orders": completed_orders
        }

    except Exception as e:
        request_logger.error(f"Error getting order summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting order summary")


@router.get("/pos-summary", response_model=POSSummary)
async def get_pos_summary(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get today's POS sales summary."""
    from datetime import date
    from sqlalchemy import cast, Date

    today = date.today()
    base_filter = [
        Order.tenant_id == current_tenant_id,
        cast(Order.created_at, Date) == today,
        Order.status != "cancelled",
    ]

    try:
        total_sales = db.query(func.sum(Order.total_amount)).filter(*base_filter).scalar() or 0.0
        order_count = db.query(func.count(Order.id)).filter(*base_filter).scalar() or 0
    except Exception as e:
        request_logger.error(f"Error getting POS summary totals: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error getting POS summary")

    # Payment breakdown — gracefully degrades if payment_method column not yet migrated
    payments: Dict[str, float] = {"cash": 0.0, "upi": 0.0, "card": 0.0, "pending": 0.0}
    try:
        rows = (
            db.query(Order.payment_method, func.sum(Order.total_amount))
            .filter(*base_filter)
            .group_by(Order.payment_method)
            .all()
        )
        for method, amount in rows:
            key = method if method in payments else "pending"
            payments[key] += float(amount or 0.0)
    except Exception:
        db.rollback()  # column not yet migrated — return zero breakdown

    # Top items by quantity
    top_items: List[Dict[str, Any]] = []
    try:
        item_rows = (
            db.query(Order.product_name, func.sum(Order.quantity))
            .filter(*base_filter)
            .group_by(Order.product_name)
            .order_by(func.sum(Order.quantity).desc())
            .limit(5)
            .all()
        )
        top_items = [{"name": name, "qty": int(qty or 0)} for name, qty in item_rows]
    except Exception:
        db.rollback()

    return {
        "today_sales": float(total_sales),
        "today_order_count": order_count,
        "payment_breakdown": payments,
        "top_items": top_items,
    }


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Get a specific order for current tenant."""
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.tenant_id == current_tenant_id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return order
    
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error(f"Error getting order: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting order")


@router.get("/customer/{customer_mobile}", response_model=List[OrderResponse])
async def get_customer_orders(
    customer_mobile: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get all orders for a specific customer."""
    try:
        orders = db.query(Order).filter(
            Order.tenant_id == current_tenant_id,
            Order.customer_mobile == customer_mobile
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        
        request_logger.info(
            f"Listed {len(orders)} orders for customer {customer_mobile} "
            f"(tenant: {current_tenant_id})"
        )
        
        return orders
    
    except Exception as e:
        request_logger.error(f"Error listing customer orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing customer orders")


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: str = Query(..., description="New order status"),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Update order status for current tenant."""
    try:
        valid_statuses = ["pending", "processing", "completed", "cancelled"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.tenant_id == current_tenant_id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(order)
        
        request_logger.info(
            f"Updated order {order_id} status to {new_status} "
            f"(tenant: {current_tenant_id})"
        )
        
        return {
            "status": "updated",
            "order_id": order_id,
            "new_status": new_status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        request_logger.error(f"Error updating order status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating order status")


@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Confirm a draft quotation into a real order, checking inventory."""
    order = db.query(Order).filter(Order.id == order_id, Order.tenant_id == current_tenant_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft orders can be confirmed")
    
    # 1. Check Inventory (Optional but recommended at confirmation)
    if order.sku:
        from app.models.sku import ProductSKU
        sku_record = db.query(ProductSKU).filter(
            ProductSKU.tenant_id == current_tenant_id,
            ProductSKU.sku == order.sku
        ).first()
        if sku_record and sku_record.quantity < order.quantity:
            request_logger.warning(f"Low stock for SKU {order.sku} at confirmation: {sku_record.quantity} available")
            # We can still confirm but warn or block

    # 2. Update status
    order.status = "pending"
    order.updated_at = datetime.utcnow()
    
    # 3. Trigger WhatsApp/n8n for "Order Confirmed"
    from app.models.tenant import Tenant
    from app.services.n8n_service import N8NService
    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    if tenant and tenant.n8n_webhook_url:
        import asyncio
        asyncio.create_task(N8NService.trigger_order_flow(
            tenant.n8n_webhook_url, 
            {
                "event": "order.confirmed",
                "id": order.id,
                "customer_mobile": order.customer_mobile,
                "amount": order.total_amount
            }
        ))
        
    db.commit()
    return order


@router.patch("/{order_id}/payment-status")
async def update_payment_status(
    order_id: int,
    new_payment_status: str = Query(..., description="New payment status"),
    payment_id: Optional[str] = Query(None, description="Payment transaction ID"),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Update payment status for order."""
    try:
        valid_statuses = ["pending", "completed", "failed", "refunded"]
        if new_payment_status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.tenant_id == current_tenant_id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order.payment_status = new_payment_status
        if payment_id:
            order.payment_id = payment_id
        order.updated_at = datetime.utcnow()
        
        if new_payment_status == "completed" and order.status == "pending":
            order.status = "processing"
        
        db.commit()
        db.refresh(order)
        
        request_logger.info(
            f"Updated order {order_id} payment status to {new_payment_status} "
            f"(tenant: {current_tenant_id})"
        )
        
        return {
            "status": "updated",
            "order_id": order_id,
            "payment_status": new_payment_status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        request_logger.error(f"Error updating payment status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating payment status")


@router.post("/{order_id}/generate-payment")
async def generate_payment_link(
    order_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Generate a Razorpay Payment Link for an order."""
    from app.services.razorpay_service import RazorpayService
    from app.models.tenant import Tenant
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    order = db.query(Order).filter(Order.id == order_id, Order.tenant_id == current_tenant_id).first()
    
    if not tenant or not order:
        raise HTTPException(status_code=404, detail="Tenant or Order not found")
        
    payment_link = await RazorpayService.create_payment_link(
        tenant_id=current_tenant_id,
        order_id=order.id,
        amount=order.total_amount,
        customer_mobile=order.customer_mobile,
        razorpay_key=tenant.razorpay_key,
        razorpay_secret=tenant.razorpay_secret,
        business_name=tenant.business_name
    )
    
    if not payment_link:
        raise HTTPException(status_code=500, detail="Failed to create payment link")
        
    order.payment_id = payment_link.get("id")
    db.commit()
    
    return {
        "status": "success",
        "payment_link_id": payment_link.get("id"),
        "payment_url": payment_link.get("short_url")
    }

class POSCartItem(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class POSCheckout(BaseModel):
    customer_id: Optional[int] = None
    payment_method: str  # cash, upi, card
    items: List[POSCartItem]
    total_amount: float
    coupon_code: Optional[str] = None

@router.post("/pos")
async def pos_checkout(
    checkout: POSCheckout,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """POS multi-item checkout. For UPI, returns a Razorpay payment link."""
    from app.models.product import Product
    from app.services.razorpay_service import RazorpayService

    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Resolve product names
    product_ids = [i.product_id for i in checkout.items]
    products = db.query(Product).filter(
        Product.id.in_(product_ids),
        Product.tenant_id == current_tenant_id
    ).all()
    product_map = {p.id: p for p in products}

    label_parts = []
    for item in checkout.items:
        p = product_map.get(item.product_id)
        name = p.name if p else f"Product #{item.product_id}"
        label_parts.append(f"{name} x{item.quantity}")
    product_label = ", ".join(label_parts)

    customer = None
    customer_mobile = "0000000000"
    if checkout.customer_id:
        customer = db.query(Customer).filter(
            Customer.id == checkout.customer_id,
            Customer.tenant_id == current_tenant_id
        ).first()
        if customer:
            customer_mobile = customer.mobile or customer_mobile

    new_order = Order(
        tenant_id=current_tenant_id,
        customer_id=checkout.customer_id,
        customer_mobile=customer_mobile,
        product_name=product_label,
        quantity=sum(i.quantity for i in checkout.items),
        unit_price=checkout.total_amount,
        total_amount=checkout.total_amount,
        grand_total=checkout.total_amount,
        status="completed" if checkout.payment_method in ("cash", "card") else "pending",
        payment_status="paid" if checkout.payment_method in ("cash", "card") else "pending",
        payment_method=checkout.payment_method,
        source="pos",
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    if customer:
        customer.total_spend += checkout.total_amount
        customer.order_count += 1
        customer.last_order_date = datetime.utcnow()
        db.commit()

    result: Dict[str, Any] = {
        "order_id": new_order.id,
        "payment_method": checkout.payment_method,
        "total_amount": checkout.total_amount,
        "status": new_order.status,
        "payment_status": new_order.payment_status,
        "items": [
            {
                "name": product_map.get(i.product_id).name if product_map.get(i.product_id) else f"Product #{i.product_id}",
                "quantity": i.quantity,
                "unit_price": i.unit_price,
            }
            for i in checkout.items
        ],
        "business_name": tenant.business_name,
    }

    if checkout.payment_method == "upi" and tenant.razorpay_key and tenant.razorpay_secret:
        payment_link = await RazorpayService.create_payment_link(
            tenant_id=current_tenant_id,
            order_id=new_order.id,
            amount=checkout.total_amount,
            customer_mobile=customer_mobile,
            razorpay_key=tenant.razorpay_key,
            razorpay_secret=tenant.razorpay_secret,
            business_name=tenant.business_name,
        )
        if payment_link:
            new_order.payment_id = payment_link.get("id")
            db.commit()
            result["payment_url"] = payment_link.get("short_url")
            result["payment_link_id"] = payment_link.get("id")

    request_logger.info(f"POS order {new_order.id} created for {current_tenant_id} via {checkout.payment_method}")
    return result


@router.get("/{order_id}/payment-status")
async def get_payment_status(
    order_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Poll payment status for an order — used by POS UPI flow."""
    from app.services.razorpay_service import RazorpayService

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.tenant_id == current_tenant_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.payment_status == "paid":
        return {"order_id": order_id, "payment_status": "paid"}

    if order.payment_id:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
        if tenant and tenant.razorpay_key and tenant.razorpay_secret:
            link_data = await RazorpayService.get_payment_link_status(
                payment_link_id=order.payment_id,
                razorpay_key=tenant.razorpay_key,
                razorpay_secret=tenant.razorpay_secret,
            )
            if link_data and link_data.get("status") == "paid":
                order.payment_status = "paid"
                order.status = "completed"
                db.commit()
                return {"order_id": order_id, "payment_status": "paid"}

    return {"order_id": order_id, "payment_status": order.payment_status}


class OrderCreate(BaseModel):
    customer_mobile: str
    product_name: str
    quantity: int
    unit_price: float
    total_amount: float
    sku: Optional[str] = None
    coupon_code: Optional[str] = None
    commitment_date: Optional[datetime] = None
    status: Optional[str] = "pending"  # Allow "draft" for quotations
    customer_state: Optional[str] = None
    customer_gstin: Optional[str] = None   # B2B orders
    shipping_address: Optional[str] = None

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new order and trigger the n8n workflow."""
    from app.services.n8n_service import N8NService
    from app.models.tenant import Tenant
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    try:
        # CRM Integration: Find or create customer
        customer = db.query(Customer).filter(
            Customer.tenant_id == current_tenant_id,
            Customer.mobile == order_data.customer_mobile
        ).first()
        
        if not customer:
            customer = Customer(
                tenant_id=current_tenant_id,
                mobile=order_data.customer_mobile,
                name=f"Customer-{order_data.customer_mobile[-4:]}" # Placeholder name
            )
            db.add(customer)
            db.flush() # Get customer.id
            
        # New Logic: Calculate Discounts and Snapshot Costs
        discount_value = 0.0
        unit_cost = 0.0
        sku_record = None
        
        if order_data.sku:
            from app.models.sku import ProductSKU
            sku_record = db.query(ProductSKU).filter(
                ProductSKU.tenant_id == current_tenant_id,
                ProductSKU.sku == order_data.sku
            ).first()
            if sku_record:
                unit_cost = sku_record.cost_price or 0.0

        if order_data.coupon_code:
            from app.models.coupon import Coupon
            coupon = db.query(Coupon).filter(
                Coupon.tenant_id == current_tenant_id,
                Coupon.code == order_data.coupon_code.upper(),
                Coupon.is_active == True
            ).first()
            
            if coupon:
                # Basic calculation logic (percentage or fixed)
                if coupon.discount_type == "percentage":
                    discount_value = order_data.total_amount * (coupon.discount_value / 100)
                    if coupon.max_discount_amount:
                        discount_value = min(discount_value, coupon.max_discount_amount)
                else:
                    discount_value = min(coupon.discount_value, order_data.total_amount)
                
                coupon.usage_count += 1
            else:
                request_logger.warning(f"Invalid coupon code: {order_data.coupon_code}")

        new_order = Order(
            tenant_id=current_tenant_id,
            customer_id=customer.id,
            customer_mobile=order_data.customer_mobile,
            product_name=order_data.product_name,
            sku=order_data.sku,
            quantity=order_data.quantity,
            unit_price=order_data.unit_price,
            total_amount=order_data.total_amount - discount_value,
            discount_amount=discount_value,
            coupon_code=order_data.coupon_code.upper() if order_data.coupon_code else None,
            unit_cost_at_sale=unit_cost,
            commitment_date=order_data.commitment_date,
            status=order_data.status or "pending",
            customer_state=order_data.customer_state,
            customer_gstin=order_data.customer_gstin,
            shipping_address=order_data.shipping_address,
        )

        # Auto-calculate GST at creation
        taxable_amount = order_data.total_amount - discount_value
        hsn_snapshot = None
        if order_data.sku and sku_record:
            hsn_snapshot = getattr(sku_record, 'hsn_code', None)
        tax_info = calculate_gst(
            base_amount=taxable_amount,
            merchant_state=tenant.state if hasattr(tenant, 'state') else None,
            customer_state=order_data.customer_state,
            selling_price_per_unit=order_data.unit_price,
        )
        new_order.tax_type = tax_info["tax_type"]
        new_order.gst_rate = tax_info["gst_rate"]
        new_order.tax_amount = tax_info["tax_amount"]
        new_order.cgst_amount = tax_info["cgst_amount"]
        new_order.sgst_amount = tax_info["sgst_amount"]
        new_order.igst_amount = tax_info["igst_amount"]
        new_order.grand_total = tax_info["grand_total"]
        new_order.hsn_code = hsn_snapshot or "6105"
        
        # Update Customer Lifetime Stats
        customer.total_spend += (order_data.total_amount - discount_value)
        customer.order_count += 1
        customer.last_order_date = datetime.utcnow()
        
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        # Dispatch n8n workflow trigger (background or direct)
        if tenant.n8n_webhook_url:
            import asyncio
            # We can run this in background for speed
            asyncio.create_task(N8NService.trigger_order_flow(
                tenant.n8n_webhook_url, 
                {
                    "id": new_order.id,
                    "tenant_id": new_order.tenant_id,
                    "customer_mobile": new_order.customer_mobile,
                    "product_name": new_order.product_name,
                    "total_amount": new_order.total_amount,
                    "business_name": tenant.business_name
                }
            ))
            
        request_logger.info(f"Created order {new_order.id} for tenant: {current_tenant_id}")
        return new_order
        
    except Exception as e:
        db.rollback()
        request_logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating order")


@router.get("/{order_id}/invoice", response_model=InvoiceResponse)
async def get_order_invoice(
    order_id: int,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Generate invoice data with GST breakdown."""
    order = db.query(Order).filter(Order.id == order_id, Order.tenant_id == current_tenant_id).first()
    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    
    if not order or not tenant:
        raise HTTPException(status_code=404, detail="Order or Merchant profile not found")
        
    # Calculate Tax if not already done
    tax_info = calculate_gst(
        base_amount=order.total_amount,
        merchant_state=tenant.state,
        customer_state=order.customer_state
    )
    
    # Auto-generate invoice number if missing
    if not order.invoice_number:
        order.invoice_number = f"INV-{tenant.tenant_id.upper()}-{order.id:05d}"
        order.tax_type = tax_info["tax_type"]
        order.tax_amount = tax_info["tax_amount"]
        order.grand_total = tax_info["grand_total"]
        db.commit()
    
    return {
        "order_id": order.id,
        "invoice_number": order.invoice_number,
        "business_details": {
            "name": tenant.business_name,
            "gstin": tenant.gstin,
            "address": f"{tenant.address_line1}, {tenant.city}, {tenant.state} - {tenant.pincode}"
        },
        "customer_details": {
            "mobile": order.customer_mobile,
            "address": order.shipping_address,
            "state": order.customer_state
        },
        "items": [
            {
                "name": order.product_name,
                "qty": order.quantity,
                "unit_price": order.unit_price,
                "total": order.total_amount
            }
        ],
        "tax_breakdown": tax_info,
        "grand_total": order.grand_total or tax_info["grand_total"]
    }


@router.post("/{order_id}/fulfill", response_model=FulfillmentResponse)
async def fulfill_order(
    order_id: int,
    carrier_name: str,
    tracking_number: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Record fulfillment and update order status."""
    order = db.query(Order).filter(Order.id == order_id, Order.tenant_id == current_tenant_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    fulfillment = Fulfillment(
        tenant_id=current_tenant_id,
        order_id=order_id,
        carrier_name=carrier_name,
        tracking_number=tracking_number,
        status="shipped",
        shipped_at=datetime.utcnow()
    )
    
    order.status = "completed" # Or "shipped" depending on business logic
    db.add(fulfillment)
    
    # Trigger WhatsApp Dispatch Notification
    from app.services.whatsapp_bot_service import WhatsAppBotService
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.tenant_id == current_tenant_id).first()
    if tenant and order.customer_mobile:
        import asyncio
        asyncio.create_task(WhatsAppBotService.send_dispatch_notification(
            tenant, order.customer_mobile, order.id, tracking_number
        ))
    
    db.commit()
    return fulfillment
