import hmac
import hashlib
import json
import requests as http_requests
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.api.auth import get_current_user, check_owner
from app.models.subscription import Subscription, PLANS
from app.services.subscription_service import SubscriptionService
from app.core.config import settings

router = APIRouter(prefix="/subscription", tags=["subscription"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class UpgradeRequest(BaseModel):
    plan: str  # "starter" or "pro"
    customer_name: str
    customer_email: str
    customer_contact: str


class ManualPlanRequest(BaseModel):
    plan: str
    status: str = "active"
    days: int = 30


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/plans")
def list_plans():
    """Return all available plan tiers and their limits."""
    return [
        {
            "plan": k,
            "display_name": v["display_name"],
            "price_monthly": v["price_monthly"],
            "orders_per_month": v["orders_per_month"],
            "products": v["products"],
            "users": v["users"],
            "modules": v["modules"],
        }
        for k, v in PLANS.items()
    ]


@router.get("/")
def get_subscription(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current subscription status for the authenticated tenant."""
    tenant_id = user["tenant_id"]
    svc = SubscriptionService(db, tenant_id)
    sub = svc.get_or_create()

    within_limit, orders_used, orders_limit = svc.check_order_limit(sub)
    _, products_used, products_limit = svc.check_product_limit(sub)

    return {
        "plan": sub.plan,
        "status": sub.status,
        "is_active": svc.is_active(sub),
        "days_remaining": svc.days_remaining(sub),
        "trial_ends_at": sub.trial_ends_at,
        "current_period_end": sub.current_period_end,
        "usage": {
            "orders_this_month": orders_used,
            "orders_limit": orders_limit,
            "products": products_used,
            "products_limit": products_limit,
        },
        "modules": PLANS.get(sub.plan, PLANS["free"])["modules"],
    }


@router.post("/upgrade")
def upgrade_plan(
    body: UpgradeRequest,
    user: dict = Depends(check_owner),
    db: Session = Depends(get_db),
):
    """Initiate a Razorpay subscription for a paid plan. Returns checkout URL."""
    if body.plan not in ("starter", "pro"):
        raise HTTPException(400, "Invalid plan. Choose 'starter' or 'pro'")

    plan_config = PLANS[body.plan]
    razorpay_plan_id = plan_config.get("razorpay_plan_id") or getattr(
        settings, f"razorpay_plan_{body.plan}", None
    )
    if not razorpay_plan_id:
        raise HTTPException(
            400,
            f"Razorpay plan ID not configured for '{body.plan}'. "
            f"Set RAZORPAY_PLAN_{body.plan.upper()} in .env",
        )

    razorpay_secret = getattr(settings, "razorpay_secret", "")
    auth = (settings.razorpay_key, razorpay_secret)

    # Create/find Razorpay customer
    customer_resp = http_requests.post(
        "https://api.razorpay.com/v1/customers",
        json={
            "name": body.customer_name,
            "email": body.customer_email,
            "contact": body.customer_contact,
            "fail_existing": 0,
        },
        auth=auth,
    )
    if customer_resp.status_code not in (200, 201):
        raise HTTPException(502, f"Razorpay customer creation failed: {customer_resp.text}")
    customer_id = customer_resp.json()["id"]

    # Create Razorpay subscription
    sub_resp = http_requests.post(
        "https://api.razorpay.com/v1/subscriptions",
        json={
            "plan_id": razorpay_plan_id,
            "customer_id": customer_id,
            "total_count": 12,
            "quantity": 1,
            "customer_notify": 1,
        },
        auth=auth,
    )
    if sub_resp.status_code not in (200, 201):
        raise HTTPException(502, f"Razorpay subscription creation failed: {sub_resp.text}")

    data = sub_resp.json()
    return {
        "razorpay_subscription_id": data["id"],
        "short_url": data.get("short_url"),
        "status": data["status"],
        "plan": body.plan,
        "amount_monthly": plan_config["price_monthly"],
    }


@router.post("/cancel")
def cancel_subscription(
    user: dict = Depends(check_owner),
    db: Session = Depends(get_db),
):
    """Cancel the current paid subscription (access continues until period end)."""
    tenant_id = user["tenant_id"]
    svc = SubscriptionService(db, tenant_id)
    sub = svc.get_or_create()

    if sub.status not in ("active", "past_due"):
        raise HTTPException(400, "No active subscription to cancel")

    if sub.razorpay_subscription_id:
        razorpay_secret = getattr(settings, "razorpay_secret", "")
        auth = (settings.razorpay_key, razorpay_secret)
        http_requests.post(
            f"https://api.razorpay.com/v1/subscriptions/{sub.razorpay_subscription_id}/cancel",
            json={"cancel_at_cycle_end": 1},
            auth=auth,
        )

    svc.cancel()
    return {
        "status": "cancelled",
        "access_until": sub.current_period_end,
        "message": "Subscription cancelled. Access continues until end of current billing period.",
    }


@router.post("/webhook")
async def subscription_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay subscription lifecycle webhook events."""
    body_bytes = await request.body()

    webhook_secret = getattr(settings, "razorpay_webhook_secret", "")
    if webhook_secret:
        sig = request.headers.get("X-Razorpay-Signature", "")
        expected = hmac.new(webhook_secret.encode(), body_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise HTTPException(400, "Invalid webhook signature")

    event = json.loads(body_bytes)
    event_type = event.get("event", "")
    payload = event.get("payload", {}).get("subscription", {}).get("entity", {})
    razorpay_sub_id = payload.get("id")

    if not razorpay_sub_id:
        return {"status": "ignored"}

    sub = db.query(Subscription).filter(
        Subscription.razorpay_subscription_id == razorpay_sub_id
    ).first()
    if not sub:
        return {"status": "not_found"}

    svc = SubscriptionService(db, sub.tenant_id)

    if event_type == "subscription.activated":
        period_end = datetime.utcfromtimestamp(payload.get("current_end", 0))
        plan = _plan_from_razorpay_id(payload.get("plan_id", ""))
        svc.activate(plan, razorpay_sub_id, payload.get("customer_id", ""), period_end)

    elif event_type == "subscription.charged":
        period_end = datetime.utcfromtimestamp(payload.get("current_end", 0))
        svc.renew(period_end)

    elif event_type in ("subscription.payment_failed", "subscription.halted"):
        svc.mark_past_due()

    elif event_type in ("subscription.cancelled", "subscription.completed"):
        svc.cancel()

    return {"status": "ok", "event": event_type}


# ── Admin helpers (no auth — called from admin API) ───────────────────────────

def admin_set_plan(tenant_id: str, body: ManualPlanRequest, db: Session) -> dict:
    """Used by admin router to manually override a tenant's plan."""
    svc = SubscriptionService(db, tenant_id)
    sub = svc.set_plan_manual(body.plan, body.status, body.days)
    return {
        "tenant_id": tenant_id,
        "plan": sub.plan,
        "status": sub.status,
        "current_period_end": sub.current_period_end,
    }


def _plan_from_razorpay_id(razorpay_plan_id: str) -> str:
    for plan_name, config in PLANS.items():
        if config.get("razorpay_plan_id") == razorpay_plan_id:
            return plan_name
    return "starter"
