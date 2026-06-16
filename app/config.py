from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "AI Text Cleaning API"
    debug: bool = False

    # Database
    database_url: str = "postgresql://postgres:postgres@db:5432/aitextcleaning"

    # JWT
    secret_key: str = "changeme-use-a-long-random-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Razorpay
    razorpay_key_id: str = "rzp_test_T1w7yaAecz6ChcR"
    razorpay_key_secret: str = "sN6GdDR1OVEhDLBWWzOY5q3D"
    razorpay_webhook_secret: str = ""

    # Cashfree
    cashfree_app_id: str = ""
    cashfree_secret_key: str = ""
    cashfree_environment: str = "sandbox"  # "sandbox" or "production"
    cashfree_webhook_secret: str = ""

    # Base URL (used for payment return URLs)
    base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
