import json
import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.logger import request_logger

# Paths where subscription check is skipped
_EXCLUDED_EXACT = {"/", "/health", "/docs", "/redoc", "/openapi.json", "/admin"}
_EXCLUDED_PREFIXES = (
    "/auth/",
    "/api/admin/",
    "/webhook",
    "/payment-webhook",
    "/whatsapp/",
    "/subscription/",
    "/static/",
)


class SubscriptionGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in _EXCLUDED_EXACT or any(path.startswith(p) for p in _EXCLUDED_PREFIXES):
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            return await call_next(request)

        token = auth[7:]
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            tenant_id = payload.get("tenant_id")
        except Exception:
            return await call_next(request)

        if not tenant_id:
            return await call_next(request)

        from app.core.database import SessionLocal
        from app.services.subscription_service import SubscriptionService

        db = SessionLocal()
        try:
            svc = SubscriptionService(db, tenant_id)
            sub = svc.get_or_create()
            if not svc.is_active(sub):
                request_logger.warning(f"Subscription blocked: tenant={tenant_id} status={sub.status}")
                return JSONResponse(
                    status_code=402,
                    content={
                        "error": "subscription_expired",
                        "message": "Your subscription has expired. Please upgrade to continue.",
                        "plan": sub.plan,
                        "status": sub.status,
                    },
                )
        except Exception as exc:
            request_logger.error(f"SubscriptionGuard error for tenant={tenant_id}: {exc}")
        finally:
            db.close()

        return await call_next(request)
