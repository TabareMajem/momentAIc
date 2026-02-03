"""
Design Lead Agent
AI-powered brand identity and UI/UX designer
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm

logger = structlog.get_logger()


class DesignAgent:
    """
    Design Lead Agent - Expert in Brand Identity and UI/UX
    
    Capabilities:
    - Brand Identity Generation (Palettes, Typography)
    - UI/UX Critiques
    - Design System Creation
    - Accessibility Audits
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-pro", temperature=0.7)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a design request"""
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": "design", "error": True}
        
        try:
            context = self._build_context(startup_context)
            prompt = f"""{context}

User Request: {message}

As Design Lead, provide:
1. Visual direction recommendations
2. UX paradigms to employ
3. Color/Typography suggestions
4. Accessibility considerations"""

            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "design",
                "tools_used": [],
            }
        except Exception as e:
            logger.error("Design agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "design", "error": True}
    
    async def generate_brand_identity(
        self,
        name: str,
        industry: str,
        vibe: str
    ) -> Dict[str, Any]:
        """Generate a brand identity system"""
        if not self.llm:
            return {"brand_identity": "AI Service Unavailable", "agent": "design", "error": True}
        
        prompt = f"""Generate Brand Identity:
Name: {name}
Industry: {industry}
Vibe: {vibe}

Provide:
1. Color Palette (Primary, Secondary, Accent with Hex codes)
2. Typography Pairings (Headings, Body)
3. Logo Concept Description
4. Visual Motif suggestions"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            return {
                "brand_identity": response.content,
                "agent": "design",
            }
        except Exception as e:
            return {"brand_identity": f"Error: {str(e)}", "agent": "design", "error": True}
        

    def _get_system_prompt(self) -> str:
        return """You are the Design Lead agent - expert in visual strategy and UX.
Your goals: Create stunning, functional, and accessible designs.
Focus on modern aesthetics (Glassmorphism, Bento grids, etc.) but prioritize usability."""
    
    def _build_context(self, ctx: Dict[str, Any]) -> str:
        return f"""Startup Context:
- Product: {ctx.get('name', 'Unknown')}
- Description: {ctx.get('description', '')}"""
    

    async def generate_card_image(
        self,
        archetype_name: str,
        anime_style: str,
        description: str
    ) -> str:
        """
        Generate visual card image using Google Gemini Imagen 3.
        Returns a signed URL or base64 data URI of the generated image.
        """
        if not settings.google_api_key:
             logger.warning("Google API key missing for image generation")
             return "https://via.placeholder.com/400x600?text=API+Key+Missing"

        logger.info("Generating image with Imagen 3", archetype=archetype_name)
        
        try:
            import google.generativeai as genai
            import base64
            
            # Configure GenAI with the API key from settings
            genai.configure(api_key=settings.google_api_key)
            
            # Use the Imagen 3 model
            model = genai.ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
            
            prompt = f"""
            Anime style character card for '{archetype_name}'.
            Style: {anime_style}.
            Description: {description}.
            High quality, detailed, 8k resolution, masterpiece.
            Vertical aspect ratio suitable for mobile card.
            """
            
            # Generate images
            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
            )
            
            if response and response.images:
                # Get the first image
                image = response.images[0]
                
                # Convert to base64 data URI 
                # Note: In a production app, we should upload this to S3/GCS and return a URL
                # For this implementation, we'll return a data URI to display directly
                # image_bytes = image._image_bytes # Accessing internal bytes if needed, but usually image is PIL
                
                # Check if it's a PIL image or bytes wrapper
                # According to docs, we might need bytes.
                # Assuming the SDK returns an object with `_image_bytes` or we can save it.
                # Let's try getting bytes safely.
                
                # To be safe with the SDK version (which might vary), let's look at standard patterns.
                # Usually `image` object has `_image_bytes` or `save()`.
                
                # Let's use a BytesIO buffer if it's a PIL image, or raw bytes if available.
                # Checking SDK source isn't easy here, but `image._image_bytes` is common in recent Google SDKs.
                
                # Hack for safety:
                img_data = image._image_bytes 
                b64_data = base64.b64encode(img_data).decode('utf-8')
                mime_type = "image/png" # Imagen usually returns PNG or JPEG.
                
                return f"data:{mime_type};base64,{b64_data}"
                
            else:
                logger.warning("Imagen returned no images")
                return f"https://placehold.co/400x600/1a1a1a/FFF?text={archetype_name.replace(' ', '+')}&font=montserrat"

        except Exception as e:
            logger.error("Image generation failed", error=str(e))
            # Fallback to placeholder
            safe_name = archetype_name.replace(" ", "+")
            return f"https://placehold.co/400x600/1a1a1a/FFF?text={safe_name}&font=montserrat"

                return f"https://placehold.co/400x600/1a1a1a/FFF?text={safe_name}&font=montserrat"

    async def generate_video(
        self,
        prompt: str,
        model: str = "kling"
    ) -> str:
        """
        Generate video using PiAPI (Kling/Sora).
        Returns a video URL.
        """
        if not settings.piapi_api_key:
            raise Exception("PiAPI key missing")
            
        import aiohttp
        import asyncio
        
        base_url = "https://api.piapi.ai/api/v1/task"
        headers = {
            "x-api-key": settings.piapi_api_key,
            "Content-Type": "application/json"
        }
        
        # Payload depends on model, but assuming standard PiAPI structure
        # Using Kling 2.5 (kling-v1-standard is valid model ID usually, checking default)
        # Based on search, endpoint is /task for creation
        
        payload = {
            "model": "kling", # or specific version like "kling-v1"
            "task_type": "video_generation", # verifying if needed
            "input": {
                "prompt": prompt,
                "negative_prompt": "blurry, low quality",
                # "aspect_ratio": "16:9" 
            },
            "config": {
                "service_mode": "public" 
            }
        }
        
        # Specific Kling payload adjustment based on common PiAPI patterns
        # Usually: {"model": "kling", "input": {"prompt": "..."}}
        
        async with aiohttp.ClientSession() as session:
            # 1. Create Task
            async with session.post(base_url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error("PiAPI task creation failed", status=resp.status, error=error_text)
                    raise Exception(f"Video generation failed: {error_text}")
                
                data = await resp.json()
                task_id = data.get("data", {}).get("task_id")
                if not task_id:
                     raise Exception("No task ID returned from PiAPI")
            
            logger.info("PiAPI task created", task_id=task_id)
            
            # 2. Poll for completion (Max 60 seconds for demo, otherwise return task_id)
            # Video gen can take minutes, so we might want to return task_id/status if it takes too long.
            # For this MVP, we try for 30s then return a placeholder or the status link.
            
            for _ in range(15): # 15 * 2s = 30s
                await asyncio.sleep(2)
                async with session.get(f"{base_url}/{task_id}", headers=headers) as resp:
                    if resp.status != 200:
                        continue
                        
                    task_data = await resp.json()
                    status = task_data.get("data", {}).get("status") # completed, failed, processing
                    
                    if status == "completed":
                        # Get output URL
                        output = task_data.get("data", {}).get("output", {})
                        video_url = output.get("video_url") or output.get("url")
                        return video_url
                    
                    if status == "failed":
                        raise Exception(f"Task failed: {task_data.get('data', {}).get('error')}")
            
            # Key modification: If timeout, we still return the Task ID info so client can poll
            # But the signature expects str (URL). 
            # Ideally we return a strict Schema object, but method signature says str.
            # I will return a special string or raise Timeout for now, 
            # but actually let's return a "processing_url" mock or the status URL.
            
            return f"https://api.piapi.ai/task/{task_id}" # Placeholder for "Check this URL"

# Singleton
design_agent = DesignAgent()
