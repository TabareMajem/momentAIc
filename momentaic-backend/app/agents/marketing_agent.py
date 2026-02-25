"""
Marketing Agent
AI-powered marketing distribution & growth hacking
Upgraded to BaseAgent with structured outputs, memory context, and self-correction.
"""

from typing import Dict, Any, Optional, List
import structlog
import datetime
import json
from pydantic import BaseModel, Field

from app.agents.base import get_llm, get_agent_config, BaseAgent, safe_parse_json
from app.models.conversation import AgentType
from app.core.events import publish_event
from app.services.agent_memory_service import agent_memory_service

logger = structlog.get_logger()


# ==========================================
# Pydantic Structured Outputs
# ==========================================

class CampaignTask(BaseModel):
    day: int = Field(description="Day relative to launch (negative = pre-launch)")
    title: str = Field(description="Short task title")
    description: str = Field(description="What to do")
    template: str = Field(description="Draft content template")

class CampaignPlan(BaseModel):
    name: str = Field(description="Campaign name")
    strategy_summary: str = Field(description="2-sentence strategy")
    tasks: List[CampaignTask] = Field(description="Day-by-day task list")

class LookalikeProfile(BaseModel):
    name: str = Field(description="Person's name")
    title: str = Field(description="Their title/role")
    company: str = Field(description="Company or channel name")
    reason: str = Field(description="Why they are similar to the seed")

class LeadMagnet(BaseModel):
    title: str = Field(description="Catchy lead magnet title")
    subtitle: str = Field(description="Hook/subtitle")
    content: List[str] = Field(description="Content items (checklist items or section headings)")
    cta: str = Field(description="Call-to-action text")
    email_sequence: List[str] = Field(description="Follow-up email sequence outlines")

class LandingPageSection(BaseModel):
    hero_headline: str = Field(description="Main headline")
    hero_subheadline: str = Field(description="Supporting subheadline")
    hero_cta: str = Field(description="CTA button text")
    pain_points: List[str] = Field(description="3 pain points")
    benefits: List[str] = Field(description="3 solution benefits")
    features: List[str] = Field(description="5 feature descriptions")
    faq: List[str] = Field(description="5 FAQ questions and answers")
    final_cta: str = Field(description="Final call-to-action")

class ViralHook(BaseModel):
    hook: str = Field(description="The scroll-stopping hook text")
    type: str = Field(description="Hook type: contrarian, story, data, question, how-to")

class MarketingOpportunity(BaseModel):
    platform: str = Field(description="Platform where found")
    type: str = Field(description="Type: comment, reply, or trend_jack")
    title: str = Field(description="Post title or context")
    url: Optional[str] = Field(default=None, description="URL if available")
    insight: str = Field(description="Why this is an opportunity")
    draft: str = Field(description="Draft response promoting our solution")

class OpportunityList(BaseModel):
    opportunities: List[MarketingOpportunity]


# ==========================================
# Agent Class
# ==========================================

