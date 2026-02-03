from typing import Dict, Any, Optional, List
import structlog
from app.agents.base import get_llm, get_agent_config
from app.models.conversation import AgentType
from app.core.events import publish_event
import datetime

logger = structlog.get_logger()

class MarketingAgent:
    """
    Marketing Agent - Handles social media distribution & growth hacking
    Integration target: CrossPost.app, LinkedIn, X
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.MARKETING)
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            # Use gemini-flash for speed and reliability
            self._llm = get_llm("gemini-flash", temperature=0.7)
        return self._llm

    async def create_social_post(self, context: str, platform: str) -> str:
        """Generate high-engagement social post"""
        # Publish "Thinking" event
        await publish_event("agent_activity", {
            "agent": "MarketingAgent",
            "action": "processing_request",
            "status": "thinking",
            "timestamp": str(datetime.datetime.utcnow())
        })

        if not self.llm:
            return "Marketing Agent not initialized (LLM missing)."
        
        # ... logic ...
        return "Draft post..."

    async def cross_post_to_socials(self, content: str, platforms: List[str], startup_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Post content to multiple platforms via Internal Social Engine.
        """
        from app.integrations.typefully import TypefullyIntegration
        from app.models.social import SocialPlatform
        
        social_engine = TypefullyIntegration()
        results = []
        
        # [REALITY UPGRADE] Use Internal Engine (SocialPost) for all
        for platform in platforms:
            try:
                # Map platform string to SocialPlatform enum logic if needed, 
                # but TypefullyIntegration handles logic. 
                # We'll use schedule_thread which saves to DB.
                
                # Determine action based on platform. 
                # For now, treat all as threads/posts.
                
                action_result = await social_engine.execute_action("schedule_thread", {
                    "content": content,
                    "date": datetime.datetime.utcnow().isoformat(), # Schedule immediately/now
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
        """
        Self-optimizing loop: Draft -> Critique -> Rewrite
        """
        if not self.llm:
            return {"error": "Marketing Agent LLM not initialized"}
            
        from app.agents import judgement_agent
        from langchain.schema import HumanMessage, SystemMessage

        # 1. Initial Drafts (Generate 2 variations)
        draft_prompt = f"""
        Draft 2 distinct viral social media posts about: {topic}
        Goal: {goal}
        Audience: {target_audience}
        
        Format as:
        ---
        <Post 1 Text>
        ---
        <Post 2 Text>
        ---
        """
        
        draft_response = await self.llm.ainvoke(draft_prompt)
        original_drafts = [d.strip() for d in draft_response.content.split("---") if len(d.strip()) > 10]
        
        if len(original_drafts) < 2:
            return {"error": "Failed to generate variations"}
            
        current_variations = original_drafts[:2]
        history = []
        winner = None
        
        # 2. Optimization Loop (Max 3 iterations)
        for iteration in range(3):
            # Evaluate
            evaluation = await judgement_agent.evaluate_content(
                goal=goal, 
                target_audience=target_audience, 
                variations=current_variations
            )
            
            if "error" in evaluation:
                return evaluation
                
            history.append({
                "iteration": iteration + 1,
                "variations": current_variations,
                "scores": evaluation.get("scores", []),
                "winner_idx": evaluation.get("winner_index", 1),
                "critique": evaluation.get("critique", [])
            })
            
            # Check threshold (e.g., Score > 85)
            scores = evaluation.get("scores", [0])
            best_score = max(scores) if scores else 0
            
            if best_score >= 85:
                # We have a winner!
                winner_idx = evaluation.get("winner_index", 1) - 1
                winner = current_variations[winner_idx]
                break
                
            # If not good enough, REWRITE based on critique
            critiques = evaluation.get("critique", [])
            critique_text = "\n".join(critiques)
            
            rewrite_prompt = f"""
            Your previous drafts were good, but we need VIRAL status (Score > 85).
            
            Critique from Judgement Agent:
            {critique_text}
            
            REWRITE the posts to address this critique. Make them punchier, stronger hooks.
            Return 2 new variations in the same format.
            """
            
            rewrite_response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert copywriter who takes feedback seriously."),
                HumanMessage(content=draft_prompt),  # Context
                HumanMessage(content=rewrite_response.content if 'rewrite_response' in locals() else draft_response.content), # Previous
                HumanMessage(content=rewrite_prompt)
            ])
            
            new_drafts = [d.strip() for d in rewrite_response.content.split("---") if len(d.strip()) > 10]
            if len(new_drafts) >= 2:
                current_variations = new_drafts[:2]
            else:
                # Failed to generate valid rewrites, break to avoid loop
                break
                
        # If loop finishes without > 85, take the last best
        if not winner and current_variations:
            winner = current_variations[0] 

        return {
            "status": "optimized",
            "final_score": best_score,
            "iterations": len(history),
            "winner": winner,
            "history": history
        }

    async def generate_campaign_plan(self, template_name: str, startup_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a custom campaign plan based on a template and startup context"""
        if not self.llm:
            return {"error": "LLM not initialized"}
            
        context_str = f"""
        Product: {startup_context.get('name', 'My Startup')}
        Description: {startup_context.get('description', 'A new product')}
        Audience: {startup_context.get('industry', 'General')}
        Value Prop: {startup_context.get('tagline', 'Better solution')}
        """
        
        prompt = f"""
        You are a Growth Marketing Expert. Create a detailed, day-by-day launch campaign for this product.
        
        CONTEXT:
        {context_str}
        
        CAMPAIGN TYPE: {template_name}
        
        Output valid JSON with this structure:
        {{
            "name": "Customized {template_name}",
            "strategy_summary": "2-sentence strategy",
            "tasks": [
                {{ "day": -5, "title": "...", "description": "...", "template": "Draft social post..." }},
                {{ "day": 0, "title": "Launch Day", "description": "...", "template": "It's live!..." }}
            ]
        }}
        
        Make the tasks specific to the product description provided. Do not use markdown backticks.
        """
        
        try:
            # Uses module-level imports or ensured imports
            from langchain.schema import HumanMessage, SystemMessage 
            
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a growth hacker agent. Output only valid JSON."),
                HumanMessage(content=prompt)
            ])
            
            # Simple JSON parsing (in production would use output parsers)
            import json
            import re
            
            content = response.content
            # Try to find JSON block if wrapped in markdown
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                content = match.group(0)
                
            return json.loads(content)
        except Exception as e:
            logger.error("Campaign generation failed", error=str(e))
            return {"error": str(e)}

    async def generate_daily_ideas(self, startup_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Autonomous Mode: Scan for trends and propose content.
        """
        logger.info("MarketingAgent: Scaning daily trends")
        
        # 1. "Scan" Trends (Real Web Search)
        industry = startup_context.get('industry', 'Technology')
        date_str = datetime.datetime.now().strftime("%B %Y")
        
        # Search for trends
        from app.agents.base import web_search # Ensure import
        try:
            search_query = f"trending news items {industry} {date_str}"
            search_results = await web_search.ainvoke(search_query)
        except:
             search_results = "AI Agents, Remote Work, Tech Layoffs" # Fallback if search fails completely
             
        # Pick best topic via LLM
        selector_prompt = f"""
        Analyze these search results and pick the ONE single most "viral" topic for a thought leadership post.
        
        Search Results:
        {search_results}
        
        Return ONLY the topic name (max 5 words).
        """
        
        try:
             topic_response = await self.llm.ainvoke(selector_prompt)
             topic = topic_response.content.strip().replace('"','')
        except:
             topic = "The Future of AI"
        
        # 2. Draft Content
        draft = await self.generate_viral_thread(topic)
        
        return {
            "topic": topic,
            "draft_preview": draft[0] if draft else "Error generating draft",
            "full_draft": draft
        }
    
    async def scan_opportunities(self, platform: str, keywords: str) -> List[Dict[str, Any]]:
        """
        Scan specific platforms for guerrilla marketing opportunities.
        Uses sophisticated search operators to find high-intent discussions.
        Refactored to use Pydantic Output Parsing for reliability.
        """
        logger.info(f"MarketingAgent: Scanning {platform} for '{keywords}'")
        from app.agents.base import web_search
        from langchain.output_parsers import PydanticOutputParser
        from pydantic import BaseModel, Field
        from langchain.schema import HumanMessage, SystemMessage

        # Define Pydantic Model for structured output
        class MarketingOpportunity(BaseModel):
            platform: str = Field(description="The platform where the opportunity was found")
            type: str = Field(description="Type of opportunity: comment, reply, or trend_jack")
            title: str = Field(description="Post title or Tweet context")
            url: Optional[str] = Field(description="URL if available, else null")
            insight: str = Field(description="Why is this an opportunity? (e.g. 'User hates Competitor X')")
            draft: str = Field(description="A witty, helpful response promoting our solution")
            timestamp: str = Field(description="ISO timestamp or approximate time")

        class OpportunityList(BaseModel):
            opportunities: List[MarketingOpportunity]

        results = []
        
        try:
            # tailored queries
            if platform == 'reddit':
                query = f"site:reddit.com {keywords} \"looking for\" OR \"recommend\" OR \"alternative to\" after:2024-01-01"
            elif platform == 'twitter':
                query = f"site:twitter.com OR site:x.com {keywords} \"hate\" OR \"broken\" OR \"wish\" -filter:replies"
            else:
                query = f"{keywords} news trends analysis"
                
            search_data = await web_search.ainvoke(query)
            
            # Setup Parser
            parser = PydanticOutputParser(pydantic_object=OpportunityList)
            
            prompt = f"""
            Analyze these {platform} search results and extract 3 high-intent marketing opportunities.
            
            Search Results:
            {search_data}
            
            {parser.get_format_instructions()}
            
            Focus on finding people who are dissatisfied with competitors or asking for recommendations.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a guerrilla marketing expert. You find leads and draft killer replies."),
                HumanMessage(content=prompt)
            ])
            
            # Parse output
            try:
                parsed_result = parser.parse(response.content)
                results = [op.dict() for op in parsed_result.opportunities]
            except Exception as parse_error:
                logger.warning("MarketingAgent: Pydantic parse failed", error=str(parse_error))
                # Fallback to simple regex if Pydantic fails (though unlikely with format instructions)
                import json
                import re
                match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if match:
                     results = json.loads(match.group(0))

        except Exception as e:
            logger.error(f"Scan failed for {platform}", error=str(e))
            
        return results

    async def find_lookalikes(self, seed_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        [Hunter 2.0] Infinite Expansion Loop
        Given a seed profile (e.g. 'Bilawal Sidhu'), finds 5 similar profiles
        to auto-expand the pipeline without user input.
        """
        logger.info(f"HunterAgent: Finding lookalikes for {seed_profile.get('name', 'Unknown')}")
        from app.agents.base import web_search

        # 1. Construct Search Query
        name = seed_profile.get('name', '')
        industry = seed_profile.get('industry', 'Tech')
        query = f"people similar to {name} {industry} influencers list"
        
        try:
            search_data = await web_search.ainvoke(query)

            # 2. Extract New Targets via LLM
            prompt = f"""
            I have a high-value lead: {name} ({industry}).
            Based on these search results, identify 3 OTHER specific people who are similar profiles (influencers/creators in the same niche).
            
            Search Results:
            {search_data}

            Return valid JSON array:
            [
                {{
                    "name": "Name",
                    "title": "Title",
                    "company": "Company/Channel Name",
                    "reason": "Why they are similar"
                }}
            ]
            """
            
            from langchain.schema import HumanMessage, SystemMessage
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a Talent Scout. Find specific people."),
                HumanMessage(content=prompt)
            ])
            
            import json
            import re
            content = response.content
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return []

        except Exception as e:
            logger.error("Lookalike search failed", error=str(e))
            return []

    async def execute_outreach(self, lead: Dict[str, Any], campaign_subject: str, email_body: str) -> Dict[str, Any]:
        """
        [REAL ACTION] Sends the drafted campaign email via Gmail integration.
        """
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
                "sender_email": None # Uses env default
            })
            return result
        except Exception as e:
            logger.error("HunterAgent: Send Failed", error=str(e))
            return {"success": False, "error": str(e)}

    # ==== TWIN.SO KILLER: LEAD GENERATION TOOLS ====
    
    async def generate_lead_magnet(
        self,
        startup_context: Dict[str, Any],
        magnet_type: str = "checklist",  # checklist, pdf_guide, template, cheat_sheet
        target_audience: str = "",
    ) -> Dict[str, Any]:
        """
        Generate a lead magnet (PDF outline, checklist, etc).
        Superior to twin.so: full content generation, not just ideas.
        """
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        prompt = f"""Create a lead magnet for this startup:

STARTUP: {startup_context.get('name', '')}
INDUSTRY: {startup_context.get('industry', 'Tech')}
DESCRIPTION: {startup_context.get('description', '')}
TARGET AUDIENCE: {target_audience or 'Early-stage founders'}

MAGNET TYPE: {magnet_type}

Generate:
1. Catchy Title (with number if checklist)
2. Subtitle/Hook
3. Full Content (10-15 items for checklist, 5 sections for guide)
4. Lead capture CTA text
5. Email follow-up sequence outline (3 emails)

Format as JSON:
{{
    "title": "...",
    "subtitle": "...",
    "content": [...],
    "cta": "...",
    "email_sequence": [...]
}}"""

        try:
            from langchain.schema import HumanMessage
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            import json, re
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                magnet = json.loads(json_match.group())
                return {
                    "success": True,
                    "magnet_type": magnet_type,
                    "lead_magnet": magnet,
                    "agent": "MarketingAgent"
                }
            return {"raw": response.content}
        except Exception as e:
            logger.error("Lead magnet generation failed", error=str(e))
            return {"error": str(e)}

    async def landing_page_copy(
        self,
        startup_context: Dict[str, Any],
        page_type: str = "saas",  # saas, agency, ecommerce, waitlist
        tone: str = "confident",
    ) -> Dict[str, Any]:
        """
        Generate high-converting landing page copy.
        Returns structured sections ready for implementation.
        """
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        prompt = f"""Write landing page copy for:

STARTUP: {startup_context.get('name', '')}
DESCRIPTION: {startup_context.get('description', '')}
PAGE TYPE: {page_type}
TONE: {tone}

Generate:
1. Hero Section (headline, subheadline, CTA button text)
2. Problem Section (3 pain points)
3. Solution Section (3 benefits)
4. Social Proof Placeholder (what to include)
5. Features Section (5 features with icons)
6. Pricing Teaser
7. FAQ (5 questions)
8. Final CTA

Format as JSON with all sections."""

        try:
            from langchain.schema import HumanMessage
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            import json, re
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                return {
                    "success": True,
                    "page_type": page_type,
                    "copy": json.loads(json_match.group()),
                    "agent": "MarketingAgent"
                }
            return {"raw": response.content}
        except Exception as e:
            logger.error("Landing page copy failed", error=str(e))
            return {"error": str(e)}

    async def viral_hook_generator(
        self,
        topic: str,
        platform: str = "linkedin",
        count: int = 5,
    ) -> Dict[str, Any]:
        """
        Generate viral content hooks that stop the scroll.
        """
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        prompt = f"""Generate {count} viral hooks for {platform} about: {topic}

Types to include:
- Contrarian take
- Personal story starter
- Data/statistic lead
- Question hook
- "How I..." hook

Each hook should be under 20 words and make people STOP scrolling.

Format as JSON array: [{{\"hook\": \"...\", \"type\": \"...\"}}]"""

        try:
            from langchain.schema import HumanMessage
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            import json, re
            match = re.search(r'\[[\s\S]*\]', response.content)
            if match:
                return {
                    "success": True,
                    "hooks": json.loads(match.group()),
                    "platform": platform
                }
            return {"raw": response.content}
        except Exception as e:
            return {"error": str(e)}

marketing_agent = MarketingAgent()
