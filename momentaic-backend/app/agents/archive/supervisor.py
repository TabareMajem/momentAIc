"""
Supervisor Agent
Routes user queries to specialized agents using LangGraph
"""

from typing import Dict, Any, List, Optional, Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
import structlog
import re

from app.agents.base import AgentState, get_llm, get_agent_config, AGENT_CONFIGS
from app.models.conversation import AgentType

logger = structlog.get_logger()


class SupervisorAgent:
    """
    Supervisor Agent - Routes queries to specialized agents
    
    Uses LLM to understand user intent and route to the best agent.
    Can also handle simple queries directly.
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.SUPERVISOR)
        self.llm = get_llm("gemini-pro", temperature=0.3)  # Lower temp for routing
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the supervisor routing graph"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("route", self._route_node)
        workflow.add_node("respond_direct", self._respond_direct_node)
        workflow.add_node("delegate", self._delegate_node)
        
        # Set entry point
        workflow.set_entry_point("analyze")
        
        # Add edges
        workflow.add_edge("analyze", "route")
        
        # Conditional routing
        workflow.add_conditional_edges(
            "route",
            self._should_delegate,
            {
                "delegate": "delegate",
                "direct": "respond_direct",
            }
        )
        
        workflow.add_edge("respond_direct", END)
        workflow.add_edge("delegate", END)
        
        return workflow.compile()
    
    async def _analyze_node(self, state: AgentState) -> AgentState:
        """
        Analyze the user's query to understand intent
        """
        messages = state.get("messages", [])
        if not messages:
            return state
        
        last_message = messages[-1]
        user_query = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        # Quick keyword-based routing for obvious cases
        query_lower = user_query.lower()
        
        # Sales keywords
        if any(kw in query_lower for kw in ["lead", "outreach", "email", "crm", "sales", "prospect", "deal"]):
            state["route_to"] = AgentType.SALES_HUNTER.value
            state["should_route"] = True
            return state
        
        # Content keywords
        if any(kw in query_lower for kw in ["content", "post", "linkedin", "twitter", "article", "blog", "write"]):
            state["route_to"] = AgentType.CONTENT_CREATOR.value
            state["should_route"] = True
            return state
        
        # Tech keywords
        if any(kw in query_lower for kw in ["code", "api", "database", "architecture", "deploy", "bug", "tech stack"]):
            state["route_to"] = AgentType.TECH_LEAD.value
            state["should_route"] = True
            return state
        
        # Finance keywords
        if any(kw in query_lower for kw in ["revenue", "mrr", "arr", "runway", "financial model", "cfo"]):
            state["route_to"] = AgentType.FINANCE_CFO.value
            state["should_route"] = True
            return state

        # Fundraising keywords
        if any(kw in query_lower for kw in ["fundraising", "pitch deck", "investor", "vc", "term sheet", "valuation", "angel", "raise capital"]):
            state["route_to"] = AgentType.FUNDRAISING_COACH.value
            state["should_route"] = True
            return state
        
        
        # Growth keywords
        if any(kw in query_lower for kw in ["growth", "acquisition", "retention", "viral", "experiment", "funnel"]):
            state["route_to"] = AgentType.GROWTH_HACKER.value
            state["should_route"] = True
            return state
        
        # Product keywords
        if any(kw in query_lower for kw in ["feature", "roadmap", "user story", "requirement", "priorit", "backlog"]):
            state["route_to"] = AgentType.PRODUCT_PM.value
            state["should_route"] = True
            return state
        
        # Onboarding/Journey keywords
        if any(kw in query_lower for kw in ["onboarding", "journey", "phase", "stage", "where am i", "what should i", "guide", "help me start"]):
            state["route_to"] = AgentType.ONBOARDING_COACH.value
            state["should_route"] = True
            return state
        
        # Competitor keywords
        if any(kw in query_lower for kw in ["competitor", "competition", "battle card", "versus", " vs ", "compare"]):
            state["route_to"] = AgentType.COMPETITOR_INTEL.value
            state["should_route"] = True
            return state
        
        # Persona keywords
        if any(kw in query_lower for kw in ["elon", "first principles", "hardcore"]):
            state["route_to"] = AgentType.ELON_MUSK.value
            state["should_route"] = True
            return state
            
        if any(kw in query_lower for kw in ["paul graham", "pg", "yc", "y combinator"]):
            state["route_to"] = AgentType.PAUL_GRAHAM.value
            state["should_route"] = True
            return state
        
        # If no clear match, use LLM for routing
        if self.llm:
            state = await self._llm_route(state, user_query)
        else:
            # Default to general agent
            state["route_to"] = AgentType.GENERAL.value
            state["should_route"] = False
        
        return state
    
    async def _llm_route(self, state: AgentState, query: str) -> AgentState:
        """Use LLM to determine routing"""
        
        agent_descriptions = "\n".join([
            f"- {atype.value}: {config['description']}"
            for atype, config in AGENT_CONFIGS.items()
            if atype != AgentType.SUPERVISOR
        ])
        
        prompt = f"""Analyze this user query and determine the best agent to handle it.

