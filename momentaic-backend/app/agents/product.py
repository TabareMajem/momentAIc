"""
ProductSuperAgent (The Builder)
Consolidates PM, Design, Tech Lead, and QA into a single product development engine.
"""
from typing import Dict, Any, List, TypedDict
import structlog
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage

from app.agents.base import get_llm
from app.agents.product_pm_agent import product_pm_agent
from app.agents.design_agent import design_agent
from app.agents.tech_lead_agent import tech_lead_agent
from app.agents.qa_tester_agent import qa_tester_agent

logger = structlog.get_logger()

# Remove dataclass decorator and inheritance from Dict
class ProductState(TypedDict):
    """Unified State for Product Operations"""
    messages: List[Any]
    mission: str # "spec_feature", "review_code", "qa_test"
    requirement: Dict[str, Any]
    startup_context: Dict[str, Any]
    spec: Dict[str, Any]
    design: Dict[str, Any]
    code: Dict[str, Any]
    qa_report: Dict[str, Any]
    user_id: str

class ProductSuperAgent:
    def __init__(self):
        self.llm = get_llm("gemini-2.5-flash", temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(ProductState)
        
        # Core Nodes
        workflow.add_node("pm_spec", self._pm_node)
        workflow.add_node("design_ux", self._design_node)
        workflow.add_node("tech_architect", self._tech_node)
        workflow.add_node("qa_review", self._qa_node)
        
        # Edges
        workflow.set_entry_point("pm_spec")
        workflow.add_edge("pm_spec", "design_ux")
        workflow.add_edge("design_ux", "tech_architect")
        workflow.add_edge("tech_architect", "qa_review")
        workflow.add_edge("qa_review", END)
        
        return workflow.compile(checkpointer=MemorySaver())

    async def _pm_node(self, state: ProductState) -> ProductState:
        logger.info("ProductAgent: PM - Drafting Spec")
        requirement = state.get("requirement", {})
        startup_context = state.get("startup_context", {})
        
        # Real logic: Use ProductPMAgent to generate PRD
        feature_name = requirement.get("feature_name", "New Feature")
        feature_desc = requirement.get("description", "")
        
        # Combine into context for PRD generation
        context = {**startup_context, "description": feature_desc}
        
        # Call the real agent
        prd_result = await product_pm_agent.generate_prd(
            feature_name=feature_name,
            context=context
        )
        
        return {
            "spec": prd_result.get("prd", {}),
            "messages": [AIMessage(content=f"PRD Drafted for {feature_name}")]
        }

    async def _design_node(self, state: ProductState) -> ProductState:
        logger.info("ProductAgent: Design - Creating UX")
        spec = state.get("spec", {})
        startup_context = state.get("startup_context", {})
        
        # Real logic: Use DesignAgent to generate brand/UI concepts
        # For now, we'll ask for a UI critique/proposal based on the spec
        spec_text = str(spec)
        prompt = f"Create a UI/UX design concept for this feature spec: {spec_text[:500]}..."
        
        design_result = await design_agent.process(
            message=prompt,
            startup_context=startup_context,
            user_id=state.get("user_id", "system")
        )
        
        return {
            "design": design_result,
            "messages": [AIMessage(content="Design Concept Created")]
        }

    async def _tech_node(self, state: ProductState) -> ProductState:
        logger.info("ProductAgent: Tech Lead - Reviewing Feasibility")
        spec = state.get("spec", {})
        design = state.get("design", {})
        startup_context = state.get("startup_context", {})
        
        # Real logic: Use TechLeadAgent to review architecture + stack
        combined_input = f"Spec: {str(spec)[:300]}... Design: {str(design)[:300]}..."
        
        tech_result = await tech_lead_agent.review_architecture(
            architecture_description=combined_input,
            startup_context=startup_context
        )
        
        return {
            "code": tech_result, # Architecture review
            "messages": [AIMessage(content="Technical Feasibility Reviewed")]
        }
        
    async def _qa_node(self, state: ProductState) -> ProductState:
        logger.info("ProductAgent: QA - Testing Plan")
        spec = state.get("spec", {})
        startup_context = state.get("startup_context", {})
        
        # Real logic: Use QATesterAgent to generate test plan (simulated via process)
        # Note: QATester usually audits URLs. Here we ask for a TEST PLAN.
        prompt = f"Draft a QA Test Plan for this feature spec: {str(spec)[:500]}..."
        
        qa_result = await qa_tester_agent.process(
            message=prompt,
            startup_context=startup_context,
            user_id=state.get("user_id", "system")
        )
        
        return {
            "qa_report": qa_result,
            "messages": [AIMessage(content="QA Test Plan Generated")]
        }

    async def run(self, mission: str, requirement: Dict[str, Any], startup_context: Dict[str, Any], user_id: str):
        import time
        start_time = time.time()
        
        initial_state = {
            "messages": [],
            "mission": mission,
            "requirement": requirement,
            "startup_context": startup_context,
            "spec": {},
            "design": {},
            "code": {},
            "qa_report": {},
            "user_id": user_id
        }
        config = {"configurable": {"thread_id": f"product_{mission}_{datetime.now().isoformat()}"}}
        result = await self.graph.ainvoke(initial_state, config)
        
        # Persist output to DB
        execution_ms = int((time.time() - start_time) * 1000)
        from app.services.agent_persistence import save_agent_outcome
        await save_agent_outcome(
            agent_name="ProductSuperAgent",
            action_type=mission,
            input_context={"requirement": requirement, "startup": startup_context},
            output_data={"spec": result.get("spec"), "design": result.get("design"), "qa_report": result.get("qa_report")},
            startup_id=startup_context.get("startup_id"),
            user_id=user_id,
            execution_time_ms=execution_ms,
        )
        
        return result

# Singleton
product_agent = ProductSuperAgent()
