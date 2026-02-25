"""
GrowthSuperAgent (The Revenue Engine)
Consolidates Sales, Marketing, and Growth Hacking into a single revenue engine.
"""
import structlog
from typing import Dict, Any, List, TypedDict, Annotated
import operator
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, BaseMessage

from app.agents.base import get_llm
from app.agents.viral_campaign_agent import viral_campaign_agent
from app.agents.sales_agent import sales_agent
from app.agents.marketing_agent import marketing_agent
from app.agents.growth_hacker_agent import growth_hacker_agent

logger = structlog.get_logger()

class GrowthState(TypedDict):
    """Unified State for Growth Operations"""
    messages: Annotated[List[BaseMessage], operator.add]
    mission: str # "viral_campaign", "sales_hunt", "marketing_push", "growth_experiment"
    target: Dict[str, Any]
    startup_context: Dict[str, Any]
    content: Dict[str, Any]
    leads: List[Dict[str, Any]]
    analytics: Dict[str, Any]
    user_id: str

class GrowthSuperAgent:
    def __init__(self):
        self.llm = get_llm("gemini-2.5-flash", temperature=0.9)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(GrowthState)
        
        # Core Nodes
        workflow.add_node("viral_research", self._research_node)
        workflow.add_node("campaign_strategy", self._strategy_node)
        workflow.add_node("execution_layer", self._execute_node)
        
        # Router
        workflow.set_conditional_entry_point(
            self._route_mission,
            {
                "viral": "viral_research",
                "sales": "execution_layer", # Sales agent handles its own research
                "marketing": "campaign_strategy",
                "growth": "campaign_strategy"
            }
        )
        
        workflow.add_edge("viral_research", "execution_layer")
        workflow.add_edge("campaign_strategy", "execution_layer")
        workflow.add_edge("execution_layer", END)
        
        return workflow.compile(checkpointer=MemorySaver())

    def _route_mission(self, state: GrowthState) -> str:
        mission = state.get("mission", "viral_campaign")
        if "viral" in mission:
            return "viral"
        elif "sales" in mission:
            return "sales"
        elif "marketing" in mission:
            return "marketing"
        else:
            return "growth"

    async def _research_node(self, state: GrowthState) -> GrowthState:
        # Viral Research = Generating the content strategy
        campaign_type = state.get("target", {}).get("type", "exit_survey")
        logger.info(f"GrowthAgent: Generating viral assets for {campaign_type}")
        
        # Generate the creative assets here
        target = state.get("target", {})
        assets = await viral_campaign_agent.generate_campaign_assets(
            campaign_type=campaign_type,
            variations=target.get("variations", 1),
            **{k: v for k, v in target.items() if k not in ["type", "variations"]}
        )
        
        # Normalize assets for frontend consumption
        normalized_assets = []
        for asset in assets:
            content = asset.get("content", {})
            campaign_type = asset.get("type", "viral_content")
            
            # Extract common fields based on type
            title = f"{campaign_type.replace('_', ' ').title()} ({asset.get('tone') or asset.get('style', 'Generic')})"
            platform = "Multi-platform"
            hook = ""
            body = ""
            
            if campaign_type == "exit_survey":
                hook = content.get("intro_screen_text", "")
                share_text = content.get("share_text", "")
                body = f"Intro: {hook}\n\nShare: {share_text}\n\n(Full survey questions generated JSON)"
                
            elif campaign_type == "wedding_vows":
                hook = content.get("opening_line", "")
                body = content.get("full_vow", "")
                
            elif campaign_type == "stats_card":
                hook = content.get("share_text", "")
                body = str(content.get("stats", {})) + "\n" + str(content.get("special_abilities", []))
                
            normalized_assets.append({
                "title": title,
                "platform": platform,
                "hook": hook,
                "body": body,
                "raw_content": content,
                "type": campaign_type
            })
        
        return {"content": {"assets": normalized_assets, "status": "generated"}}

    async def _strategy_node(self, state: GrowthState) -> GrowthState:
        mission = state.get("mission")
        startup_context = state.get("startup_context", {})
        target = state.get("target", {})
        
        if "marketing" in mission:
            # delegated to MarketingAgent
            plan = await marketing_agent.generate_campaign_plan(
                template_name=target.get("template", "launch"),
                startup_context=startup_context
            )
            return {"content": {"plan": plan}}
            
        elif "growth" in mission:
            # delegated to GrowthHackerAgent
            experiment = await growth_hacker_agent.design_experiment(
                goal=target.get("goal", "increase_conversion"),
                current_metrics=state.get("analytics", {})
            )
            return {"content": {"experiment": experiment}}
            
        return {"content": {}}

    async def _execute_node(self, state: GrowthState) -> GrowthState:
        mission = state.get("mission")
        startup_context = state.get("startup_context", {})
        user_id = state.get("user_id", "system")
        
        if "viral" in mission:
            # Content has been generated in the research node — return it as drafted
            content = state.get("content")
            return {
                "analytics": {"status": "drafted", "note": "Content ready for review. Connect social APIs to publish."},
                "messages": [AIMessage(content="Campaign Assets Drafted — Ready for Review")]
            }
            
        elif "sales" in mission:
            # Delegate to SalesAgent auto_hunt
            # Note: SalesAgent.auto_hunt is a complex flow, we trigger it here
            await sales_agent.auto_hunt(
                startup_context=startup_context,
                user_id=user_id
            )
            return {
                "leads": [{"status": "hunting_started"}],
                "messages": [AIMessage(content="Sales Hunter Agent Deployed")]
            }
            
        elif "marketing" in mission:
            # Delegate execution (e.g. creating a post)
            if state.get("target", {}).get("action") == "create_post":
                 post = await marketing_agent.create_social_post(
                     context=str(state.get("target")),
                     platform=state.get("target", {}).get("platform", "linkedin")
                 )
                 return {
                     "content": {"post": post},
                     "messages": [AIMessage(content="Social Post Drafted")]
                 }
                 
        return {"messages": [AIMessage(content=f"Mission {mission} executed")]}

    async def run(self, mission: str, target: Dict[str, Any], startup_context: Dict[str, Any], user_id: str):
        import time
        start_time = time.time()
        
        initial_state = {
            "messages": [],
            "mission": mission,
            "target": target,
            "startup_context": startup_context,
            "content": {},
            "leads": [],
            "analytics": {},
            "user_id": user_id
        }
        config = {"configurable": {"thread_id": f"growth_{mission}_{datetime.now().isoformat()}"}}
        result = await self.graph.ainvoke(initial_state, config)
        
        # Persist output to DB
        execution_ms = int((time.time() - start_time) * 1000)
        from app.services.agent_persistence import save_agent_outcome
        await save_agent_outcome(
            agent_name="GrowthSuperAgent",
            action_type=mission,
            input_context={"target": target, "startup": startup_context},
            output_data={"content": result.get("content"), "leads": result.get("leads"), "analytics": result.get("analytics")},
            startup_id=startup_context.get("startup_id"),
            user_id=user_id,
            execution_time_ms=execution_ms,
        )
        
        return result

# Singleton
growth_agent = GrowthSuperAgent()
