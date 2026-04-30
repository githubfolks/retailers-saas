from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Odoo SaaS API"
    postgres_url: str
    whatsapp_verify_token: str
    odoo_url: str
    razorpay_key: str
    secret_key: str
    redis_url: str = "redis://redis:6379"
    admin_password: str = "admin123"
    admin_token: str = "change-this-admin-token-in-production"
    allowed_origins: str = ""  # Comma-separated list of allowed CORS origins
    debug: bool = False
    app_base_url: str = "http://localhost:9000"  # Set to your public domain in production
    
    # Inventory System Settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    forecast_lookback_days: int = 365
    low_stock_alert_threshold: float = 0.2
    demand_forecast_min_confidence: float = 0.7
    inventory_sync_interval_minutes: int = 15
    alert_check_interval_minutes: int = 60
    notification_send_interval_minutes: int = 5
    
    # SMTP Email Settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Inventory System"

    # Ports
    fastapi_port: int = 9000
    redis_port: int = 6380
    odoo_port: int = 8069

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