class MarketingAgent(BaseAgent):
    """
    Marketing Agent - Handles social media distribution & growth hacking.
    Upgraded to BaseAgent with cognitive depth, memory recall, and structured outputs.
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.MARKETING)
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = get_llm("gemini-2.0-flash", temperature=0.7)
        return self._llm

    async def create_social_post(self, context: str, platform: str) -> str:
        """Generate high-engagement social post"""
        await publish_event("agent_activity", {
            "agent": "MarketingAgent",
            "action": "processing_request",
            "status": "thinking",
            "timestamp": str(datetime.datetime.utcnow())
        })
        if not self.llm:
            return "Marketing Agent not initialized (LLM missing)."
        return "Draft post..."

    async def cross_post_to_socials(self, content: str, platforms: List[str], startup_id: Optional[str] = None) -> Dict[str, Any]:
        """Post content to multiple platforms via Internal Social Engine."""
        from app.integrations.typefully import TypefullyIntegration
        
        social_engine = TypefullyIntegration()
        results = []
        
        for platform in platforms:
            try:
                action_result = await social_engine.execute_action("schedule_thread", {
                    "content": content,
                    "date": datetime.datetime.utcnow().isoformat(),
                    "startup_id": startup_id,
                    "platform": platform
                })
                results.append({
                    "platform": platform,
                    "success": action_result.get("success"),
                    "id": action_result.get("thread_id"),
                    "status": action_result.get("status")
                })
            except Exception as e:
                logger.error(f"MarketingAgent: Post to {platform} failed", error=str(e))
                results.append({"platform": platform, "success": False, "error": str(e)})

        return {
            "success": any(r["success"] for r in results),
            "provider": "Internal Social Engine",
            "results": results
        }

    async def generate_viral_thread(self, topic: str) -> List[str]:
        """Generate a high-engagement X/LinkedIn thread about a topic"""
        if not self.llm:
            return ["Topic: " + topic]
        prompt = f"Create a 5-tweet viral thread about: {topic}. Start with a massive hook."
        response = await self.llm.ainvoke(prompt)
        return response.content.split("\n\n")

    async def optimize_post_loop(self, topic: str, goal: str, target_audience: str) -> Dict[str, Any]:
        """Self-optimizing loop using BaseAgent's self_correcting_call."""
        if not self.llm:
            return {"error": "Marketing Agent LLM not initialized"}
        
        try:
            prompt = f"""Draft 2 distinct viral social media posts about: {topic}
Goal: {goal}
Audience: {target_audience}

Return the BEST single post that would score above 85/100 for virality."""
            
            result = await self.self_correcting_call(
                prompt=prompt,
                goal=goal,
                target_audience=target_audience,
                model_name="gemini-2.0-flash",
                max_iterations=3,
                threshold=85
            )
            
            return {
                "status": "optimized",
                "winner": str(result),
                "agent": "MarketingAgent"
            }
        except Exception as e:
            logger.error("Post optimization failed", error=str(e))
            return {"error": str(e)}

    async def generate_campaign_plan(self, template_name: str, startup_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a custom campaign plan using structured output."""
        if not self.llm:
            return {"error": "LLM not initialized"}
            
        context_str = f"""Product: {startup_context.get('name', 'My Startup')}
Description: {startup_context.get('description', 'A new product')}
Audience: {startup_context.get('industry', 'General')}
Value Prop: {startup_context.get('tagline', 'Better solution')}"""

        prompt = f"""Create a detailed, day-by-day launch campaign.
CONTEXT: {context_str}
CAMPAIGN TYPE: {template_name}
Generate a campaign with name, strategy summary, and day-by-day tasks (each with day number, title, description, and template content)."""

        try:
            result = await self.structured_llm_call(
                prompt=prompt,
                response_model=CampaignPlan
            )
            if isinstance(result, CampaignPlan):
                return result.model_dump()
            return result if isinstance(result, dict) else {"raw": str(result)}
        except Exception as e:
            logger.error("Campaign generation failed", error=str(e))
            return {"error": str(e)}

    async def generate_daily_ideas(self, startup_context: Dict[str, Any]) -> Dict[str, Any]:
        """Autonomous Mode: Scan for trends and propose content."""
        logger.info("MarketingAgent: Scanning daily trends")
        
        industry = startup_context.get('industry', 'Technology')
        date_str = datetime.datetime.now().strftime("%B %Y")
        
        from app.agents.base import web_search
        try:
            search_query = f"trending news items {industry} {date_str}"
            search_results = await web_search.ainvoke(search_query)
        except Exception:
            search_results = "AI Agents, Remote Work, Tech Layoffs"
             
        selector_prompt = f"""Analyze these search results and pick the ONE single most "viral" topic for a thought leadership post.
Search Results: {search_results}
Return ONLY the topic name (max 5 words)."""
        
        try:
            topic_response = await self.llm.ainvoke(selector_prompt)
            topic = topic_response.content.strip().replace('"','')
        except Exception:
            topic = "The Future of AI"
        
        draft = await self.generate_viral_thread(topic)
        
        return {
            "topic": topic,
            "draft_preview": draft[0] if draft else "Error generating draft",
            "full_draft": draft
        }

    async def scan_opportunities(self, platform: str, keywords: str) -> List[Dict[str, Any]]:
        """Scan platforms for guerrilla marketing opportunities using structured output."""
        logger.info(f"MarketingAgent: Scanning {platform} for '{keywords}'")
        from app.agents.base import web_search

        try:
            if platform == 'reddit':
                query = f"site:reddit.com {keywords} \"looking for\" OR \"recommend\" OR \"alternative to\" after:2024-01-01"
            elif platform == 'twitter':
                query = f"site:twitter.com OR site:x.com {keywords} \"hate\" OR \"broken\" OR \"wish\" -filter:replies"
            else:
                query = f"{keywords} news trends analysis"
                
            search_data = await web_search.ainvoke(query)
            
            prompt = f"""Analyze these {platform} search results and extract 3 high-intent marketing opportunities.
Search Results: {search_data}
Focus on finding people who are dissatisfied with competitors or asking for recommendations."""
            
            result = await self.structured_llm_call(
                prompt=prompt,
                response_model=OpportunityList
            )
            
            if isinstance(result, OpportunityList):
                return [op.model_dump() for op in result.opportunities]
            elif isinstance(result, dict) and "opportunities" in result:
                return result["opportunities"]
            return []

        except Exception as e:
            logger.error(f"Scan failed for {platform}", error=str(e))
            return []

    async def find_lookalikes(self, seed_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar profiles to expand the pipeline using structured output."""
        logger.info(f"HunterAgent: Finding lookalikes for {seed_profile.get('name', 'Unknown')}")
        from app.agents.base import web_search

        name = seed_profile.get('name', '')
        industry = seed_profile.get('industry', 'Tech')
        query = f"people similar to {name} {industry} influencers list"
        
        try:
            search_data = await web_search.ainvoke(query)

            prompt = f"""I have a high-value lead: {name} ({industry}).
Based on these search results, identify 3 OTHER specific people who are similar profiles.
Search Results: {search_data}
Return their name, title, company, and why they are similar."""

            result = await self.structured_llm_call(prompt=prompt)
            
            if isinstance(result, list):
                return result
            elif isinstance(result, dict):
                return result.get("profiles", [result]) if result else []
            return safe_parse_json(str(result)) or []
            
        except Exception as e:
            logger.error("Lookalike search failed", error=str(e))
            return []

    async def execute_outreach(self, lead: Dict[str, Any], campaign_subject: str, email_body: str) -> Dict[str, Any]:
        """Send campaign email via Gmail integration."""
        email_address = lead.get("email") or lead.get("contact_email")
        if not email_address:
            return {"success": False, "error": "No email address found for lead."}
             
        logger.info(f"HunterAgent: SENDING REAL EMAIL to {email_address}...")
        
        from app.integrations.gmail import gmail_integration
        
        try:
            result = await gmail_integration.execute_action("send_email", {
                "to": email_address,
                "subject": campaign_subject,
                "body": email_body,
                "sender_email": None
            })
            return result
        except Exception as e:
            logger.error("HunterAgent: Send Failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def generate_lead_magnet(
        self,
        startup_context: Dict[str, Any],
        magnet_type: str = "checklist",
        target_audience: str = "",
    ) -> Dict[str, Any]:
        """Generate a lead magnet using structured output."""
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        prompt = f"""Create a lead magnet for this startup:
STARTUP: {startup_context.get('name', '')}
INDUSTRY: {startup_context.get('industry', 'Tech')}
DESCRIPTION: {startup_context.get('description', '')}
TARGET AUDIENCE: {target_audience or 'Early-stage founders'}
MAGNET TYPE: {magnet_type}
Generate a catchy title, subtitle, content items, CTA text, and email follow-up sequence."""

        try:
            result = await self.structured_llm_call(prompt=prompt, response_model=LeadMagnet)
            if isinstance(result, LeadMagnet):
                return {"success": True, "magnet_type": magnet_type, "lead_magnet": result.model_dump(), "agent": "MarketingAgent"}
            return {"success": True, "lead_magnet": result, "agent": "MarketingAgent"}
        except Exception as e:
            logger.error("Lead magnet generation failed", error=str(e))
            return {"error": str(e)}

    async def landing_page_copy(
        self,
        startup_context: Dict[str, Any],
        page_type: str = "saas",
        tone: str = "confident",
    ) -> Dict[str, Any]:
        """Generate high-converting landing page copy using structured output."""
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        prompt = f"""Write landing page copy for:
STARTUP: {startup_context.get('name', '')}
DESCRIPTION: {startup_context.get('description', '')}
PAGE TYPE: {page_type}
TONE: {tone}
Generate hero section, pain points, benefits, features, FAQ, and final CTA."""

        try:
            result = await self.structured_llm_call(prompt=prompt, response_model=LandingPageSection)
            if isinstance(result, LandingPageSection):
                return {"success": True, "page_type": page_type, "copy": result.model_dump(), "agent": "MarketingAgent"}
            return {"success": True, "copy": result, "agent": "MarketingAgent"}
        except Exception as e:
            logger.error("Landing page copy failed", error=str(e))
            return {"error": str(e)}

    async def viral_hook_generator(
        self,
        topic: str,
        platform: str = "linkedin",
        count: int = 5,
    ) -> Dict[str, Any]:
        """Generate viral content hooks using structured output."""
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        prompt = f"""Generate {count} viral hooks for {platform} about: {topic}
Types: contrarian, personal story, data/statistic, question, "How I..."
Each hook should be under 20 words and make people STOP scrolling."""

        try:
            result = await self.structured_llm_call(prompt=prompt)
            
            if isinstance(result, list):
                hooks = result
            elif isinstance(result, dict):
                hooks = result.get("hooks", [result])
            else:
                hooks = safe_parse_json(str(result)) or []
                
            return {"success": True, "hooks": hooks, "platform": platform}
        except Exception as e:
            return {"error": str(e)}

# Legacy singleton export
marketing_agent = MarketingAgent()
