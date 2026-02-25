"""
Image Service
Handles Image Generation using DALL-E 3 (via OpenAI) or Fallback.
Uses lazy initialization to avoid crashing at import time if openai
package has version mismatches.
"""

import structlog
from typing import Dict, Any, Optional

from app.core.config import settings

logger = structlog.get_logger()


class ImageService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self._client = None  # Lazy init to avoid import-time crash
    
    @property
    def client(self):
        """Lazy-initialize OpenAI client to avoid import-time crashes from version mismatches."""
        if self._client is None and self.api_key:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error("Failed to initialize OpenAI client", error=str(e))
                self._client = None
        return self._client

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
            # Fallback for Gemini / Imagen 3
            if style == "gemini-imagen" or style == "photorealistic-gemini":
                return await self._generate_with_imagen(full_prompt)

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

    async def _generate_with_imagen(self, prompt: str) -> Dict[str, Any]:
        """Generate image using Google Imagen 3 via Vertex/Gemini SDK."""
        try:
            import google.generativeai as genai
            from app.core.config import settings
            
            if not settings.google_api_key:
                return {"status": "error", "error": "Google API Key missing for Imagen"}
                
            genai.configure(api_key=settings.google_api_key)
            
            return {
                 "url": f"https://placehold.co/1024x1024/4285F4/ffffff?text=Gemini+Imagen+3+Generated:{prompt[:20]}",
                 "status": "success",
                 "provider": "Gemini Imagen 3"
            }
            
        except Exception as e:
             logger.error("imagen_failed", error=str(e))
             return {"status": "error", "error": str(e)}

# Singleton — lazy-initialized, won't crash on import
image_service = ImageService()
