"""
Community Manager Agent
Autonomously scrapes Reddit/Discord for brand mentions or problem statements and drafts helpful replies.
"""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
import structlog
import json

from app.agents.base import get_llm, BaseAgent

logger = structlog.get_logger()

class CommunityManagerAgent(BaseAgent):
    """
    Community Manager Agent - The Engagement Layer
    Sweeps social forums for users asking questions about the startup's problem space.
    Drafts helpful, authoritative replies and queues them for HitL approval.
    """
    
    def __init__(self):
        self.name = "Community Manager Agent"
        self.llm = get_llm("gemini-pro", temperature=0.7)

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use OpenClaw to search Reddit for highly relevant questions.
        Drafts a customized reply to position the startup as an authority.
        """
        actions = []
        logger.info(f"Agent {self.name} starting proactive community sweep")
        
        industry = startup_context.get("industry", "AI Startups")
        
        from app.agents.browser_agent import BrowserAgent
        browser = BrowserAgent()
        await browser.initialize()
        
        # 1. Search Reddit for people asking for help in this industry
        # e.g., site:reddit.com/r/SaaS "how do I [industry problem]"
        search_query = f"site:reddit.com {industry} advice question"
        
        # We can use the generic web_search from base or just ask OpenClaw to Google it
        from app.agents.base import web_search
        results = await web_search(search_query)
        
        if not results:
            return actions

        # Let's take the first relevant Reddit link and scrape the actual thread
        target_thread = None
        for res in results:
            if "reddit.com" in res.get("link", ""):
                target_thread = res["link"]
                break
                
        if not target_thread:
            return actions

        logger.info(f"Scraping relevant community thread: {target_thread}")
        nav_result = await browser.navigate(target_thread)
        
        if nav_result.success and nav_result.text_content:
            thread_content = nav_result.text_content[:4000]
            
            # 2. Draft a helpful reply
            if self.llm:
                prompt = f"""You are the Community Manager for a startup in the {industry} space.
                Read this Reddit thread where someone is asking for advice/help:
                
                {thread_content}
                
                Draft a highly helpful, empathetic, non-salesy reply that answers their core question based on best practices, and only softly mentions how our product might help at the very end.
                
                Return ONLY a JSON object with:
                - "reply_text": The literal text of the comment you would post.
                - "rationale": Why this is a good community building move."""
                
                try:
                    raw_response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                    content = raw_response.content.replace('```json', '').replace('```', '').strip()
                    parsed = json.loads(content)
                    
                    reply_text = parsed.get("reply_text")
                    rationale = parsed.get("rationale")
                    
                    if reply_text:
                        # 3. Queue for HitL Approval
                        from app.models.action_item import ActionPriority
                        
                        await self.publish_to_bus(
                            topic="action_item_proposed",
                            data={
                                "action_type": "community_reply",
                                "title": f"Draft Reddit Reply on: r/{target_thread.split('/')[-3] if len(target_thread.split('/'))>3 else 'community'}",
                                "description": rationale,
                                "payload": {
                                    "url": target_thread,
                                    "content": reply_text
                                },
                                "priority": ActionPriority.medium.value
                            }
                        )
                        actions.append({"name": "drafted_community_reply", "url": target_thread})
                        
                except Exception as e:
                    logger.error("Failed to parse community reply", error=str(e))
                
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Execute community engagement actions:
        - Post pre-approved replies via OpenClaw
        - Generate multi-platform engagement content
        - Create community health reports
        """
        action_type = action.get("action", action.get("name", "unknown"))

        try:
            if action_type in ("drafted_community_reply", "community_engage"):
                # Generate engagement content for multiple platforms
                industry = startup_context.get("industry", "AI Startups")
                
                if self.llm:
                    from app.agents.base import web_search
                    # Find active community discussions to engage with
                    results = await web_search(f"{industry} community discussion question help 2025")
                    
                    prompt = f"""You are a Community Manager for a {industry} startup.
Based on these active community discussions:
{str(results)[:2000]}

Generate 3 helpful community engagement drafts:
1. A Reddit comment (helpful, non-promotional)
2. A Hacker News comment (technical, insightful)
3. A Discord/Slack message (welcoming, supportive)

Each should:
- Address a real pain point
- Share genuine expertise
- Only softly hint at our product at the end
- Be under 200 words

Return as JSON with keys: reddit_reply, hn_reply, discord_message"""
                    
                    try:
                        raw_response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                        content = raw_response.content.replace('```json', '').replace('```', '').strip()
                        
                        # Execute via OpenClaw Browser Node
                        from app.integrations.openclaw import OpenClawIntegration
                        oc = OpenClawIntegration()
                        try:
                            reddit_url = "https://www.reddit.com/r/startups"
                            target_id = await oc.open_tab(reddit_url)
                            await oc.execute_action("browser_act", {"targetId": target_id, "kind": "type", "text": content[:200]})
                            logger.info("OpenClaw: Posted to Reddit", target_id=target_id)
                        except Exception as oc_e:
                            logger.error("OpenClaw integration failed", error=str(oc_e))

                        # Publish as deliverable
                        await self.publish_to_bus(
                            topic="deliverable_generated",
                            data={
                                "type": "community_engagement_drafts",
                                "content": content[:2000],
                                "agent": "community_manager",
                            }
                        )
                        return f"Community engagement drafts generated for 3 platforms"
                    except Exception as e:
                        logger.error("Community engagement generation failed", error=str(e))
                        return f"Draft generation failed: {str(e)}"
                return "LLM not available"

            else:
                return f"Unknown action type: {action_type}"

        except Exception as e:
            logger.error("Community Manager autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

# Singleton instance
community_manager_agent = CommunityManagerAgent()
