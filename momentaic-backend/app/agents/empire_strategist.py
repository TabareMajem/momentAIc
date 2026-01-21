"""
Empire Strategist Agent
The "Meta-Agent" that orchestrates the entire ecosystem of products for the Admin.
"""

from typing import Dict, Any, List
import structlog
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.base import get_llm

logger = structlog.get_logger()

class EmpireStrategistAgent:
    def __init__(self):
        self.products = [
            {"name": "BondQuests.com", "desc": "Gamified habit forming & quests"},
            {"name": "Otaku.Yokaizen.com", "desc": "Anime/Manga niche community & tools"},
            {"name": "Yokaizen.com", "desc": "Main App - The holistic AI ecosystem Platform"},
            {"name": "YokaizenCampus.com", "desc": "Educational hub for AI & growth"},
            {"name": "YokaizenKids.com", "desc": "AI safety & education for children"},
            {"name": "AgentForgeAI.com", "desc": "The Agent Building Foundry"},
            {"name": "MomentAIc.com", "desc": "The AI Operating System (This Platform)"}
        ]

    async def generate_nano_bananas_content(self, product_name: str) -> Dict[str, Any]:
        """
        Generates AAA 'Nano Bananas' style content.
        Style: High-Octane, Vibrant, Gamified, 'Reality Distortion'.
        """
        llm = get_llm("gemini-2.0-flash", temperature=0.9) # High creativity
        if not llm:
            return {"error": "LLM not available"}

        product = next((p for p in self.products if p["name"].lower() == product_name.lower()), None)
        if not product:
            product = {"name": product_name, "desc": "An ecosystem product"}

        prompt = f"""
        ACT AS: The 'Nano Bananas' Creative Director.
        STYLE: AAA Game Marketing meets Cyberpunk Optimism. High energy. Visual. 'Reality Distortion'. 
        
        OBJECTIVE: Create a massive content drop for: {product['name']} ({product['desc']}).

        GENERATE 3 ASSETS:
        1. **Viral Tweet**: Hook + Value + 'Reality Distortion' CTA.
        2. **LinkedIn Power Post**: Professional but electric. specific insight.
        3. **Visual Art Prompt**: A detailed prompt for an image generator (Midjourney/DALL-E 3) that captures the vibe.

        Return JSON:
        {{
            "tweet": "...",
            "linkedin": "...",
            "art_prompt": "..."
        }}
        """

        try:
            response = await llm.ainvoke([SystemMessage(content="You are the Nano Bananas Engine."), HumanMessage(content=prompt)])
            import json
            import re
            
            content = response.content
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            return json.loads(content)
        except Exception as e:
            logger.error("Nano Bananas generation failed", error=str(e))
            return {"error": str(e)}

    async def surprise_me_strategy(self) -> Dict[str, Any]:
        """
        Generates a synergistic GTM strategy connecting multiple products.
        """
        llm = get_llm("gemini-2.0-flash", temperature=0.8)
        if not llm:
            return {"error": "LLM not available"}

        products_str = "\\n".join([f"- {p['name']}: {p['desc']}" for p in self.products])

        prompt = f"""
        ACT AS: The Empire Strategist.
        CONTEXT: We own this ecosystem of products:
        {products_str}

        OBJECTIVE: Create a 'Massive' GTM Strategy that connects at least 2-3 of these products in a synergistic way.
        
        REQUIREMENTS:
        - Must be a "Campaign" idea.
        - Must be surprising and high-impact.
        - "Nano Bananas" vibe (Fun, but serious business value).

        Return JSON:
        {{
            "campaign_name": "...",
            "tagline": "...",
            "strategy_brief": "...",
            "steps": ["Step 1...", "Step 2...", "Step 3..."],
            "involved_products": ["Prod A", "Prod B"]
        }}
        """

        try:
            response = await llm.ainvoke([SystemMessage(content="You are the Empire Strategist."), HumanMessage(content=prompt)])
            import json
            import re
            
            content = response.content
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            return json.loads(content)
        except Exception as e:
            logger.error("Strategy generation failed", error=str(e))
            return {"error": str(e)}

empire_strategist = EmpireStrategistAgent()
