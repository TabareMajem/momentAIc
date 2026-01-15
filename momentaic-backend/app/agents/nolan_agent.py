"""
Nolan Pro Agent
The "Trend-Jacker" Video Strategist.
"""

import structlog
from typing import List, Dict, Any
from app.services.news_service import news_service
from app.services.video_service import video_service

logger = structlog.get_logger()

class NolanAgent:
    def __init__(self):
        self.name = "Nolan Pro"
        self.role = "Video Strategist"

    async def run_daily_news_cycle(self, user_email: Any = None) -> Dict[str, Any]:
        """
        Execute the Daily News Wrap:
        1. Fetch News
        2. Write Scripts
        3. Dispatch Render Jobs
        """
        logger.info("nolan_starting_daily_cycle", user=user_email)
        
        # 1. Fetch
        news_items = await news_service.fetch_trending_topics(category="AI & Tech", count=3)
        
        generated_content = []
        
        # 2. Process
        for item in news_items:
            # Script
            script_data = await video_service.generate_script(item)
            
            # Render (Simulated/Real)
            # Pass user_email to video service to forward to ecosystem
            render_result = await video_service.render_video(script_data, user_email=user_email) # Note: Need to update video_service signature or just pass it in script_data
            
            # Correction: video_service.render_video signature needs update?
            # Or I can modify script_data to include it?
            # Let's check video_service signature. It takes script_data: Dict.
            # I'll inject it into script_data for simplicity or update method. 
            # I updated ecosystem_service to take optional user_email.
            # I updated video_service to call ecosystem_service.
            # I need to update video_service to ACCEPT user_email too.
            # Start simple: Inject into script_data? No, clean API is better.
            
            generated_content.append({
                "news_source": item,
                "script": script_data,
                "render_status": render_result
            })
            
        return {
            "agent": "Nolan Pro",
            "action": "Daily News Wrap",
            "timestamp": "now",
            "items_generated": len(generated_content),
            "details": generated_content
        }

    async def create_template_trailer(self, niche: str) -> Dict[str, Any]:
        """
        Create a template trailer for onboarding.
        """
        # Logic for "Activation" phase
        return {"status": "not_implemented_yet"}

nolan_agent = NolanAgent()
