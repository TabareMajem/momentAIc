"""
Sales Hunter Agent
LangGraph-based autonomous sales agent with human-in-the-loop
"""

from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog

from app.agents.base import (
    AgentState,
    get_llm,
    get_agent_config,
    web_search,
    linkedin_search,
    company_research,
    draft_email,
)
from app.models.conversation import AgentType
from app.models.growth import Lead, LeadStatus

logger = structlog.get_logger()


@dataclass
class SalesAgentState(AgentState):
    """Extended state for Sales Agent"""
    lead_info: Dict[str, Any] = None
    research_results: Dict[str, Any] = None
    outreach_strategy: Dict[str, Any] = None
    draft_message: Dict[str, Any] = None
    approval_status: str = "pending"  # pending, approved, rejected
    approval_feedback: Optional[str] = None


class SalesAgent:
    """
    Sales Hunter Agent - Autonomous lead research and outreach
    
    Workflow:
    1. Research → Gather info about lead and company
    2. Strategy → Determine best approach/hook
    3. Draft → Create personalized outreach
    4. Human Review → Wait for approval
    5. Execute → Send message (if approved)
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.SALES_HUNTER)
        self.llm = get_llm("gemini-pro", temperature=0.7)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create graph
        workflow = StateGraph(SalesAgentState)
        
        # Add nodes
        workflow.add_node("research", self._research_node)
        workflow.add_node("strategize", self._strategize_node)
        workflow.add_node("draft", self._draft_node)
        workflow.add_node("human_review", self._human_review_node)
        workflow.add_node("execute", self._execute_node)
        
        # Add edges
        workflow.set_entry_point("research")
        workflow.add_edge("research", "strategize")
        workflow.add_edge("strategize", "draft")
        workflow.add_edge("draft", "human_review")
        
        # Conditional edge based on approval
        workflow.add_conditional_edges(
            "human_review",
            self._check_approval,
            {
                "approved": "execute",
                "rejected": END,
                "pending": "human_review",  # Wait
            }
        )
        
        workflow.add_edge("execute", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _research_node(self, state: SalesAgentState) -> SalesAgentState:
        """
        Node 1: Research the lead and company
        """
        logger.info("Sales Agent: Researching lead", lead=state.get("lead_info", {}).get("contact_name"))
        
        lead_info = state.get("lead_info", {})
        company_name = lead_info.get("company_name", "Unknown")
        contact_name = lead_info.get("contact_name", "Unknown")
        
        # Execute research tools
        research_results = {
            "company_research": company_research.invoke(company_name),
            "contact_linkedin": linkedin_search.invoke(contact_name, company_name),
            "recent_news": web_search.invoke(f"{company_name} recent news"),
            "researched_at": datetime.utcnow().isoformat(),
        }
        
        state["research_results"] = research_results
        state["messages"].append(
            AIMessage(content=f"Completed research on {company_name} and {contact_name}")
        )
        
        return state
    
    async def _strategize_node(self, state: SalesAgentState) -> SalesAgentState:
        """
        Node 2: Determine the best outreach strategy
        """
        logger.info("Sales Agent: Developing strategy")
        
        lead_info = state.get("lead_info", {})
        research = state.get("research_results", {})
        startup_context = state.get("startup_context", {})
        
        if not self.llm:
             # Fallback if no LLM
            strategy = {
                "hook": "Error: AI Service Unavailable",
                "angle": "N/A",
                "tone": "N/A",
                "key_points": [],
                "error": True
            }
        else:
            # Use LLM to develop strategy
            prompt = f"""Based on this research, develop an outreach strategy.

Lead Info:
- Name: {lead_info.get('contact_name')}
- Company: {lead_info.get('company_name')}
- Title: {lead_info.get('contact_title')}

Research Results:
{research}

Our Startup:
- Name: {startup_context.get('name')}
- Description: {startup_context.get('description')}
- Value Prop: {startup_context.get('tagline')}

Determine:
1. The best "hook" (recent news, shared connection, pain point)
2. The angle to approach them
3. The tone (professional, casual, bold)
4. 3 key points to include

