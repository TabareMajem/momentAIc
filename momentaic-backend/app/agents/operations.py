"""
OperationsSuperAgent (The Operator)
Consolidates Finance, Legal, HR, and Support into a single ops engine.
"""
import structlog
from typing import Dict, Any, List, TypedDict
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage

from app.agents.base import get_llm
from app.agents.finance_cfo_agent import finance_cfo_agent
from app.agents.legal_counsel_agent import legal_counsel_agent
from app.agents.hr_operations_agent import hr_operations_agent

logger = structlog.get_logger()

# Remove dataclass decorator and inheritance from Dict
class OperationsState(TypedDict):
    """Unified State for Ops"""
    messages: List[Any]
    mission: str # "audit_compliance", "review_contract", "hr_policy", "financial_review"
    context: Dict[str, Any]
    startup_context: Dict[str, Any]
    report: Dict[str, Any]
    approval_needed: bool
    user_id: str

class OperationsSuperAgent:
    def __init__(self):
        self.llm = get_llm("gemini-2.5-flash", temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(OperationsState)
        
        # Core Nodes
        workflow.add_node("compliance_check", self._compliance_node)
        workflow.add_node("financial_review", self._finance_node)
        workflow.add_node("hr_policy", self._hr_node)
        
        # Router
        workflow.set_conditional_entry_point(
            self._route_mission,
            {
                "compliance": "compliance_check",
                "finance": "financial_review",
                "hr": "hr_policy"
            }
        )
        
        workflow.add_edge("compliance_check", END)
        workflow.add_edge("financial_review", END)
        workflow.add_edge("hr_policy", END)
        
        return workflow.compile(checkpointer=MemorySaver())

    def _route_mission(self, state: OperationsState) -> str:
        mission = state.get("mission", "compliance")
        logger.info("OpsAgent: Routing", mission=mission, state_keys=list(state.keys()))
        if "contract" in mission or "legal" in mission or "compliance" in mission:
            return "compliance"
        elif "finance" in mission or "money" in mission or "audit" in mission:
            return "finance"
        else:
            return "hr"

    async def _compliance_node(self, state: OperationsState) -> OperationsState:
        logger.info("OpsAgent: Running Compliance Check")
        startup_context = state.get("startup_context", {})
        context = state.get("context", {})
        
        # Real logic: Use LegalCounselAgent
        # If it's a contract review, call review_contract
        if state.get("mission") and "contract" in state.get("mission"):
             result = await legal_counsel_agent.review_contract(
                 contract_type=context.get("type", "generic"),
                 contract_summary=context.get("summary", ""),
                 key_terms=context.get("terms", {})
             )
             return {"report": result, "messages": [AIMessage(content="Contract Reviewed")]}
        
        # Default to compliance check
        result = await legal_counsel_agent.compliance_check(
            industry=startup_context.get("industry", "Technology"),
            location=startup_context.get("location", "US"),
            business_model=startup_context.get("business_model", "SaaS")
        )
        return {"report": result, "messages": [AIMessage(content="Compliance Check Complete")]}

    async def _finance_node(self, state: OperationsState) -> OperationsState:
        logger.info("OpsAgent: Running Financial Review")
        startup_context = state.get("startup_context", {})
        context = state.get("context", {})
        
        # Real logic: Use FinanceCFOAgent
        metrics = context.get("metrics", {})
        if not metrics:
             # If no metrics provided, try to find them in startup_context or mock
             metrics = startup_context.get("financials", {"mrr": 0})
             
        if state.get("mission") and "readiness" in state.get("mission"):
            result = await finance_cfo_agent.fundraising_readiness(
                metrics=metrics,
                target_raise=context.get("target_raise", 1000000)
            )
            return {"report": result, "messages": [AIMessage(content="Fundraising Assessment Complete")]}
            
        # Default to metrics analysis
        result = await finance_cfo_agent.analyze_metrics(
             metrics=metrics
        )
        return {"report": result, "messages": [AIMessage(content="Financial Analysis Complete")]}

    async def _hr_node(self, state: OperationsState) -> OperationsState:
        logger.info("OpsAgent: HR Policy Check")
        startup_context = state.get("startup_context", {})
        context = state.get("context", {})
        
        # Real logic: Use HROperationsAgent
        if "recruiting" in state.get("mission") or "job" in state.get("mission"):
             jd = await hr_operations_agent.generate_job_description(
                 role=context.get("role", "Engineer"),
                 level=context.get("level", "Senior"),
                 requirements=context.get("requirements", [])
             )
             return {"report": {"job_description": jd}, "messages": [AIMessage(content="Job Description Generated")]}
             
        # Default to org structure recommendation
        result = await hr_operations_agent.recommend_org_structure(
             team_size=context.get("team_size", 5),
             stage=startup_context.get("stage", "Seed")
        )
        return {"report": result, "messages": [AIMessage(content="Org Structure Recommended")]}

    async def run(self, mission: str, context: Dict[str, Any], startup_context: Dict[str, Any], user_id: str):
        import time
        start_time = time.time()
        
        initial_state = {
            "messages": [],
            "mission": mission,
            "context": context,
            "startup_context": startup_context,
            "report": {},
            "approval_needed": False,
            "user_id": user_id
        }
        config = {"configurable": {"thread_id": f"ops_{mission}_{datetime.now().isoformat()}"}}
        result = await self.graph.ainvoke(initial_state, config)
        
        # Persist output to DB
        execution_ms = int((time.time() - start_time) * 1000)
        from app.services.agent_persistence import save_agent_outcome
        await save_agent_outcome(
            agent_name="OperationsSuperAgent",
            action_type=mission,
            input_context={"context": context, "startup": startup_context},
            output_data={"report": result.get("report"), "approval_needed": result.get("approval_needed")},
            startup_id=startup_context.get("startup_id"),
            user_id=user_id,
            execution_time_ms=execution_ms,
        )
        
        return result

# Singleton
operations_agent = OperationsSuperAgent()
