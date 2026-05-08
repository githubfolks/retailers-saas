from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.subscription import Subscription, PLANS, TRIAL_DAYS
from app.core.logger import request_logger


class SubscriptionService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def get_or_create(self) -> Subscription:
        sub = self.db.query(Subscription).filter(
            Subscription.tenant_id == self.tenant_id
        ).first()
        if not sub:
            sub = self._create_trial()
        return sub

    def _create_trial(self) -> Subscription:
        sub = Subscription(
            tenant_id=self.tenant_id,
            plan="free",
            status="trial",
            trial_ends_at=datetime.utcnow() + timedelta(days=TRIAL_DAYS),
        )
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        request_logger.info(f"Trial subscription created for tenant {self.tenant_id}")
        return sub

    def is_active(self, sub: Subscription) -> bool:
        now = datetime.utcnow()
        if sub.status == "trial":
            return sub.trial_ends_at is not None and sub.trial_ends_at > now
        if sub.status == "active":
            return sub.current_period_end is None or sub.current_period_end > now
        if sub.status == "cancelled":
            # Access until end of paid period
            return sub.current_period_end is not None and sub.current_period_end > now
        return False  # past_due, expired

    def can_access_module(self, sub: Subscription, module: str) -> bool:
        plan_config = PLANS.get(sub.plan, PLANS["free"])
        return module in plan_config["modules"]

    def check_order_limit(self, sub: Subscription) -> tuple:
        """Returns (within_limit, used, limit)."""
        plan_config = PLANS.get(sub.plan, PLANS["free"])
        limit = plan_config["orders_per_month"]
        if limit == -1:
            return True, 0, -1
        from app.models.order import Order
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        used = self.db.query(func.count(Order.id)).filter(
            Order.tenant_id == self.tenant_id,
            Order.created_at >= month_start,
        ).scalar() or 0
        return used < limit, used, limit

    def check_product_limit(self, sub: Subscription) -> tuple:
        """Returns (within_limit, used, limit)."""
        plan_config = PLANS.get(sub.plan, PLANS["free"])
        limit = plan_config["products"]
        if limit == -1:
            return True, 0, -1
        from app.models.product import Product
        used = self.db.query(func.count(Product.id)).filter(
            Product.tenant_id == self.tenant_id,
        ).scalar() or 0
        return used < limit, used, limit

    def activate(self, plan: str, razorpay_subscription_id: str,
                 razorpay_customer_id: str, period_end: datetime) -> Subscription:
        sub = self.get_or_create()
        sub.plan = plan
        sub.status = "active"
        sub.razorpay_subscription_id = razorpay_subscription_id
        sub.razorpay_customer_id = razorpay_customer_id
        sub.current_period_start = datetime.utcnow()
        sub.current_period_end = period_end
        sub.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(sub)
        request_logger.info(f"Subscription activated: tenant={self.tenant_id} plan={plan}")
        return sub

    def renew(self, period_end: datetime) -> Subscription:
        sub = self.get_or_create()
        sub.status = "active"
        sub.current_period_start = datetime.utcnow()
        sub.current_period_end = period_end
        sub.updated_at = datetime.utcnow()
        self.db.commit()
        request_logger.info(f"Subscription renewed: tenant={self.tenant_id} until={period_end}")
        return sub

    def mark_past_due(self) -> Subscription:
        sub = self.get_or_create()
        sub.status = "past_due"
        sub.updated_at = datetime.utcnow()
        self.db.commit()
        request_logger.warning(f"Subscription past_due: tenant={self.tenant_id}")
        return sub

    def cancel(self) -> Subscription:
        sub = self.get_or_create()
        sub.status = "cancelled"
        sub.cancelled_at = datetime.utcnow()
        sub.updated_at = datetime.utcnow()
        self.db.commit()
        request_logger.info(f"Subscription cancelled: tenant={self.tenant_id}")
        return sub

    def set_plan_manual(self, plan: str, status: str = "active", days: int = 30) -> Subscription:
        """Admin override — set plan without Razorpay."""
        if plan not in PLANS:
            raise ValueError(f"Unknown plan: {plan}")
        sub = self.get_or_create()
        sub.plan = plan
        sub.status = status
        sub.current_period_start = datetime.utcnow()
        sub.current_period_end = datetime.utcnow() + timedelta(days=days)
        sub.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(sub)
        request_logger.info(f"Subscription manually set: tenant={self.tenant_id} plan={plan} status={status}")
        return sub

    def days_remaining(self, sub: Subscription) -> int:
        now = datetime.utcnow()
        if sub.status == "trial" and sub.trial_ends_at:
            return max(0, (sub.trial_ends_at - now).days)
        if sub.current_period_end:
            return max(0, (sub.current_period_end - now).days)
        return 0
