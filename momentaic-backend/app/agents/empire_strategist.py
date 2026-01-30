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

    async def generate_nano_bananas_content(self, product_name: str, startup_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates AAA 'Nano Bananas' style content.
        Style: High-Octane, Vibrant, Gamified, 'Reality Distortion'.
        
        Args:
            product_name: Name of the product
            startup_context: Optional dictionary with 'name' and 'description' (for general users)
        """
        llm = get_llm("gemini-2.0-flash", temperature=0.9) # High creativity
        if not llm:
            return {"error": "LLM not available"}

        # 1. Try to find in Admin Ecoystem first (legacy support)
        product = next((p for p in self.products if p["name"].lower() == product_name.lower()), None)
        
        # 2. If not found, use provided context (General User)
        if not product and startup_context:
            product = {
                "name": startup_context.get("name", product_name),
                "desc": startup_context.get("description", "A revolutionary startup")
            }
            
        # 3. Fallback
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

    async def surprise_me_strategy(self, products_context: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generates a synergistic GTM strategy connecting multiple products.
        
        Args:
             products_context: Optional list of dicts [{"name": "...", "desc": "..."}] for general users.
                               If None, defaults to Admin's ecosystem.
        """
        llm = get_llm("gemini-2.0-flash", temperature=0.8)
        if not llm:
            return {"error": "LLM not available"}

        # Use provided context or default to Admin Ecosystem
        target_products = products_context if products_context else self.products
        
        if not target_products:
             return {"error": "No products available for strategy generation."}

        products_str = "\\n".join([f"- {p['name']}: {p['desc']}" for p in target_products])

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
