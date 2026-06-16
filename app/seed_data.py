"""
Seed default subscription plans and demo data.
Run this after database initialization.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.base import Base, Plan, PlanName
from datetime import datetime, timezone


def seed_plans(db: Session):
    """Create default subscription plans."""
    plans = [
        Plan(
            name=PlanName.free,
            display_name="Free",
            price_inr=0,
            price_usd=0,
            requests_per_day=100,
            max_chars_per_request=5000,
            features=["basic_cleaning", "api_access", "5_operations"],
        ),
        Plan(
            name=PlanName.starter,
            display_name="Starter",
            price_inr=999,
            price_usd=12,
            requests_per_day=1000,
            max_chars_per_request=50000,
            features=[
                "all_operations",
                "batch_processing",
                "api_keys",
                "analytics",
            ],
        ),
        Plan(
            name=PlanName.pro,
            display_name="Pro",
            price_inr=4999,
            price_usd=60,
            requests_per_day=10000,
            max_chars_per_request=500000,
            features=[
                "all_features",
                "priority_support",
                "webhooks",
                "advanced_analytics",
            ],
        ),
        Plan(
            name=PlanName.enterprise,
            display_name="Enterprise",
            price_inr=-1,  # Custom pricing
            price_usd=-1,
            requests_per_day=-1,  # Unlimited
            max_chars_per_request=-1,  # Unlimited
            features=[
                "unlimited_everything",
                "dedicated_support",
                "sso",
                "custom_integrations",
                "sla_guarantee",
            ],
        ),
    ]

    # Check if plans already exist
    for plan in plans:
        existing = db.query(Plan).filter(Plan.name == plan.name).first()
        if not existing:
            db.add(plan)
            print(f"✓ Created {plan.display_name} plan")
        else:
            print(f"- {plan.display_name} plan already exists")

    db.commit()


def init_db():
    """Initialize database and seed default data."""
    print("🗄️  Initializing database...")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

    # Seed default plans
    db = SessionLocal()
    try:
        seed_plans(db)
        print("\n✓ Database initialization complete!")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
