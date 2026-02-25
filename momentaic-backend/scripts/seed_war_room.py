"""
MomentAIc GTM: War Room Seed Script
Seeds the production database with 3 realistic demo startups and rich data.
Run: docker exec -it momentaic-api-prod python scripts/seed_war_room.py
"""

import asyncio
import uuid
from datetime import datetime, timedelta
import random


async def seed():
    # Lazy imports so this script works inside the Docker container
    from app.core.database import async_session_maker
    from app.models.startup import Startup, Signal, StartupStage
    from app.models.growth import Lead, LeadStatus, ContentItem
    from app.models.user import User
    from app.models.action_item import ActionItem
    from sqlalchemy import select

    async with async_session_maker() as db:
        # Find the admin user
        result = await db.execute(
            select(User).where(User.email == "tabaremajem@gmail.com")
        )
        admin = result.scalar_one_or_none()

        if not admin:
            print("❌ Admin user tabaremajem@gmail.com not found. Aborting.")
            return

        print(f"✅ Found admin user: {admin.email} (id={admin.id})")

        # ─── STARTUP DEFINITIONS ───
        startups_data = [
            {
                "name": "NovaPay",
                "tagline": "Instant cross-border payments for emerging markets",
                "description": "NovaPay provides real-time cross-border payment infrastructure for African and LatAm fintech companies. We reduce settlement times from 3 days to under 30 seconds using stablecoin rails.",
                "industry": "Fintech",
                "stage": StartupStage.PMF,
                "metrics": {"mrr": 42000, "dau": 1850, "runway_months": 14, "burn_rate": 35000, "arr": 504000},
                "website_url": "https://novapay.io",
            },
            {
                "name": "HealthStack AI",
                "tagline": "AI-powered clinical decision support",
                "description": "HealthStack AI uses large language models fine-tuned on 2M+ medical records to provide real-time clinical decision support for emergency physicians. Reduces diagnostic errors by 40%.",
                "industry": "Healthcare",
                "stage": StartupStage.MVP,
                "metrics": {"mrr": 8500, "dau": 320, "runway_months": 9, "burn_rate": 55000, "arr": 102000},
                "website_url": "https://healthstack.ai",
            },
            {
                "name": "GreenRoute",
                "tagline": "Carbon-optimized logistics for last-mile delivery",
                "description": "GreenRoute optimizes last-mile delivery routes to minimize carbon emissions while reducing fuel costs by 25%. Used by 3 Fortune 500 retailers across 12 cities.",
                "industry": "Climate / Logistics",
                "stage": StartupStage.SCALING,
                "metrics": {"mrr": 125000, "dau": 4200, "runway_months": 22, "burn_rate": 80000, "arr": 1500000},
                "website_url": "https://greenroute.earth",
            },
        ]

        # ─── SEED STARTUPS ───
        created_startups = []
        for s_data in startups_data:
            # Check if already exists
            existing = await db.execute(
                select(Startup).where(Startup.name == s_data["name"])
            )
            if existing.scalar_one_or_none():
                print(f"  ⏭️  Startup '{s_data['name']}' already exists, skipping.")
                continue

            startup = Startup(
                id=uuid.uuid4(),
                owner_id=admin.id,
                name=s_data["name"],
                tagline=s_data["tagline"],
                description=s_data["description"],
                industry=s_data["industry"],
                stage=s_data["stage"],
                metrics=s_data["metrics"],
                website_url=s_data["website_url"],
            )
            db.add(startup)
            created_startups.append(startup)
            print(f"  ✅ Created startup: {startup.name}")

        await db.flush()

        # ─── SEED SIGNALS ───
        for startup in created_startups:
            mrr = startup.metrics.get("mrr", 10000)
            for i in range(4):
                days_ago = i * 7
                sig = Signal(
                    id=uuid.uuid4(),
                    startup_id=startup.id,
                    tech_velocity=round(random.uniform(55, 95), 1),
                    pmf_score=round(random.uniform(40, 90), 1),
                    growth_momentum=round(random.uniform(50, 92), 1),
                    runway_health=round(random.uniform(60, 95), 1),
                    overall_score=round(random.uniform(55, 88), 1),
                    raw_data={
                        "commits_7d": random.randint(20, 80),
                        "commits_prev_7d": random.randint(15, 60),
                        "mrr_growth": round(random.uniform(0.05, 0.25), 2),
                    },
                    ai_insights=f"Strong {'upward' if i % 2 == 0 else 'steady'} trajectory. {'Recommend doubling paid acquisition spend.' if i == 0 else 'Monitor churn rate closely.'}",
                    recommendations=[
                        "Increase outbound email volume by 30%",
                        "Launch referral program for power users",
                        "A/B test pricing page copy",
                    ],
                    calculated_at=datetime.utcnow() - timedelta(days=days_ago),
                )
                db.add(sig)
            print(f"  📊 Seeded 4 signals for {startup.name}")

        # ─── SEED LEADS ───
        lead_templates = [
            {"company": "Stripe", "name": "Sarah Chen", "email": "s.chen@stripe.com", "pain": "Looking for emerging market payment rails"},
            {"company": "Shopify", "name": "Marcus Obi", "email": "m.obi@shopify.com", "pain": "Need faster settlement for international merchants"},
            {"company": "Airbnb", "name": "Priya Sharma", "email": "p.sharma@airbnb.com", "pain": "Cross-border host payouts are too slow"},
            {"company": "Wise", "name": "Tom Kreig", "email": "t.kreig@wise.com", "pain": "Looking for stablecoin integration partners"},
            {"company": "Nubank", "name": "Ana Ferreira", "email": "a.ferreira@nubank.com", "pain": "Expanding LatAm payment capabilities"},
            {"company": "Mayo Clinic", "name": "Dr. James Liu", "email": "j.liu@mayo.edu", "pain": "Reducing diagnostic latency in the ER"},
            {"company": "Kaiser", "name": "Rachel Gomez", "email": "r.gomez@kaiser.org", "pain": "AI triage for telehealth patients"},
            {"company": "Amazon Logistics", "name": "Kevin Park", "email": "k.park@amazon.com", "pain": "Need to hit ESG targets for last-mile delivery"},
            {"company": "DHL", "name": "Hans Mueller", "email": "h.mueller@dhl.com", "pain": "Route optimization for urban delivery"},
            {"company": "FedEx", "name": "Lisa Wong", "email": "l.wong@fedex.com", "pain": "Carbon reporting for Scope 3 emissions"},
        ]

        for i, startup in enumerate(created_startups):
            # Assign 3-4 leads per startup based on index
            start_idx = i * 3
            end_idx = start_idx + random.randint(3, 4)
            for lt in lead_templates[start_idx:min(end_idx, len(lead_templates))]:
                lead = Lead(
                    id=uuid.uuid4(),
                    startup_id=startup.id,
                    company_name=lt["company"],
                    contact_name=lt["name"],
                    contact_email=lt["email"],
                    status=random.choice([LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.QUALIFIED]),
                    source="ai_hunter",
                    score=random.randint(65, 98),
                    notes=f"Pain point: {lt['pain']}\n\nDraft Outreach:\nHi {lt['name'].split()[0]}, I noticed {lt['company']} is {lt['pain'].lower()}. We've helped similar companies achieve 10x faster settlement...",
                )
                db.add(lead)
            print(f"  🎯 Seeded leads for {startup.name}")

        # ─── SEED ACTION ITEMS ───
        action_templates = [
            ("Launch referral program for power users", "growth", "pending"),
            ("Schedule demo with enterprise prospect", "sales", "approved"),
            ("Audit landing page conversion funnel", "marketing", "pending"),
            ("Review Q1 financial projections", "finance", "completed"),
            ("Deploy v2.1 hotfix for payment timeout", "engineering", "completed"),
            ("Onboard 3 new beta testers from waitlist", "product", "pending"),
        ]

        for i, startup in enumerate(created_startups):
            for j in range(2):
                tpl = action_templates[(i * 2 + j) % len(action_templates)]
                ai = ActionItem(
                    id=uuid.uuid4(),
                    startup_id=startup.id,
                    title=tpl[0],
                    description=f"Auto-generated by the {tpl[1].upper()} agent during the daily ISP run.",
                    category=tpl[1],
                    status=tpl[2],
                    priority="high" if j == 0 else "medium",
                    source_agent=f"{tpl[1]}_agent",
                    created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                )
                db.add(ai)
            print(f"  ⚡ Seeded action items for {startup.name}")

        await db.commit()
        print("\n🚀 WAR ROOM SEEDING COMPLETE!")
        print(f"   Created {len(created_startups)} startups with signals, leads, and action items.")


if __name__ == "__main__":
    asyncio.run(seed())
