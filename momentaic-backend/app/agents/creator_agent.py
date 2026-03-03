import asyncio
import structlog
from typing import List,  Dict, Any
from app.services.kling_service import kling_service

logger = structlog.get_logger()

class CreatorAgent:
    """
    Phase 10-13: The Video Render Engine
    
    Responsible for generating the "Proof of Work" assets for the 1,000 User Swarm.
    It takes the prospect's brand assets and integrates with Kling 3.0 API
    to dynamically generate a UGC demo video of their workflow working locally.
    """
    
    async def render_demo_video(self, prospect_handle: str, blueprint_path: str, startup_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates a hyper-personalized video utilizing the JSON blueprint via Kling 3.0 PIAPI.
        """
        logger.info("creator_agent_initiating_render", target=prospect_handle, blueprint=blueprint_path)
        
        # Default fallback Avatar
        avatar_url = "https://s16-def.ap4r.com/bs2/upload-ylab-stunt-sgp/kling/digital/image/Isabella.png"
        prompt = f"She introduces herself to {prospect_handle} and shows them a custom API integration."
        
        if startup_context:
            settings = startup_context.get("settings", {})
            if settings.get("avatar_image_url"):
                avatar_url = settings.get("avatar_image_url")
                
            startup_name = startup_context.get("name", "our platform")
            product_desc = startup_context.get("description", "")
            
            prompt = (
                f"She introduces herself as a founder from {startup_name}. "
                f"She looks directly at the camera and says she built a custom API integration for {prospect_handle}. "
                f"Context: {product_desc}"
            )

        # User explicitly requested to NEVER spend credits autonomously without permission.
        # This acts as the Business Model execution lock.
        approval_granted = startup_context.get("settings", {}).get("auto_generate_ugc_videos", False) if startup_context else False
        
        video_url = await kling_service.generate_kling_avatar(image_url=avatar_url, prompt=prompt, approval_granted=approval_granted)
        
        if not video_url:
            logger.error("creator_agent_kling_blocked_or_failed", target=prospect_handle, approval=approval_granted)
            return {"success": False, "error": "Kling generation requires manual approval and was blocked."}
        
        logger.info("creator_agent_render_complete", output=video_url)
        
        return {
            "success": True,
            "video_path": video_url,
            "duration": "~5s",
            "resolution": "1080p"
        }


    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for video content trends and visual asset needs.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} video content trends and visual asset needs 2025")
        
        if results:
            from app.agents.base import get_llm
            llm = get_llm("gemini-pro", temperature=0.3)
            if llm:
                from langchain_core.messages import HumanMessage
                prompt = f"""Analyze these results for a {industry} startup:
{str(results)[:2000]}

Identify the top 3 actionable insights. Be concise."""
                try:
                    response = await llm.ainvoke([HumanMessage(content=prompt)])
                    from app.agents.base import BaseAgent
                    if hasattr(self, 'publish_to_bus'):
                        await self.publish_to_bus(
                            topic="intelligence_gathered",
                            data={
                                "source": "CreatorAgent",
                                "analysis": response.content[:1500],
                                "agent": "creator_agent",
                            }
                        )
                    actions.append({"name": "video_needed", "industry": industry})
                except Exception as e:
                    logger.error(f"CreatorAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Auto-generates video content and visual assets using AI rendering.
        """
        action_type = action.get("action", action.get("name", "unknown"))

        try:
            from app.agents.base import get_llm, web_search
            from langchain_core.messages import HumanMessage
            
            industry = startup_context.get("industry", "Technology")
            llm = get_llm("gemini-pro", temperature=0.5)
            
            if not llm:
                return "LLM not available"
            
            search_results = await web_search(f"{industry} {action_type} best practices 2025")
            
            prompt = f"""You are the Video and visual content creation via AI models agent for a {industry} startup.

Based on this context:
- Action requested: {action_type}
- Industry: {industry}
- Research: {str(search_results)[:1500]}

Generate a concrete, actionable deliverable. No fluff. Be specific and executable."""
            
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            if hasattr(self, 'publish_to_bus'):
                await self.publish_to_bus(
                    topic="deliverable_generated",
                    data={
                        "type": action_type,
                        "content": response.content[:2000],
                        "agent": "creator_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("CreatorAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

creator_agent = CreatorAgent()
