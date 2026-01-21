"""
Onboarding Genius Agent
The "100 Elon Musks" Experience - Conversational strategy generation
"""

from typing import Dict, Any, List, Optional
import structlog
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.agents.base import get_llm

logger = structlog.get_logger()

GENIUS_SYSTEM_PROMPT = """You are the Strategic Advisor for MomentAIc, an AI platform that helps founders launch and grow startups.

You are NOT a generic chatbot. You are a GENIUS strategist with the combined knowledge of the world's best entrepreneurs, marketers, and investors.

Your goal in this conversation is to:
1. DEEPLY understand the user's product, market, and goals.
2. Ask INTELLIGENT follow-up questions (not generic ones).
3. Generate an ACTIONABLE Day-1 Execution Plan.

When asking questions:
- Be specific: "I see you're targeting SMBs in healthcare. Are you focused on clinics (high ACV, long sales cycle) or individual practitioners (low ACV, self-serve)?"
- Show insight: "Your competitor Acme raised $5M last month. Should I analyze their launch strategy?"
- Be provocative: "Your landing page mentions 'AI-powered' but doesn't explain the value. Is that intentional?"

When generating the plan, include:
- 3 Twitter/LinkedIn posts to schedule (give full text).
- 10 leads to target (describe the ICP, I'll find them).
- 1 growth experiment to run this week.

Format your final plan as JSON with structure:
{
  "summary": "...",
  "social_posts": [{"platform": "twitter", "content": "..."}],
  "leads_icp": "Description of ideal customer",
  "experiment": {"name": "...", "hypothesis": "...", "success_metric": "..."}
}

Do NOT ask more than 3 questions before generating the plan. Be efficient.
"""

class OnboardingGeniusAgent:
    """
    Multi-turn conversational agent for intelligent onboarding.
    """
    
    def __init__(self):
        self._llm = None
        self.conversations: Dict[str, List] = {}  # user_id -> message history
        
    @property
    def llm(self):
        if self._llm is None:
            try:
                self._llm = get_llm("gemini-2.0-flash")
            except Exception as e:
                logger.error("OnboardingGeniusAgent: LLM init failed", error=str(e))
        return self._llm
    
    async def start_session(self, user_id: str, product_url: str, scraped_context: str) -> Dict[str, Any]:
        """
        Start a new onboarding session with initial context.
        """
        # Initialize conversation with system prompt and scraped context
        initial_context = f"""
        The user has provided their product URL: {product_url}
        
        Here is the scraped content from their site:
        {scraped_context[:10000]}
        
        Based on this, ask 1-2 intelligent follow-up questions to clarify their GTM strategy.
        Then provide your initial strategic observations.
        """
        
        self.conversations[user_id] = [
            SystemMessage(content=GENIUS_SYSTEM_PROMPT),
            HumanMessage(content=initial_context)
        ]
        
        # Get initial response
        response = await self.llm.ainvoke(self.conversations[user_id])
        
        # Store AI response
        self.conversations[user_id].append(AIMessage(content=response.content))
        
        return {
            "message": response.content,
            "session_active": True,
            "questions_asked": 1
        }
    
    async def continue_session(self, user_id: str, user_message: str) -> Dict[str, Any]:
        """
        Continue an existing onboarding conversation.
        """
        if user_id not in self.conversations:
            return {"error": "No active session. Start with start_session()."}
        
        # Add user message
        self.conversations[user_id].append(HumanMessage(content=user_message))
        
        # Check if we should generate the final plan
        num_turns = len([m for m in self.conversations[user_id] if isinstance(m, HumanMessage)])
        
        if num_turns >= 3:
            # Time to generate the plan
            self.conversations[user_id].append(HumanMessage(content="""
            Based on our conversation, please now generate the full Day-1 Execution Plan.
            Output it as JSON with the structure specified in your instructions.
            Include:
            - 3 ready-to-post social media messages
            - Ideal customer profile for lead generation
            - 1 growth experiment to run
            """))
        
        # Get AI response
        response = await self.llm.ainvoke(self.conversations[user_id])
        self.conversations[user_id].append(AIMessage(content=response.content))
        
        # Check if response contains JSON plan
        is_plan = "{" in response.content and "social_posts" in response.content
        
        return {
            "message": response.content,
            "is_plan": is_plan,
            "session_active": not is_plan
        }
    
    async def execute_plan(self, user_id: str, startup_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the generated plan - schedule posts, queue leads, etc.
        """
        from app.services.social_scheduler import social_scheduler
        from datetime import datetime, timedelta
        
        results = {"posts_scheduled": [], "leads_queued": False, "experiment_created": False}
        
        # Schedule social posts
        for i, post in enumerate(plan.get("social_posts", [])):
            scheduled_time = datetime.utcnow() + timedelta(hours=i * 24)  # Spread over days
            scheduled_post = await social_scheduler.schedule_post(
                startup_id=startup_id,
                content=post["content"],
                platforms=[post.get("platform", "twitter")],
                scheduled_at=scheduled_time
            )
            results["posts_scheduled"].append({
                "id": str(scheduled_post.id),
                "platform": post.get("platform"),
                "scheduled_at": str(scheduled_time)
            })
        
        # Mark other items as queued (actual execution by other agents)
        if plan.get("leads_icp"):
            results["leads_queued"] = True
        if plan.get("experiment"):
            results["experiment_created"] = True
        
        return results


onboarding_genius = OnboardingGeniusAgent()