User Query: {query}

Available Agents:
{agent_descriptions}

If the query is simple and doesn't need a specialist, respond with "DIRECT".
Otherwise, respond with the agent type (e.g., "sales_hunter", "content_creator").

Respond in this format:
ROUTE: <agent_type or DIRECT>
REASON: <brief explanation>"""
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            content = response.content
            
            # Parse response
            route_match = re.search(r"ROUTE:\s*(\w+)", content)
            if route_match:
                route_to = route_match.group(1).lower()
                
                if route_to == "direct":
                    state["should_route"] = False
                    state["route_to"] = None
                else:
                    # Validate agent type
                    valid_agents = [a.value for a in AgentType if a != AgentType.SUPERVISOR]
                    if route_to in valid_agents:
                        state["should_route"] = True
                        state["route_to"] = route_to
                    else:
                        state["should_route"] = False
                        state["route_to"] = AgentType.GENERAL.value
            else:
                state["should_route"] = False
                state["route_to"] = None
                
        except Exception as e:
            logger.error("LLM routing failed", error=str(e))
            state["should_route"] = False
            state["route_to"] = None
        
        return state
    
    async def _route_node(self, state: AgentState) -> AgentState:
        """
        Routing decision node (mostly pass-through after analysis)
        """
        logger.info(
            "Supervisor: Routing decision",
            should_route=state.get("should_route"),
            route_to=state.get("route_to"),
        )
        return state
    
    def _should_delegate(self, state: AgentState) -> Literal["delegate", "direct"]:
        """
        Conditional edge: should we delegate to another agent?
        """
        if state.get("should_route") and state.get("route_to"):
            return "delegate"
        return "direct"
    
    async def _respond_direct_node(self, state: AgentState) -> AgentState:
        """
        Handle query directly without delegation
        """
        messages = state.get("messages", [])
        if not messages:
            state["final_response"] = "I'm here to help. What would you like to know?"
            return state
        
        last_message = messages[-1]
        user_query = last_message.content if hasattr(last_message, "content") else str(last_message)
        startup_context = state.get("startup_context", {})
        
        if not self.llm:
            state["final_response"] = "AI Service Unavailable. Please configure keys."
            return state
        
        # Build context-aware prompt
        context_section = ""
        if startup_context:
            context_section = f"""
Current Startup Context:
- Name: {startup_context.get('name', 'Your startup')}
- Industry: {startup_context.get('industry', 'Technology')}
- Stage: {startup_context.get('stage', 'Early')}
"""
        
        prompt = f"""{context_section}
User question: {user_query}

Provide a helpful, concise response. If the question would be better handled by a specialist agent, let the user know which one."""
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a helpful AI assistant for startup founders. Be concise and actionable."),
                HumanMessage(content=prompt),
            ])
            state["final_response"] = response.content
        except Exception as e:
            logger.error("Direct response failed", error=str(e))
            state["final_response"] = f"An error occurred: {str(e)}"
        
        return state
    
    async def _delegate_node(self, state: AgentState) -> AgentState:
        """
        Prepare for delegation to specialized agent
        """
        route_to = state.get("route_to")
        agent_config = AGENT_CONFIGS.get(AgentType(route_to), {})
        
        state["final_response"] = None  # Will be filled by delegated agent
        state["current_agent"] = route_to
        
        logger.info(
            "Supervisor: Delegating to agent",
            agent=route_to,
            agent_name=agent_config.get("name"),
        )
        
        return state
    
    async def route(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
        startup_id: str,
    ) -> Dict[str, Any]:
        """
        Route a message through the supervisor
        
        Returns routing decision and optional direct response
        """
        initial_state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "startup_context": startup_context,
            "user_id": user_id,
            "startup_id": startup_id,
            "current_agent": "supervisor",
            "tool_results": [],
            "should_route": False,
            "route_to": None,
            "final_response": None,
        }
        
        try:
            result = await self.graph.ainvoke(initial_state)
            
            return {
                "routed": result.get("should_route", False),
                "route_to": result.get("route_to"),
                "response": result.get("final_response"),
                "agent_used": result.get("current_agent"),
            }
            
        except Exception as e:
            logger.error("Supervisor routing error", error=str(e))
            return {
                "routed": False,
                "route_to": None,
                "response": "I apologize, but I encountered an error processing your request.",
                "error": str(e),
            }


# Singleton instance
supervisor_agent = SupervisorAgent()