Respond in JSON format."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt)
            ])
            
            # Parse response (in production, use structured output)
            strategy = {
                "hook": "Recent company achievement",
                "angle": "Solution alignment",
                "tone": "professional",
                "key_points": response.content.split("\n")[:3],
                "raw_response": response.content,
            }
        
        state["outreach_strategy"] = strategy
        state["messages"].append(
            AIMessage(content=f"Strategy developed: Using '{strategy['hook']}' hook")
        )
        
        return state
    
    async def _draft_node(self, state: SalesAgentState) -> SalesAgentState:
        """
        Node 3: Draft the outreach message
        """
        logger.info("Sales Agent: Drafting message")
        
        lead_info = state.get("lead_info", {})
        strategy = state.get("outreach_strategy", {})
        startup_context = state.get("startup_context", {})
        
        if not self.llm:
             draft = {
                "subject": "Error: AI Service Unavailable",
                "body": "Unable to draft message without AI service.",
                "channel": "email",
                "error": True
            }
        else:
            # Use LLM to draft
            prompt = f"""Draft a personalized outreach email based on this strategy.

Recipient: {lead_info.get('contact_name')} at {lead_info.get('company_name')}
Strategy:
- Hook: {strategy.get('hook')}
- Angle: {strategy.get('angle')}
- Tone: {strategy.get('tone')}
- Key Points: {strategy.get('key_points')}

Our Company: {startup_context.get('name')} - {startup_context.get('tagline')}

Write a compelling, short email (under 150 words) that:
1. Opens with the hook
2. Connects to their pain point
3. Briefly mentions our solution
4. Has a clear, low-commitment CTA

Return as JSON with 'subject' and 'body' fields."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert at writing cold outreach emails that get responses."),
                HumanMessage(content=prompt)
            ])
            
            draft = {
                "subject": f"Quick question for {lead_info.get('contact_name')}",
                "body": response.content,
                "channel": "email",
            }
        
        state["draft_message"] = draft
        state["messages"].append(
            AIMessage(content=f"Draft created with subject: {draft['subject']}")
        )
        
        return state
    
    async def _human_review_node(self, state: SalesAgentState) -> SalesAgentState:
        """
        Node 4: Wait for human approval
        This node pauses execution until approval is received
        """
        logger.info("Sales Agent: Waiting for human approval")
        
        # In practice, this creates an approval request in the database
        # and the workflow pauses until the user approves/rejects
        
        state["messages"].append(
            AIMessage(content="Draft ready for review. Waiting for approval...")
        )
        
        # The approval_status will be updated externally when user decides
        return state
    
    def _check_approval(self, state: SalesAgentState) -> Literal["approved", "rejected", "pending"]:
        """
        Conditional check for approval status
        """
        status = state.get("approval_status", "pending")
        logger.info("Sales Agent: Checking approval", status=status)
        return status
    
    async def _execute_node(self, state: SalesAgentState) -> SalesAgentState:
        """
        Node 5: Execute the outreach (send email)
        """
        logger.info("Sales Agent: Executing outreach")
        
        draft = state.get("draft_message", {})
        lead_info = state.get("lead_info", {})
        
        # In production, actually send the email via Gmail API / SendGrid
        # For now, we mark it as sent
        
        state["final_response"] = f"Email sent to {lead_info.get('contact_email')}"
        state["messages"].append(
            AIMessage(content=f"✅ Outreach sent to {lead_info.get('contact_name')}")
        )
        
        return state
    
    async def run(
        self,
        lead: Lead,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Run the sales agent workflow for a lead
        """
        initial_state: SalesAgentState = {
            "messages": [],
            "startup_context": startup_context,
            "user_id": user_id,
            "startup_id": str(lead.startup_id),
            "current_agent": "sales_hunter",
            "tool_results": [],
            "should_route": False,
            "route_to": None,
            "final_response": None,
            "lead_info": {
                "id": str(lead.id),
                "company_name": lead.company_name,
                "company_website": lead.company_website,
                "contact_name": lead.contact_name,
                "contact_title": lead.contact_title,
                "contact_email": lead.contact_email,
                "contact_linkedin": lead.contact_linkedin,
            },
            "research_results": None,
            "outreach_strategy": None,
            "draft_message": None,
            "approval_status": "pending",
            "approval_feedback": None,
        }
        
        # Run until human review
        config = {"configurable": {"thread_id": str(lead.id)}}
        
        try:
            result = await self.graph.ainvoke(initial_state, config)
            return {
                "status": "waiting_approval",
                "draft": result.get("draft_message"),
                "research": result.get("research_results"),
                "strategy": result.get("outreach_strategy"),
                "thread_id": str(lead.id),
            }
        except Exception as e:
            logger.error("Sales agent error", error=str(e))
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def approve(self, thread_id: str, approved: bool, feedback: Optional[str] = None):
        """
        Continue workflow after human approval
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        # Update state with approval
        update = {
            "approval_status": "approved" if approved else "rejected",
            "approval_feedback": feedback,
        }
        
        if approved:
            # Continue execution
            result = await self.graph.ainvoke(update, config)
            return result
        else:
            return {"status": "rejected", "feedback": feedback}


# Singleton instance
sales_agent = SalesAgent()
