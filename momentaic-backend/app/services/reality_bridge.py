"""
Reality Bridge Service
Connects autonomous agent outputs to real-world execution APIs.
"""

from typing import Dict, Any, Optional
import structlog
from app.services.social.twitter import twitter_service
from app.services.social.linkedin import linkedin_service
from app.services.email_service import get_email_service
from app.agents.browser_agent import browser_agent

logger = structlog.get_logger()


class RealityBridge:
    """
    The Reality Bridge - Executes agent-generated plans in the real world.
    """
    
    def __init__(self):
        self.email_service = get_email_service()

    # ========================
    # BANSHEE BRIDGE (Social)
    # ========================
    async def execute_banshee(
        self, 
        output: Dict[str, Any], 
        social_creds: Optional[Dict[str, Any]] = None,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Execute Banshee's viral content on Twitter/LinkedIn.
        """
        thread_hook = output.get("thread_hook", "")
        thread_body = output.get("thread_body", "")
        content = f"{thread_hook}\n\n{thread_body}"
        
        if dry_run:
            logger.info("[DRY RUN] Banshee would post", content=content[:200])
            return {"status": "DRY_RUN", "content": content}
        
        result = {"twitter": None, "linkedin": None}
        
        # Twitter
        if social_creds and social_creds.get("twitter"):
            try:
                tweet_result = await twitter_service.tweet(content[:280], social_creds["twitter"])
                result["twitter"] = tweet_result
                logger.info("Banshee LIVE FIRE: Twitter", result=tweet_result)
            except Exception as e:
                logger.error("Banshee Twitter failed", error=str(e))
                result["twitter"] = {"error": str(e)}

        # LinkedIn
        if social_creds and social_creds.get("linkedin"):
            try:
                li_result = await linkedin_service.post_update(content, social_creds["linkedin"])
                result["linkedin"] = li_result
                logger.info("Banshee LIVE FIRE: LinkedIn", result=li_result)
            except Exception as e:
                logger.error("Banshee LinkedIn failed", error=str(e))
                result["linkedin"] = {"error": str(e)}
        
        return {"status": "EXECUTED", "result": result}

    # ========================
    # SNIPER BRIDGE (Email)
    # ========================
    async def execute_sniper(
        self, 
        output: Dict[str, Any], 
        target_email: Optional[str] = None,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Execute Sniper's outreach via email.
        """
        targets = output.get("targets", [])
        
        if not targets:
            return {"status": "NO_TARGETS"}
            
        # For now, use the first target's kill_shot as email content
        first_target = targets[0]
        subject = f"Quick question for {first_target.get('profile', 'you')}"
        body = first_target.get("kill_shot", "I'd love to connect.")
        
        if dry_run:
            logger.info("[DRY RUN] Sniper would send email", to=target_email, subject=subject)
            return {"status": "DRY_RUN", "to": target_email, "subject": subject, "body": body}
        
        if not target_email:
            return {"status": "NO_EMAIL_PROVIDED", "error": "Live fire requires target_email"}
            
        try:
            await self.email_service.send_email(
                to_email=target_email,
                subject=subject,
                body=body
            )
            logger.info("Sniper LIVE FIRE: Email Sent", to=target_email)
            return {"status": "EXECUTED", "to": target_email}
        except Exception as e:
            logger.error("Sniper email failed", error=str(e))
            return {"status": "FAILED", "error": str(e)}

    # ========================
    # SPY AUGMENTATION (Scraping)
    # ========================
    async def augment_spy(self, product_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide the Spy with real-time competitor intel via browser scraping.
        """
        product_name = product_context.get("name", "Unknown Product")
        
        try:
            await browser_agent.initialize()
            search_query = f"{product_name} competitors 2025"
            results = await browser_agent.search_google(search_query)
            
            intel = []
            for r in results[:3]:
                intel.append({
                    "title": r.get("title"),
                    "snippet": r.get("snippet"),
                    "link": r.get("link")
                })
            
            logger.info("Spy augmented with live intel", query=search_query, results=len(intel))
            return {"live_intel": intel}
        except Exception as e:
            logger.error("Spy augmentation failed", error=str(e))
            return {"live_intel": [], "error": str(e)}


reality_bridge = RealityBridge()
