from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.core.database import Base
from datetime import datetime

TRIAL_DAYS = 14

PLANS = {
    "free": {
        "display_name": "Free",
        "price_monthly": 0,
        "orders_per_month": 50,
        "products": 100,
        "users": 2,
        "modules": ["pos"],
        "razorpay_plan_id": None,
    },
    "starter": {
        "display_name": "Starter",
        "price_monthly": 999,
        "orders_per_month": 500,
        "products": 1000,
        "users": 10,
        "modules": ["pos", "inventory", "reports"],
        "razorpay_plan_id": None,  # set via RAZORPAY_PLAN_STARTER in .env
    },
    "pro": {
        "display_name": "Pro",
        "price_monthly": 2999,
        "orders_per_month": -1,  # unlimited
        "products": -1,
        "users": -1,
        "modules": ["pos", "inventory", "procurement", "reports", "settings"],
        "razorpay_plan_id": None,  # set via RAZORPAY_PLAN_PRO in .env
    },
}


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), unique=True, nullable=False, index=True)

    plan = Column(String, default="free", nullable=False)
    # trial | active | past_due | cancelled | expired
    status = Column(String, default="trial", nullable=False)

    trial_ends_at = Column(DateTime, nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)

    razorpay_subscription_id = Column(String, nullable=True, index=True)
    razorpay_customer_id = Column(String, nullable=True)

    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
