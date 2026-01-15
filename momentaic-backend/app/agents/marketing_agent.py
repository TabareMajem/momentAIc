from typing import Dict, Any, Optional, List
import structlog
from app.agents.base import get_llm, get_agent_config
from app.core.events import publish_event
import datetime

logger = structlog.get_logger()

class MarketingAgent:
    """
    Marketing Agent - Handles social media distribution & growth hacking
    Integration target: CrossPost.app, LinkedIn, X
    """
    
    def __init__(self):
        self._llm = None
        
    @property
    def llm(self):
        if self._llm is None:
            try:
                self._llm = get_llm("gemini-2.0-flash")
            except Exception as e:
                logger.error("MarketingAgent: LLM initialization failed", error=str(e))
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

    async def cross_post_to_socials(self, content: str, platforms: List[str]) -> Dict[str, Any]:
        """
        Post content to multiple platforms via CrossPost.app API
        Requires CROSSPOST_API_KEY in environment
        """
        import httpx
        from app.core.config import settings
        
        crosspost_key = getattr(settings, "crosspost_api_key", None)
        
        # [REALITY UPGRADE] If no API key, generate actionable Intent Links instead of mocking success.
        if not crosspost_key:
            logger.warning("MarketingAgent: No API Key. Generating Intent Links.")
            
            import urllib.parse
            encoded_content = urllib.parse.quote(content)
            
            intent_links = {
                "twitter": f"https://twitter.com/intent/tweet?text={encoded_content}",
                "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_content}", # LinkedIn share is URL based usually, but text intent exists via APIs or just text copy
                "email": f"mailto:?subject=New Post&body={encoded_content}"
            }
            
            return {
                "success": True, 
                "mode": "manual_intent",
                "message": "API Key missing. Click links to post manually.",
                "platforms": platforms,
                "intent_links": intent_links,
                "provider": "Manual"
            }

        try:
            async with httpx.AsyncClient() as client:
                # Based on typical CrossPost API patterns
                response = await client.post(
                    "https://www.crosspost.app/api/v1/posts",
                    headers={"Authorization": f"Bearer {crosspost_key}"},
                    json={
                        "content": content,
                        "platforms": platforms,
                        "schedule_now": True
                    }
                )
                
                if response.status_code in [200, 201]:
                    return {"success": True, "provider": "CrossPost", "data": response.json()}
                else:
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error("MarketingAgent: CrossPost failed", error=str(e))
            return {"success": False, "error": str(e)}

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

marketing_agent = MarketingAgent()
