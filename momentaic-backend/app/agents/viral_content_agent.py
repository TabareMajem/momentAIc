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

class ViralContentAgent:
    def __init__(self):
        # We can reuse an existing agent config, or just define a custom one
        self.llm = get_llm("gemini-pro", temperature=0.8)
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate_viral_campaign(self, topic: str) -> List[Dict[str, str]]:
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
                
                results.append({
                    "hook": hook,
                    "image_url": image_url,
                })
                
            return results
                
        except Exception as e:
            logger.error("Viral generation failed", error=str(e))
            raise e

# Singleton instance
viral_content_agent = ViralContentAgent()
