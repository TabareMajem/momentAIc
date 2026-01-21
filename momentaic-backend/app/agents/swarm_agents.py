"""
The Decemvirate: 10 Autonomous GTM Agents
Each agent has a specific "Brutal GTM" directive.
"""

from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.base import get_llm
import structlog
import asyncio

logger = structlog.get_logger()

class SwarmAgentBase:
    def __init__(self, name: str, role: str, model: str = "gemini-2.0-flash"):
        self.name = name
        self.role = role
        self.model = model

    async def execute(self, product_name: str, product_desc: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's autonomous loop"""
        llm = get_llm(self.model, temperature=0.8)
        if not llm:
            return {"error": "LLM unavailable"}

        prompt = f"""
        AGENT: {self.name} ({self.role})
        PRODUCT: {product_name}
        DESCRIPTION: {product_desc}
        
        CONTEXT: {context.get('extra_context', 'No recent context.')}
        
        YOUR MISSION:
        {self.get_mission_prompt()}
        
        OUTPUT REQUIREMENT:
        Return strict JSON with your artifacts.
        """
        
        try:
            response = await llm.ainvoke([
                SystemMessage(content=f"You are {self.name}. {self.role}. BRUTAL GTM MODE."),
                HumanMessage(content=prompt)
            ])
            import json
            import re
            content = response.content
            # Clean markdown
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            if not content.strip().startswith("{"):
                 # Try to find strict JSON
                 match = re.search(r'\{.*\}', content, re.DOTALL)
                 if match:
                     content = match.group()
            
            return json.loads(content)
        except Exception as e:
            logger.error(f"{self.name} failed", error=str(e))
            return {"error": str(e)}
            
    def get_mission_prompt(self) -> str:
        raise NotImplementedError

# ================= THE DECEMVIRATE =================

class GeneralAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Analyze recent performance and set the STRATEGY for the swarm.
        Identify 1 key weakness and 1 key opportunity for this product right now.
        Output JSON: {"strategy_brief": "...", "focus_weakness": "...", "focus_opportunity": "..."}
        """

class SniperAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Identify 3 specific types of IDEAL HIGH-VALUE CUSTOMERS (ICPs) we must hunt today.
        For each, define the 'Kill Shot' value proposition (the one sentence that gets them).
        Output JSON: {"targets": [{"profile": "...", "kill_shot": "..."}, ...]}
        """

class BansheeAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Draft a VIRAL THREAD (X/Twitter style) that is controversial, loud, or "Reality Distorting".
        It must stop the scroll. No corporate speak.
        Output JSON: {"thread_hook": "...", "thread_body": "...", "estimated_virality": 95}
        """

class SpyAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Simulate a competitor analysis. Identify the biggest rival feature we need to crush.
        Explain HOW we position against it.
        Output JSON: {"rival_feature": "...", "counter_narrative": "..."}
        """

class ArchitectAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Design the structure for a "Skyscraper" SEO article that dominates a specific high-volume keyword.
        Outline the headers and the 'Unfair Advantage' content block.
        Output JSON: {"target_keyword": "...", "article_outline": ["H1...", "H2..."], "unfair_content": "..."}
        """

class RiotAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Draft a script to incite engagement in a Discord or Reddit community. 
        It shouldn't look like marketing. It should look like a revolution or a leaked secret.
        Output JSON: {"platform": "Reddit", "subreddit": "r/...", "post_title": "...", "post_body": "..."}
        """

class DirectorAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Script a 30-second vertical video (TikTok/Shorts) that is visually arresting.
        Describe the first 3 seconds (Hook) in extreme detail.
        Output JSON: {"video_title": "...", "visual_hook": "...", "script": "..."}
        """

class ArtistAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Generate a detailed Midjourney v6 Prompt for a 'Hero Image' that defines this product's soul.
        Style: 'Nano Bananas' (Cyberpunk, Vibrant, AAA).
        Output JSON: {"image_prompt": "...", "style_notes": "..."}
        """

class HackerAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Propose ONE unconventional 'Growth Hack' experiment to test today.
        Something borderline, clever, or automated.
        Output JSON: {"experiment_name": "...", "hypothesis": "...", "execution_steps": "..."}
        """

class CloserAgent(SwarmAgentBase):
    def get_mission_prompt(self) -> str:
        return """
        Draft the text for a 'Closing' email to a warm lead who is hesitating on price.
        Use 'Loss Aversion' and 'Scarcity'.
        Output JSON: {"email_subject": "...", "email_body": "..."}
        """

# Registry
SWARM_AGENTS = {
    "general": GeneralAgent("The General", "Strategy"),
    "sniper": SniperAgent("The Sniper", "Outbound"),
    "banshee": BansheeAgent("The Banshee", "Social"),
    "spy": SpyAgent("The Spy", "Intel"),
    "architect": ArchitectAgent("The Architect", "SEO"),
    "riot": RiotAgent("The Riot", "Community"),
    "director": DirectorAgent("The Director", "Video"),
    "artist": ArtistAgent("The Artist", "Visuals"),
    "hacker": HackerAgent("The Hacker", "Growth"),
    "closer": CloserAgent("The Closer", "Sales"),
}
