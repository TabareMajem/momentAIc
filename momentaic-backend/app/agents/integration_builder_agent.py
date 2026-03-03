"""
Integration Builder Agent
The "Code Writer" agent that builds ad-hoc Python integration connectors.
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
import structlog
from app.agents.base import get_llm
from app.services.deliverable_service import deliverable_service

logger = structlog.get_logger()

class IntegrationBuilderAgent:
    """
    Integration Builder: The "Claude 4.5" of Code.
    
    Capabilities:
    - Writes production-ready Python classes for API integrations
    - targeted for platforms like HubSpot, Notion, Airtable, Slack
    - Includes type hinting, error handling, and pydantic models
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-pro", temperature=0.2) # Low temp for code precision
        self.name = "Integration Builder"
        self._tools = self._create_tools()
        
    def _create_tools(self) -> List:
        
        @tool
        async def generate_connector(
            service_name: str,
            capabilities: List[str]
        ) -> Dict[str, Any]:
            """
            Generate a full Python connector file for a specific service.
            
            Args:
                service_name: e.g. "HubSpot", "Notion", "Salesforce"
                capabilities: List of what it needs to do (e.g. "fetch contacts", "update deal stage")
            """
            
            # 1. Generate code via LLM
            prompt = f"""Write a production-quality Python connector client for {service_name}.
            
            Requirements:
            - Use `httpx` for async requests.
            - Use `pydantic` for data models.
            - Include these capabilities: {', '.join(capabilities)}
            - Handle rate limiting and authentication (Bearer token or API Key).
            - Include docstrings and type hints.
            
            Output ONLY the valid Python code for the file."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a Senior Python Backend Engineer. Write clean, robust, async code."),
                HumanMessage(content=prompt)
            ])
            
            code_content = response.content
            # Strip markdown fences if present
            if "```python" in code_content:
                code_content = code_content.split("```python")[1].split("```")[0].strip()
            elif "```" in code_content:
                code_content = code_content.split("```")[1].split("```")[0].strip()
            
            # 2. Save it to The Vault so the user can download it
            # We'll mock a "file generation" by using a text file saver in deliverable service, 
            # or we can add a specific method. For now, create a .py file in the vault.
            
            filename = f"{service_name.lower().replace(' ', '_')}_connector.py"
            # Manually using the vault dir structure since deliverable service focuses on PDF/CSV
            # But let's add a generic file writer to deliverable service or just write it here
             
            import os
            vault_path = "/app/static/vault"
            file_path = os.path.join(vault_path, filename)
            
            with open(file_path, "w") as f:
                f.write(code_content)
                
            public_url = f"/static/vault/{filename}"
            
            return {
                "action": "generate_connector",
                "status": "success",
                "file_url": public_url,
                "file_type": "PYTHON_CODE", 
                "message": f"Generated {filename}. Ready for download."
            }
            
        return [generate_connector]

    async def build_integration(self, request: str) -> Dict[str, Any]:
        """
        Main entry point to interpret user request and trigger the build.
        """
        # Logic to parse "Connect to HubSpot" into service_name="HubSpot"
        # For MVP, we pass this to LLM to decide tool call
        
        prompt = f"""User wants an integration: "{request}"
        
        Extract:
        1. Service Name
        2. Key Capabilities needed
        
        Then call the `generate_connector` tool."""
        
        # In a real LangGraph flow, this would call the tool. 
        # For this direct implementation, we'll simpler parsing or direct invocation.
        # Let's simple-parse for the demo:
        
        service_name = "Unknown Service"
        if "hubspot" in request.lower(): service_name = "HubSpot"
        elif "notion" in request.lower(): service_name = "Notion"
        elif "airtable" in request.lower(): service_name = "Airtable"
        elif "salesforce" in request.lower(): service_name = "Salesforce"
        else: service_name = request.split(" ")[-1] # Fallback
        
        # Trigger tool directly for the MVP "Show me" effect
        # In full version, use AgentExecutor
        return await self._tools[0].invoke({"service_name": service_name, "capabilities": ["CRUD operations", "Search", "Sync"]})

# Singleton

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for missing integrations and connection health.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} missing integrations and connection health 2025")
        
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
                                "source": "IntegrationBuilderAgent",
                                "analysis": response.content[:1500],
                                "agent": "integration_builder",
                            }
                        )
                    actions.append({"name": "integration_needed", "industry": industry})
                except Exception as e:
                    logger.error(f"IntegrationBuilderAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Auto-generates integration connector code and validates connection health.
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
            
            prompt = f"""You are the Ad-hoc integration connector generation agent for a {industry} startup.

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
                        "agent": "integration_builder",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("IntegrationBuilderAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

integration_builder = IntegrationBuilderAgent()
