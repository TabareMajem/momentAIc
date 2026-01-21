"""
Nexus Service
Facilitates the "Fusion" between two autonomous product swarms.
"""

from typing import Dict, Any, List
import structlog
from app.agents.base import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.swarm_service import swarm_service

logger = structlog.get_logger()

class NexusService:
    def __init__(self):
        pass

    async def fuse_products(self, product_a_id: str, product_b_id: str) -> Dict[str, Any]:
        """
        Orchestrate a dialogue between two products.
        """
        # 1. Get Context
        prod_a = swarm_service.products.get(product_a_id)
        prod_b = swarm_service.products.get(product_b_id)
        
        if not prod_a or not prod_b:
            raise ValueError("Invalid product IDs")

        logger.info(f"Initiating Nexus Fusion: {prod_a['name']} <-> {prod_b['name']}")

        # 2. The Nexus Agent Synthesis
        llm = get_llm("gemini-2.0-flash", temperature=0.85) 
        if not llm:
            return {"error": "LLM unavailable"}

        prompt = f"""
        ACT AS: The Nexus Agent (Ecosystem Architect).
        
        ENTITY A: {prod_a['name']} ({prod_a['desc']})
        ENTITY B: {prod_b['name']} ({prod_b['desc']})
        
        MISSION:
        Facilitate a "Fusion" between these two entities.
        Find a specific, non-obvious way they can collaborate to drive growth for BOTH.
        
        OUTPUT:
        1. **The Synergy (Concept)**: A high-level description of the joint venture.
        2. **The Exchange**: What does A give? What does B give?
        3. **Tactical Orders**:
           - Order for {prod_a['name']}'s Swarm (e.g. Banshee, Director).
           - Order for {prod_b['name']}'s Swarm.
           
        Return JSON:
        {{
            "synergy_name": "...",
            "concept_pitch": "...",
            "exchange_terms": "...",
            "orders_a": {{"agent_target": "...", "instruction": "..."}},
            "orders_b": {{"agent_target": "...", "instruction": "..."}}
        }}
        """
        
        try:
            response = await llm.ainvoke([
                SystemMessage(content="You are The Nexus. You connect disparate worlds."),
                HumanMessage(content=prompt)
            ])
            import json
            import re
            content = response.content
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            
            # Clean JSON if needed
            if not content.strip().startswith("{"):
                 match = re.search(r'\{.*\}', content, re.DOTALL)
                 if match: content = match.group()

            result = json.loads(content)
            
            # 3. Simulate The Dialogue (For Effect)
            dialogue = [
                f"[{prod_a['name']} General]: Establishing secure link with {prod_b['name']}...",
                f"[{prod_b['name']} General]: Link confirmed. State your assets.",
                f"[Nexus]: I have analyzed both vectors. A fusion is possible: {result['synergy_name']}.",
                f"[{prod_a['name']} General]: Agreed. executing orders for {result['orders_a']['agent_target']}.",
                f"[{prod_b['name']} General]: Acknowledged. executing orders for {result['orders_b']['agent_target']}."
            ]
            
            result["dialogue_log"] = dialogue
            return result

        except Exception as e:
            logger.error("Nexus Fusion failed", error=str(e))
            return {"error": str(e)}

nexus_service = NexusService()
