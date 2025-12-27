"""
Open Source Strategy Service
How entrepreneurs can self-host MomentAIc
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class PricingTier:
    """Pricing tier definition"""
    name: str
    price_monthly: float
    features: List[str]
    limits: Dict[str, int]
    description: str


class OpenSourceStrategy:
    """
    MomentAIc Open Source Strategy
    
    Core open source + paid managed service
    
    Philosophy:
    - Free to download and run
    - Community contributions rewarded
    - Paid managed version with premium features
    - Revenue share accelerator option
    """
    
    # Pricing tiers (as approved)
    TIERS = {
        "starter": PricingTier(
            name="Starter",
            price_monthly=9.0,
            description="For solo founders testing the waters",
            features=[
                "All 16 AI agents",
                "5 integrations",
                "Basic triggers",
                "Community support",
                "Traction score",
            ],
            limits={
                "agents": 16,
                "integrations": 5,
                "triggers": 10,
                "messages_per_month": 1000,
            }
        ),
        "pro": PricingTier(
            name="Pro",
            price_monthly=19.0,
            description="For serious builders ready to scale",
            features=[
                "Everything in Starter",
                "All 42+ integrations",
                "Unlimited triggers",
                "Browser agent",
                "Deep Research",
                "Priority AI models",
                "Leaderboard featured",
            ],
            limits={
                "agents": 16,
                "integrations": 42,
                "triggers": -1,  # Unlimited
                "messages_per_month": 10000,
            }
        ),
        "scale": PricingTier(
            name="Scale",
            price_monthly=99.0,
            description="For funded startups going big",
            features=[
                "Everything in Pro",
                "Custom agents",
                "API access",
                "White-label option",
                "Dedicated support",
                "Team seats (5)",
                "Investment memo generator",
            ],
            limits={
                "agents": -1,  # Unlimited custom
                "integrations": -1,
                "triggers": -1,
                "messages_per_month": -1,
                "team_seats": 5,
            }
        ),
        "accelerator": PricingTier(
            name="Accelerator",
            price_monthly=0,  # Revenue share model
            description="Anti-YC: Performance-based, not equity grab",
            features=[
                "Everything in Scale",
                "Human mentor network",
                "Investor introductions",
                "Featured showcase",
                "Priority co-founder matching",
                "1% equity OR 5% revenue share for 12mo",
                "No predatory terms",
            ],
            limits={
                "agents": -1,
                "integrations": -1,
                "triggers": -1,
                "messages_per_month": -1,
                "team_seats": 10,
            }
        )
    }
    
    @classmethod
    def get_tier(cls, tier_name: str) -> PricingTier:
        """Get pricing tier by name"""
        return cls.TIERS.get(tier_name)
    
    @classmethod
    def get_all_tiers(cls) -> List[Dict[str, Any]]:
        """Get all tiers for pricing page"""
        return [
            {
                "id": name,
                "name": tier.name,
                "price": tier.price_monthly,
                "description": tier.description,
                "features": tier.features,
                "limits": tier.limits,
                "popular": name == "pro"
            }
            for name, tier in cls.TIERS.items()
        ]
    
    @staticmethod
    def get_self_hosted_guide() -> Dict[str, Any]:
        """
        Self-hosted deployment guide
        
        Open source core can be deployed anywhere
        """
        return {
            "title": "Self-Host MomentAIc",
            "description": "Run the full AI co-founder stack on your own infrastructure",
            "requirements": {
                "python": "3.11+",
                "postgres": "16+ with pgvector",
                "redis": "7+",
                "memory": "4GB minimum",
                "storage": "20GB SSD"
            },
            "quick_start": """
# Clone the repo
git clone https://github.com/momentaic/momentaic.git
cd momentaic

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run with Docker
docker-compose up -d

# Or run locally
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
""",
            "docker_compose": """
version: '3.8'
services:
  momentaic:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/momentaic
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: momentaic
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
""",
            "api_keys_needed": [
                {"name": "GOOGLE_API_KEY", "description": "For Gemini AI", "required": True},
                {"name": "STRIPE_SECRET_KEY", "description": "For payments integration", "required": False},
                {"name": "GITHUB_TOKEN", "description": "For GitHub integration", "required": False},
            ],
            "contribution": {
                "how_to_contribute": "https://github.com/momentaic/momentaic/CONTRIBUTING.md",
                "rewards": [
                    "Major feature: Free Pro for life",
                    "New integration: $500 bounty + Pro for 1 year",
                    "Bug fix: Pro for 3 months",
                    "Documentation: Pro for 1 month"
                ],
                "community": {
                    "discord": "https://discord.gg/momentaic",
                    "github": "https://github.com/momentaic/momentaic"
                }
            }
        }
    
    @staticmethod
    def get_license_info() -> Dict[str, Any]:
        """License information for open source"""
        return {
            "license": "MIT",
            "commercial_use": True,
            "modification": True,
            "distribution": True,
            "patent_use": True,
            "private_use": True,
            "conditions": [
                "License and copyright notice must be included"
            ],
            "limitations": [
                "No liability",
                "No warranty"
            ],
            "note": "The open source version includes all core features. Managed cloud adds convenience, priority support, and premium AI models."
        }


# Export
def get_pricing_tiers() -> List[Dict[str, Any]]:
    """Get all pricing tiers"""
    return OpenSourceStrategy.get_all_tiers()


def get_self_hosted_guide() -> Dict[str, Any]:
    """Get self-hosted deployment guide"""
    return OpenSourceStrategy.get_self_hosted_guide()
