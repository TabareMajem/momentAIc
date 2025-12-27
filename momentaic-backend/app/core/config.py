"""
MomentAIc Configuration Settings
Pydantic-based settings management with environment variable support
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "MomentAIc"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = Field(..., min_length=32)
    api_v1_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # JWT Auth
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # AI Providers
    google_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None

    # External APIs
    serper_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None

    # Stripe
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_starter_price_id: Optional[str] = None
    stripe_growth_price_id: Optional[str] = None
    stripe_god_mode_price_id: Optional[str] = None
    
    # Stripe Connect (for Ambassador Program)
    stripe_connect_client_id: Optional[str] = None
    stripe_connect_webhook_secret: Optional[str] = None
    
    # Ambassador Program
    ambassador_commission_micro: float = 0.20   # 20% for <10k followers
    ambassador_commission_mid: float = 0.25    # 25% for 10k-100k followers
    ambassador_commission_macro: float = 0.30  # 30% for >100k followers
    ambassador_chargeback_hold_days: int = 30  # Days to hold for chargebacks
    ambassador_min_payout: float = 25.0        # Minimum payout amount

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@momentaic.com"
    smtp_from_name: str = "MomentAIc"

    # OAuth Integrations
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None

    # Credits Configuration (monthly limits per tier)
    default_starter_credits: int = 100      # $9/mo - Starter tier
    default_growth_credits: int = 500       # $19/mo - Builder tier
    default_god_mode_credits: int = 2000    # $39/mo - Founder tier
    credit_cost_signal_calc: int = 5
    credit_cost_agent_chat: int = 1
    credit_cost_content_gen: int = 3
    credit_cost_outreach_gen: int = 2
    credit_cost_vision_portal: int = 20
    credit_cost_forge_run: int = 10

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    # Sentry
    sentry_dsn: Optional[str] = None

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
