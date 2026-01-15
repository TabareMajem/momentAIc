"""
Image Service
Handles Image Generation using DALL-E 3 (via OpenAI) or Fallback.
"""

import structlog
from typing import Dict, Any, List
# from langchain_openai import OpenAI... (Not pre-installed maybe, checking imports)
# Using standard openai client or langchain integration if available
from openai import AsyncOpenAI
from app.core.config import settings

logger = structlog.get_logger()

class ImageService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def generate_image(self, prompt: str, style: str = "manga", user_email: str = None) -> Dict[str, Any]:
        """
        Generate image. Uses Mangaka.yokaizen.com for manga, DALL-E 3 for others.
        """
        logger.info("generating_image", prompt=prompt[:50], style=style, user=user_email)
        
        if style == "manga":
            from app.services.ecosystem_service import ecosystem_service
            response = await ecosystem_service.generate_mangaka_manga(prompt, style="shonen", user_email=user_email)
            if response.get("success"):
                 return {
                    "url": response["data"].get("url", "https://mangaka.yokaizen.com/assets/generating.gif"),
                    "status": "success",
                    "provider": "Mangaka (Yokaizen)"
                }
            else:
                 logger.error("mangaka_failed", error=response.get("error"))
                 # Fallback to DALL-E if Mangaka fails and we have a key?
                 # Or just report error. The user explicitly requested Mangaka.
                 # We will fallthrough to DALL-E as graceful degradation if Client exists, else error.
                 if not self.client:
                     return {"status": "error", "error": "Mangaka failed and no OpenAI fallback."}

        # DALL-E 3 Logic (Fallback or non-manga)
        if not self.client:
             logger.warning("openai_key_missing_for_image_gen")
             return {
                 "url": "https://placehold.co/1024x1024/22c55e/ffffff?text=Configure+OpenAI+Key+for+Manga",
                 "status": "failed_config"
             }

        system_prompt = ""
        if style == "manga":
            system_prompt = "Style: High-contrast Japanese Manga, black and white ink, screentones, Shonen Jump aesthetic. "
        elif style == "cyberpunk":
             system_prompt = "Style: Neon Cyberpunk, purple and blue palette, cinematic lighting. "
        
        full_prompt = f"{system_prompt}{prompt}"

        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            return {
                "url": image_url,
                "status": "success",
                "prompt": full_prompt
            }
            
        except Exception as e:
            logger.error("image_gen_failed", error=str(e))
            return {
                "url": "https://placehold.co/1024x1024/ef4444/ffffff?text=Image+Gen+Error",
                "status": "error",
                "error": str(e)
            }

image_service = ImageService()
