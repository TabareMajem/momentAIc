
import structlog
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.startup import Startup
from app.models.action_item import ActionItem, ActionStatus, ActionPriority
from app.agents.sales_agent import sales_agent
from app.agents.marketing_agent import marketing_agent
from app.agents.competitor_intel_agent import competitor_intel_agent

logger = structlog.get_logger()

class MorningBriefService:
    """
    Orchestrates the daily "Morning Brief" - a massive autonomous run of all agents.
    Runs at 6:00 AM UTC.
    """
    
    async def generate_daily_brief(self):
        """
        Main entry point. triggered by Scheduler.
        Iterates all active startups and runs autonomous agents.
        """
        logger.info("MorningBrief: Starting global daily brief generation")
        
        async with async_session_maker() as db:
            # 1. Get all active startups owned by Pro+ users
            from app.models.user import User
            
            # Subquery or join to find startups where owner has tier >= growth
            # Assuming 'tier' is on User model
            result = await db.execute(
                select(Startup)
                .join(User, Startup.owner_id == User.id)
                .where(User.tier.in_(['growth', 'god_mode']))
            ) 
            startups = result.scalars().all()
            
            logger.info(f"MorningBrief: Processing {len(startups)} startups")
            
            for startup in startups:
                try:
                    await self.process_startup(db, startup)
                except Exception as e:
                    logger.error("MorningBrief: Failed for startup", startup_id=str(startup.id), error=str(e))
                    
        logger.info("MorningBrief: Completed global generation")

    async def process_startup(self, db: AsyncSession, startup: Startup):
        """
        Run autonomous agents for a single startup
        """
        user_id = str(startup.owner_id) # Using owner as the primary usercontext
        
        # Context building
        context = {
            "name": startup.name,
            "description": startup.description,
            "industry": startup.industry,
            "tagline": startup.tagline
        }
        
        # --- AGENT 1: SALES HUNTER ---
        # "I found 5 leads"
        try:
            sales_result = await sales_agent.auto_hunt(context, user_id)
            if sales_result and not sales_result.get("error"):
                item = ActionItem(
                    startup_id=startup.id,
                    source_agent="SalesHunter",
                    title=f"Drafted outreach for {len(sales_result.get('leads', []))} new leads",
                    description=f"Identified {len(sales_result.get('leads', []))} high-value prospects from LinkedIn matching your ICP. Outreach emails drafted.",
                    priority="high",
                    payload=sales_result, # Contains the leads and drafts
                    status="pending"
                )
                db.add(item)
        except Exception as e:
            logger.error("MorningBrief: Sales Agent failed", error=str(e))

        # --- AGENT 2: MARKETING TRENDS ---
        # "I found a trending topic"
        try:
            marketing_result = await marketing_agent.generate_daily_ideas(context)
            if marketing_result and not marketing_result.get("error"):
                 item = ActionItem(
                    startup_id=startup.id,
                    source_agent="MarketingAgent",
                    title=f"Viral Opportunity: {marketing_result.get('topic')}",
                    description=f"Trending topic detected on X/LinkedIn. Drafted 3 variations to hijack the conversation.",
                    priority="medium",
                    payload=marketing_result,
                    status="pending"
                )
                 db.add(item)
        except Exception as e:
             logger.error("MorningBrief: Marketing Agent failed", error=str(e))

        # --- AGENT 3: COMPETITOR INTEL ---
        # "I found a threat" or "I mapped the landscape"
        intel_result = None
        try:
            # Load known competitors from settings
            current_settings = dict(startup.settings or {})
            known_competitors = current_settings.get("competitors", [])
            
            intel_result = await competitor_intel_agent.monitor_market(context, known_competitors)
            if intel_result and not intel_result.get("error"):
                
                # Case A: Discovery (New Competitors Found)
                if intel_result.get("mode") == "discovery":
                    new_comps = intel_result.get("new_competitors", [])
                    if new_comps:
                        # Persist to settings
                        current_settings["competitors"] = new_comps
                        startup.settings = current_settings
                        
                        db.add(item := ActionItem(
                            startup_id=startup.id,
                            source_agent="CompetitorIntel",
                            title=f"Market Map: Identified {len(new_comps)} Competitors",
                            description=f"Auto-discovered key players in your space: {', '.join(new_comps[:3])}...",
                            priority="high",
                            payload=intel_result,
                            status="pending"
                        ))
                
                # Case B: Surveillance (Alerts Found)
                elif intel_result.get("mode") == "surveillance":
                    updates = intel_result.get("updates", [])
                    if updates:
                        db.add(item := ActionItem(
                            startup_id=startup.id,
                            source_agent="CompetitorIntel",
                            title=f"Competitor Alert: {len(updates)} Updates",
                            description="\n".join(updates),
                            priority="high",
                            payload=intel_result,
                            status="pending"
                        ))
                        
        except Exception as e:
             logger.error("MorningBrief: Competitor Agent failed", error=str(e))

        # --- AGENT 4: ACQUISITION (PAID ADS) ---
        # "I generated an ad campaign"
        acquisition_result = None
        try:
            # We assume user wants growth
            # Randomize platform focus based on day or context? Or just ask for general.
            campaign_context = {**context, "target_audience": "SMB Owners and Startups"}
            
            from app.agents.acquisition_agent import acquisition_agent
            acquisition_result = await acquisition_agent.generate_ad_campaign(campaign_context)
            
            if acquisition_result and not acquisition_result.get("error"):
                 item = ActionItem(
                    startup_id=startup.id,
                    source_agent="AcquisitionAgent",
                    title=f"Paid Ad: {acquisition_result.get('headline', 'New Campaign')}",
                    description=f"Ready-to-launch {acquisition_result.get('platform', 'Ad')} campaign targeting {', '.join(acquisition_result.get('targeting', [])[:3])}.",
                    priority="medium",
                    payload=acquisition_result,
                    status="pending"
                )
                 db.add(item)
        except Exception as e:
             logger.error("MorningBrief: Acquisition Agent failed", error=str(e))

        await db.commit()
        
        # --- NOTIFICATION ---
        try:
            from app.services.notification_service import notification_service
            from app.models.user import User
            
            # Fetch user email etc
            user = await db.get(User, startup.owner_id)
            if user:
                total_items = (1 if sales_result else 0) + (1 if marketing_result else 0) + (1 if intel_result else 0) + (1 if acquisition_result else 0)
                if total_items > 0:
                    intel_summary = "No alerts"
                    if intel_result:
                         if intel_result.get("mode") == "discovery":
                             intel_summary = f"Mapped {len(intel_result.get('new_competitors', []))} competitors"
                         elif intel_result.get("updates"):
                             intel_summary = f"{len(intel_result.get('updates'))} alerts found"

                    subject = f"🚀 {startup.name} Morning Brief: {total_items} Actions Ready"
                    body = f"""Good morning!

You have {total_items} new opportunities waiting:
- Sales Hunter: {len(sales_result.get('leads', [])) if sales_result else 0} new leads
- Marketing: {marketing_result.get('topic') if marketing_result else 'No trends'}
- Competitor Intel: {intel_summary}
- Paid Ads: {acquisition_result.get('platform') if acquisition_result else 'No campaign'}

One-Click Approve in Command Center."""

                    await notification_service.notify_user(
                        user=user,
                        subject=subject,
                        body=body,
                        action_url="https://app.momentaic.com/dashboard",
                        db=db
                    )
                    logger.info("MorningBrief: Sent notification", user=user.email)
        except Exception as e:
            logger.error("MorningBrief: Notification failed", error=str(e))

morning_brief_service = MorningBriefService()
