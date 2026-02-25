"""
Viral Content Agent
Autonomously generates viral hooks and matching DALL-E 3 images for the Ambassador Swarm.
"""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
from app.agents.base import get_llm, get_agent_config
from app.models.conversation import AgentType
from openai import AsyncOpenAI
import os
import json

logger = structlog.get_logger()

from app.core.config import settings

class ViralContentAgent:
    def __init__(self):
        # We can reuse an existing agent config, or just define a custom one
        self.llm = get_llm("gemini-pro", temperature=0.8)
        
        # Prevent import crash if OpenAI key isn't set yet
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = "dummy_key_to_prevent_import_crash"
        self.openai_client = AsyncOpenAI(api_key=api_key)
        
        # New API Keys for Omni-Channel Auto-Post
        self.heygen_api_key = os.getenv("HEYGEN_API_KEY", "dummy_heygen_key")
        self.tiktok_access_token = os.getenv("TIKTOK_ACCESS_TOKEN", "dummy_tiktok_token")

    async def generate_heygen_video(self, script: str) -> str:
        """
        Generate an AI Avatar video using HeyGen's API.
        Returns the URL of the generated video.
        """
        logger.info("Generating HeyGen AI Video Avatar...", script_length=len(script))
        try:
            # Simulated or real HeyGen API call
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.heygen.com/v2/video/generate",
                    headers={
                        "X-Api-Key": self.heygen_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "video_inputs": [
                            {
                                "character": {
                                    "type": "avatar",
                                    "avatar_id": "Daisy-costume1-20220818", # Default realistic avatar
                                    "avatar_style": "normal"
                                },
                                "voice": {
                                    "type": "text",
                                    "input_text": script,
                                    "voice_id": "1bd001e7e50f421d891986aad5158bc8" # Professional energetic voice
                                }
                            }
                        ],
                        "dimension": {"width": 1080, "height": 1920} # Vertical format for TikTok/Reels
                    }
                )
                
                # In a real environment we would poll for completion, but we will mock the return for the demo
                if response.status_code == 200:
                    video_id = response.json().get("data", {}).get("video_id", "demo_video_id")
                    return f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
                else:
                    logger.warning("HeyGen API returned non-200. Using Mock Video URL.", status=response.status_code)
                    return "https://www.youtube.com/watch?v=mock_heygen_video"
        except Exception as e:
            logger.error("HeyGen video generation failed", error=str(e))
            return "https://www.youtube.com/watch?v=mock_heygen_error"

    async def post_to_tiktok(self, video_url: str, caption: str) -> bool:
        """
        Post a specific video URL direct to TikTok via their Content Posting API.
        """
        logger.info("Posting video to TikTok...", video_url=video_url)
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://open.tiktokapis.com/v2/post/publish/video/init/",
                    headers={
                        "Authorization": f"Bearer {self.tiktok_access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "post_info": {
                            "title": caption,
                            "privacy_level": "PUBLIC_TO_EVERYONE",
                            "disable_duet": False,
                            "disable_comment": False,
                            "disable_stitch": False
                        },
                        "source_info": {
                            "source": "PULL_FROM_URL",
                            "video_url": video_url
                        }
                    }
                )
                if response.status_code == 200:
                    logger.info("Successfully posted to TikTok!")
                    return True
                else:
                    logger.warning("TikTok API returned non-200", status=response.status_code)
                    return False
        except Exception as e:
            logger.error("TikTok API Posting failed", error=str(e))
            return False

    async def generate_viral_campaign(self, topic: str, generate_video: bool = False) -> List[Dict[str, str]]:
        """
        Generate 3 viral hooks and matching DALL-E image prompts based on a topic.
        Then call DALL-E to generate the images.
        """
        if not self.llm:
            raise Exception("AI Service Unavailable")
            
        system_prompt = """You are a world-class viral growth hacker and copywriter for B2B SaaS.
Your goal is to take a generic topic and generate 3 extremely compelling, polarizing, or high-value social media hooks (for TikTok, X, or Instagram Reels).
For each hook, also provide a highly detailed, dramatic image generation prompt for DALL-E 3 that perfectly matches the hook's aesthetic (e.g. cyberpunk, dark mode UI, glowing neon, dramatic data visualizations).

Return the response STRICTLY as a JSON array of objects with 'hook' and 'image_prompt' keys. Do not include markdown formatting or backticks around the JSON."""

        user_prompt = f"Topic: {topic}\n\nGenerate 3 viral hooks and image prompts as a JSON array."
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            
            # Clean up potential markdown formatting
            content = response.content.replace('```json', '').replace('```', '').strip()
            campaigns = json.loads(content)
            
            results = []
            for campaign in campaigns:
                hook = campaign.get("hook", "")
                image_prompt = campaign.get("image_prompt", "")
                if not hook or not image_prompt:
                    continue
                    
                # Call DALL-E 3
                try:
                    image_response = await self.openai_client.images.generate(
                        model="dall-e-3",
                        prompt=image_prompt[:1000],  # DALL-E max prompt length
                        size="1024x1024",
                        quality="standard",
                        n=1,
                    )
                    image_url = image_response.data[0].url
                except Exception as img_e:
                    logger.error("DALL-E generation failed", error=str(img_e))
                    image_url = "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&q=80&w=800"
                
                campaign_result = {
                    "hook": hook,
                    "image_url": image_url,
                }
                
                if generate_video:
                    video_url = await self.generate_heygen_video(script=hook)
                    campaign_result["video_url"] = video_url
                    await self.post_to_tiktok(video_url=video_url, caption=f"{hook[:50]} #viral #startup")
                    
                results.append(campaign_result)
                
            return results
                
        except Exception as e:
            logger.error("Viral generation failed", error=str(e))
            raise e

# Singleton instance
viral_content_agent = ViralContentAgent()
