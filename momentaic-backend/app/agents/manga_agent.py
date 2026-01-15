"""
Manga Magic Agent
The "Meme Lord" and Visual Doc Generator.
"""

import structlog
from typing import Dict, Any
from app.services.image_service import image_service
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

logger = structlog.get_logger()

class MangaAgent:
    def __init__(self):
        self.name = "Manga Magic"
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_api_key,
            temperature=0.8
        ) if settings.google_api_key else None

    async def generate_reaction_panel(self, context_text: str, user_email: str = None) -> Dict[str, Any]:
        """
        Generate a visual reaction (Manga Panel) to a text.
        """
        logger.info("manga_generating_reaction", context=context_text[:20])
        
        if not self.llm:
            return {"error": "Gemini Config Missing"}

        # 1. Visual Prompt Engineering
        prompt_design = await self.llm.ainvoke(f"""
            Context: "{context_text}"
            Goal: Create a funny, viral 1-panel manga reaction image description.
            Character: "Task-kun" (A cute, determined little robot helper).
            Style: Shonen Jump Manga, Black & White.
            
            Output ONLY the visual prompt description for DALL-E.
        """)
        
        visual_prompt = prompt_design.content
        
        # 2. Generate Image
        image_result = await image_service.generate_image(visual_prompt, style="manga", user_email=user_email)
        
        return {
            "agent": "Manga Magic",
            "context": context_text,
            "visual_prompt": visual_prompt,
            "result": image_result
        }

manga_agent = MangaAgent()
