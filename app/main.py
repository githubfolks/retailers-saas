from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.api.webhook import router as webhook_router
from app.api.auth import router as auth_router
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.coupons import router as coupons_router
from app.api.payment_webhook import router as payment_router
from app.api.admin import router as admin_router
from app.api.settings import router as settings_router
from app.api.sync import router as sync_router
from app.api.inventory import router as inventory_router
from app.api.procurement import router as procurement_router
from app.api.analytics import router as analytics_router
from app.api.odoo_webhooks import router as odoo_webhooks_router
from app.api.sku import router as sku_router
from app.api.customers import router as customers_router
from app.api.returns import router as returns_router
from app.api.categories import router as categories_router
from app.api.brands import router as brands_router
from app.api.units import router as units_router
from app.api.attributes import router as attributes_router
from app.api.seasons import router as seasons_router
from app.api.shifts import router as shifts_router
from app.api.whatsapp import router as whatsapp_router
from app.api.ai import router as ai_router
from app.middleware.request_logger import RequestLoggingMiddleware
from app.core.logger import request_logger
from app.core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.database import engine, Base
from app.core.config import settings
# Import all models to ensure they are registered with Base.metadata
from app import models

_dev_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
]

# In production set ALLOWED_ORIGINS to a comma-separated list of domains.
# In debug/dev mode the localhost list above is always included.
if settings.allowed_origins:
    origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    if settings.debug:
        origins = list(set(origins + _dev_origins))
else:
    origins = _dev_origins

app = FastAPI(
    title="Odoo SaaS API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(coupons_router)
app.include_router(payment_router)
app.include_router(admin_router)
app.include_router(settings_router)
app.include_router(sync_router)
app.include_router(inventory_router)
app.include_router(procurement_router)
app.include_router(analytics_router)
app.include_router(odoo_webhooks_router)
app.include_router(sku_router)
app.include_router(customers_router)
app.include_router(returns_router)
app.include_router(categories_router)
app.include_router(brands_router)
app.include_router(units_router)
app.include_router(attributes_router)
app.include_router(seasons_router)
app.include_router(shifts_router)
app.include_router(whatsapp_router)
app.include_router(ai_router)

# Mount static files for dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Serve admin dashboard"""
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path, media_type="text/html")


@app.get("/admin")
async def admin_panel():
    """Admin panel route"""
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path, media_type="text/html")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    request_logger.info("Application startup")
    try:
        Base.metadata.create_all(bind=engine)
        request_logger.info("Database tables initialized successfully")
    except Exception as e:
        request_logger.error(f"Error initializing database tables: {str(e)}")

    # Incremental column migrations — safe to run on every startup (IF NOT EXISTS)
    _migrations = [
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20)",
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'whatsapp'",
        "ALTER TABLE order_returns ADD COLUMN IF NOT EXISTS product_id INTEGER",
        "ALTER TABLE order_returns ADD COLUMN IF NOT EXISTS pickup_address TEXT",
        "ALTER TABLE order_returns ADD COLUMN IF NOT EXISTS return_warehouse_id INTEGER",
        "ALTER TABLE order_returns ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP",
        "ALTER TABLE order_returns ADD COLUMN IF NOT EXISTS approved_by VARCHAR",
        "ALTER TABLE order_returns ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP",
    ]
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            for stmt in _migrations:
                conn.execute(text(stmt))
            conn.commit()
        request_logger.info("Column migrations applied")
    except Exception as e:
        request_logger.error(f"Error applying column migrations: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    request_logger.info("Application shutdown")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
