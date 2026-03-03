"""
CX Guardian Agent
Autonomously reads support tickets, searches internal docs for answers, and queues draft replies.
"""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
import structlog
import json

from app.agents.base import get_llm, BaseAgent

logger = structlog.get_logger()

class CXGuardianAgent(BaseAgent):
    """
    CX Guardian Agent - White-glove service without headcount.
    Receives incoming customer support messages, uses OpenClaw to scrape the company's
    public documentation/help center, and drafts highly accurate replies for approval.
    """
    
    def __init__(self):
        self.name = "CX Guardian Agent"
        self.llm = get_llm("gemini-pro", temperature=0.1) # low temp for support accuracy

    async def handle_message(self, msg: Any) -> None:
        """
        Listen to the A2A bus for incoming support tickets.
        If received, scrape docs and draft a reply.
        """
        # Call the base class to store it in memory
        await super().handle_message(msg)
        
        topic = msg.get("topic")
        if topic == "inbound_support_ticket":
            data = msg.get("data", {})
            logger.info(f"Agent {self.name} received support ticket: {data.get('ticket_id', 'unknown')}")
            
            # Start drafting process
            await self._draft_support_reply(data)

    async def _draft_support_reply(self, ticket_data: Dict[str, Any]):
        """
        Core logic to resolve a ticket.
        """
        customer_inquiry = ticket_data.get("message", "")
        customer_email = ticket_data.get("customer_email", "")
        help_center_url = ticket_data.get("help_center_url", "https://docs.momentaic.com") # Default or dynamic
        
        if not customer_inquiry:
            return
            
        # 1. Search documentation using OpenClaw 
        from app.agents.browser_agent import BrowserAgent
        browser = BrowserAgent()
        await browser.initialize()
        
        # Heuristic: search the docs site
        # e.g., site:docs.acme.com "how to reset password"
        search_query = f"site:{help_center_url.replace('https://', '')} {customer_inquiry}"
        
        from app.agents.base import web_search
        results = await web_search(search_query)
        
        doc_context = "No specific documentation found. Please rely on general knowledge or escalate."
        doc_reference_url = ""
        
        if results and "link" in results[0]:
            target_doc_url = results[0]["link"]
            logger.info(f"CX Guardian scraping hit: {target_doc_url}")
            
            nav_result = await browser.navigate(target_doc_url)
            if nav_result.success and nav_result.text_content:
                # We've found the relevant doc page and extracted its text
                doc_context = nav_result.text_content[:4000]
                doc_reference_url = target_doc_url
                
        # 2. Draft the reply
        if self.llm:
            prompt = f"""You are the lead Customer Success Representative for our startup.
            A customer ({customer_email}) just sent this support ticket:
            "{customer_inquiry}"
            
            We used our AI scraper to find the most relevant internal documentation page:
            URL: {doc_reference_url}
            Content:
            {doc_context}
            
            Draft a warm, professional, and concise email reply to the customer solving their problem based strictly on the provided documentation. Include the docs URL if helpful.
            If the documentation does NOT contain the answer, apologize and say you are escalating to an engineer.
            
            Return ONLY a JSON object with:
            - "subject": The email subject line
            - "body": The email body text
            - "confidence": 1-100 score indicating if you actually found the answer in the docs."""
            
            try:
                raw_response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                content = raw_response.content.replace('```json', '').replace('```', '').strip()
                parsed = json.loads(content)
                
                subject = parsed.get("subject", "Re: Support Inquiry")
                body = parsed.get("body", "")
                confidence = parsed.get("confidence", 50)
                
                if body:
                    # 3. Queue for HitL Approval
                    from app.models.action_item import ActionPriority
                    
                    # High confidence = medium priority (easy approval). Low confidence = high priority (founder needs to fix it).
                    priority = ActionPriority.medium.value if confidence > 80 else ActionPriority.high.value
                    
                    await self.publish_to_bus(
                        topic="action_item_proposed",
                        data={
                            "action_type": "send_email",
                            "title": f"Draft Support Reply: {subject}",
                            "description": f"Confidence: {confidence}/100. Reference: {doc_reference_url}",
                            "payload": {
                                "to": customer_email,
                                "subject": subject,
                                "body": body
                            },
                            "priority": priority
                        }
                    )
                    
            except Exception as e:
                logger.error("Failed to parse CX support reply", error=str(e))

# Singleton instance

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for support tickets, customer complaints, and satisfaction drops.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} support tickets, customer complaints, and satisfaction drops 2025")
        
        if results:
            from app.agents.base import get_llm
            llm = get_llm("gemini-pro", temperature=0.3)
            if llm:
                from langchain_core.messages import HumanMessage
                prompt = f"""Analyze these results for a {industry} startup:
{str(results)[:2000]}

Identify the top 3 actionable insights. Be concise."""
                try:
                    response = await llm.ainvoke([HumanMessage(content=prompt)])
                    from app.agents.base import BaseAgent
                    if hasattr(self, 'publish_to_bus'):
                        await self.publish_to_bus(
                            topic="intelligence_gathered",
                            data={
                                "source": "CXGuardianAgent",
                                "analysis": response.content[:1500],
                                "agent": "cx_guardian_agent",
                            }
                        )
                    actions.append({"name": "cx_issue_detected", "industry": industry})
                except Exception as e:
                    logger.error(f"CXGuardianAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Auto-drafts support responses and escalates critical CX issues.
        """
        action_type = action.get("action", action.get("name", "unknown"))

        try:
            from app.agents.base import get_llm, web_search
            from langchain_core.messages import HumanMessage
            
            industry = startup_context.get("industry", "Technology")
            llm = get_llm("gemini-pro", temperature=0.5)
            
            if not llm:
                return "LLM not available"
            
            search_results = await web_search(f"{industry} {action_type} best practices 2025")
            
            prompt = f"""You are the Customer experience monitoring and support automation agent for a {industry} startup.

Based on this context:
- Action requested: {action_type}
- Industry: {industry}
- Research: {str(search_results)[:1500]}

Generate a concrete, actionable deliverable. No fluff. Be specific and executable."""
            
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            if hasattr(self, 'publish_to_bus'):
                await self.publish_to_bus(
                    topic="deliverable_generated",
                    data={
                        "type": action_type,
                        "content": response.content[:2000],
                        "agent": "cx_guardian_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("CXGuardianAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

cx_guardian_agent = CXGuardianAgent()
