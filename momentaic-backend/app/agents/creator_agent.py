import asyncio
import structlog
from typing import Dict, Any
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

creator_agent = CreatorAgent()
