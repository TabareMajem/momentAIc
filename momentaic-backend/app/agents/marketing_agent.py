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
        Post content to multiple platforms via CrossPost.app API
        Requires CROSSPOST_API_KEY in environment
        """
        import httpx
        from app.core.config import settings
        from app.core.database import async_session_maker
        from app.models.growth import ContentItem, ContentStatus, ContentPlatform
        from uuid import UUID
        
        crosspost_key = getattr(settings, "crosspost_api_key", None)
        
        # [REALITY UPGRADE] If no API key, save to DB as SCHEDULED/DRAFT ("Real" persistence)
        if not crosspost_key:
            logger.warning("MarketingAgent: No API Key. Persisting to Content Studio.")
            
            created_items = []
            
            if startup_id:
                try:
                    async with async_session_maker() as db:
                        for platform in platforms:
                            # Map string to enum if possible, else default
                            try:
                                platform_enum = ContentPlatform(platform.lower())
                            except ValueError:
                                platform_enum = ContentPlatform.LINKEDIN # Default/Fallback
                                
                            item = ContentItem(
                                startup_id=UUID(startup_id) if isinstance(startup_id, str) else startup_id,
                                title=f"Auto-generated Post ({platform})",
                                body=content,
                                platform=platform_enum,
                                content_type="post",
                                status=ContentStatus.DRAFTING, # Draft for review
                                scheduled_for=datetime.datetime.utcnow(),
                                ai_generated=True,
                                generation_context={"source": "MarketingAgent", "mode": "fallback_persistence"}
                            )
                            db.add(item)
                            
                            # Need to commit to generate IDs and save
                            await db.commit()
                            await db.refresh(item)
                            created_items.append(str(item.id))
                        
                    return {
                        "success": True, 
                        "mode": "persistence",
                        "message": f"API Key missing. Saved {len(created_items)} posts to Content Studio for manual review.",
                        "content_ids": created_items,
                        "provider": "Momentaic Content Studio"
                    }
                except Exception as e:
                    logger.error("MarketingAgent: DB Persistence failed", error=str(e))
                    # Fallthrough to Intent Links if DB fails
            
            # Legacy Intent Link Fallback (if no startup_id or DB error)
            import urllib.parse
            encoded_content = urllib.parse.quote(content)
            
            intent_links = {
                "twitter": f"https://twitter.com/intent/tweet?text={encoded_content}",
                "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_content}",
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
        """
        logger.info(f"MarketingAgent: Scanning {platform} for '{keywords}'")
        from app.agents.base import web_search
        
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
            
            # Use LLM to parse raw text into structured opportunities
            # This turns the "search blob" into the nice cards we see in the UI
            prompt = f"""
            Analyze these {platform} search results and extract 3 high-intent marketing opportunities.
            
            Search Results:
            {search_data}
            
            Return a JSON array of objects with this EXACT schema:
            [
              {{
                "platform": "{platform}",
                "type": "comment" (for reddit) or "reply" (for twitter) or "trend_jack",
                "title": "Post title or Tweet context",
                "url": "URL if available, else null",
                "insight": "Why is this an opportunity? (e.g. 'User hates Competitor X')",
                "draft": "A witty, helpful response promoting our solution (don't sound like a bot)",
                "timestamp": "ISO timestamp (approximate)"
              }}
            ]
            """
            
            from langchain_core.messages import HumanMessage, SystemMessage
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a guerrilla marketing expert. You find leads and draft killer replies."),
                HumanMessage(content=prompt)
            ])
            
            import json
            import re
            
            content = response.content
            match = re.search(r'\[.*\]', content, re.DOTALL)
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

marketing_agent = MarketingAgent()
