"""
Swarm Service
Orchestrates the massive 10-agent swarms for each product.
"""

from typing import Dict, Any, List, Optional
import asyncio
import structlog
from datetime import datetime
from app.agents.swarm_agents import SWARM_AGENTS

logger = structlog.get_logger()

class ProductSwarm:
    def __init__(self, product_name: str, product_desc: str, dry_run: bool = True, social_creds: Optional[Dict] = None):
        self.product_name = product_name
        self.product_desc = product_desc
        self.dry_run = dry_run
        self.social_creds = social_creds
        self.results = {}

    async def deploy_agent(self, agent_key: str, context: Dict[str, Any]):
        """Run a single agent and store result"""
        agent = SWARM_AGENTS.get(agent_key)
        if not agent:
            return
        
        logger.info(f"Deploying {agent.name} for {self.product_name}...")
        try:
            result = await agent.execute(self.product_name, self.product_desc, context)
            self.results[agent_key] = {
                "agent": agent.name,
                "timestamp": datetime.utcnow().isoformat(),
                "output": result
            }
            
            # ========== THE REALITY BRIDGE ==========
            from app.services.reality_bridge import reality_bridge
            
            if agent_key == "banshee":
                bridge_result = await reality_bridge.execute_banshee(
                    result, 
                    social_creds=self.social_creds, 
                    dry_run=self.dry_run
                )
                self.results[agent_key]["bridge"] = bridge_result
                
            elif agent_key == "sniper":
                bridge_result = await reality_bridge.execute_sniper(
                    result, 
                    target_email=None,  # Admin would provide this
                    dry_run=self.dry_run
                )
                self.results[agent_key]["bridge"] = bridge_result
            # =========================================
            
        except Exception as e:
            logger.error(f"{agent.name} failed", error=str(e))
            self.results[agent_key] = {"error": str(e)}

    async def unleash_swarm(self):
        """Run all 10 agents in parallel"""
        tasks = []
        context = {"extra_context": "Brutal GTM Phase 17 Launch"}
        
        for key in SWARM_AGENTS.keys():
            tasks.append(self.deploy_agent(key, context))
            
        await asyncio.gather(*tasks)
        return self.results

class SwarmService:
    def __init__(self):
        # The 7 Pillars
        self.products = {
            "bondquests": {"name": "BondQuests.com", "desc": "Gamified habit forming & quests"},
            "otaku": {"name": "Otaku.Yokaizen.com", "desc": "Anime/Manga niche community"},
            "yokaizen": {"name": "Yokaizen.com", "desc": "Holistic AI ecosystem platform"},
            "campus": {"name": "YokaizenCampus.com", "desc": "Educational hub for AI"},
            "kids": {"name": "YokaizenKids.com", "desc": "AI safety & education for kids"},
            "agentforge": {"name": "AgentForgeAI.com", "desc": "Agent building foundry"},
            "momentaic": {"name": "MomentAIc.com", "desc": "The AI Operating System"},
        }

    async def deploy_product_swarm(
        self, 
        product_id: str, 
        dry_run: bool = True,
        social_creds: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Deploy the swarm for a specific product"""
        product = self.products.get(product_id)
        if not product:
            raise ValueError("Unknown product ID")
            
        swarm = ProductSwarm(
            product["name"], 
            product["desc"], 
            dry_run=dry_run,
            social_creds=social_creds
        )
        results = await swarm.unleash_swarm()
        
        return {
            "product": product["name"],
            "swarm_size": 10,
            "mode": "DRY_RUN" if dry_run else "LIVE_FIRE",
            "status": "MISSION_COMPLETE",
            "artifacts": results
        }

swarm_service = SwarmService()
