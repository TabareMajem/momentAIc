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
            vault_path = "/root/momentaic/momentaic-backend/static/vault"
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
integration_builder = IntegrationBuilderAgent()
