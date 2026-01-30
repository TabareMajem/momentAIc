"""
Model Context Protocol (MCP) Integration
Universal tool registry exposing all integrations as MCP-compatible tools
for Gemini and other AI models
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import json
import structlog

logger = structlog.get_logger()


@dataclass
class MCPTool:
    """MCP-compatible tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable
    category: str
    requires_auth: bool = False


class MCPToolRegistry:
    """
    Central registry for all MCP-compatible tools
    
    Exposes all 42+ integrations as tools that can be dynamically
    discovered and invoked by AI models (Gemini, Claude, etc.)
    
    Follows MCP spec: https://modelcontextprotocol.io/
    """
    
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._categories: Dict[str, List[str]] = {}
        self._register_integration_tools()
        self._register_agent_tools()
        self._register_action_tools()
    
    def _register_integration_tools(self):
        """Register all integration sync/action tools"""
        from app.integrations import INTEGRATION_REGISTRY
        
        for provider, cls in INTEGRATION_REGISTRY.items():
            # Sync data tool
            self.register_tool(MCPTool(
                name=f"sync_{provider}_data",
                description=f"Sync data from {cls.display_name}: {cls.description}",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific data types to sync (optional)"
                        }
                    }
                },
                handler=self._create_sync_handler(provider),
                category="integrations",
                requires_auth=cls.oauth_required
            ))
            
            # Execute action tool
            self.register_tool(MCPTool(
                name=f"execute_{provider}_action",
                description=f"Execute an action on {cls.display_name}",
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action name"},
                        "params": {"type": "object", "description": "Action parameters"}
                    },
                    "required": ["action"]
                },
                handler=self._create_action_handler(provider),
                category="integrations",
                requires_auth=True
            ))
    
    def _register_agent_tools(self):
        """Register AI agent invocation tools"""
        agents = [
            ("supervisor", "Route queries to specialized agents"),
            ("sales_hunter", "Generate leads, outreach, and close deals"),
            ("content_creator", "Create marketing content, blogs, social posts"),
            ("tech_lead", "Code review, architecture, technical decisions"),
            ("finance_cfo", "Financial analysis, runway, fundraising strategy"),
            ("legal_counsel", "Legal advice, contracts, compliance"),
            ("growth_hacker", "Experiments, virality, acquisition strategies"),
            ("product_pm", "Product roadmap, features, user research"),
            ("customer_success", "Churn analysis, retention, customer health"),
            ("data_analyst", "Analytics, A/B tests, cohort analysis"),
            ("hr_operations", "Hiring, culture, team building"),
            ("marketing", "Brand strategy, campaigns, positioning"),
            ("community", "Community building, engagement, ambassador programs"),
            ("devops", "Infrastructure, CI/CD, security"),
            ("strategy", "Market sizing, pivots, business model"),
            ("browser", "Web automation, research, scraping"),
        ]
        
        for agent_id, description in agents:
            self.register_tool(MCPTool(
                name=f"invoke_{agent_id}_agent",
                description=description,
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Question or task for the agent"},
                        "context": {"type": "object", "description": "Additional context (startup data, etc.)"}
                    },
                    "required": ["query"]
                },
                handler=self._create_agent_handler(agent_id),
                category="agents"
            ))
    
    def _register_action_tools(self):
        """Register direct action tools (agents that DO, not just advise)"""
        actions = [
            ("send_email", "Send email via integrated provider", {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"}
            }),
            ("post_to_social", "Post content to social media", {
                "platform": {"type": "string", "enum": ["linkedin", "twitter", "instagram"]},
                "content": {"type": "string"},
                "media_url": {"type": "string"}
            }),
            ("schedule_meeting", "Schedule a meeting via calendar", {
                "title": {"type": "string"},
                "attendees": {"type": "array", "items": {"type": "string"}},
                "duration_minutes": {"type": "integer"},
                "preferred_times": {"type": "array", "items": {"type": "string"}}
            }),
            ("create_task", "Create a task in project management tool", {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "assignee": {"type": "string"},
                "due_date": {"type": "string"}
            }),
            ("send_slack_message", "Send message to Slack channel", {
                "channel": {"type": "string"},
                "message": {"type": "string"}
            }),
            ("generate_invoice", "Generate and send invoice", {
                "customer_email": {"type": "string"},
                "items": {"type": "array"},
                "currency": {"type": "string", "default": "usd"}
            }),
            ("create_github_issue", "Create issue on GitHub", {
                "repo": {"type": "string"},
                "title": {"type": "string"},
                "body": {"type": "string"},
                "labels": {"type": "array", "items": {"type": "string"}}
            }),
            ("deploy_to_vercel", "Trigger deployment to Vercel", {
                "project": {"type": "string"},
                "branch": {"type": "string", "default": "main"}
            }),
            ("browser_navigate", "Navigate remote browser (OpenClaw)", {
                "url": {"type": "string"},
                "wait_for": {"type": "string", "description": "Selector to wait for"}
            }),
            ("browser_scrape", "Scrape page content (OpenClaw)", {
                "url": {"type": "string"},
                "selector": {"type": "string", "description": "CSS selector to scrape"}
            }),
            ("browser_interact", "Interact with page (OpenClaw)", {
                "action": {"type": "string", "description": "Legacy alias for kind", "enum": ["click", "type", "scroll"]},
                "kind": {"type": "string", "enum": ["click", "type", "scroll", "fill"], "description": "Action type"},
                "ref": {"type": "integer", "description": "Element ref ID from snapshot (Preferred)"},
                "selector": {"type": "string", "description": "CSS selector (Fallback)"},
                "text": {"type": "string", "description": "Text to type"},
                "value": {"type": "string", "description": "Value to set"},
                "wait_for": {"type": "string", "description": "Wait for selector after action"}
            }),

            ("system_command", "Run system command (OpenClaw - Restricted)", {
                "command": {"type": "string"},
                "cwd": {"type": "string"}
            }),
            ("enrich_company", "Enrich company data (Clay)", {
                "domain": {"type": "string", "description": "Company domain (e.g. stripe.com)"}
            }),
            ("find_people", "Find people by role (Clay)", {
                "company_domain": {"type": "string"},
                "job_title_keyword": {"type": "string", "description": "Role keyword (e.g. Marketing, Founder)"}
            }),
            ("sync_crm_person", "Sync person to Attio CRM", {
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "company_name": {"type": "string"}
            }),
            ("sync_crm_company", "Sync company to Attio CRM", {
                "name": {"type": "string"},
                "domain": {"type": "string"}
            }),
            ("add_lead_to_campaign", "Add lead to Instantly campaign", {
                "campaign_id": {"type": "string"},
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "variables": {"type": "object"}
            }),
            ("check_email_replies", "Check Instantly for replies", {
                "campaign_id": {"type": "string"}
            }),
            ("schedule_social_thread", "Schedule a Twitter thread via Typefully", {
                "content": {"type": "string", "description": "Full thread content"},
                "date": {"type": "string", "description": "ISO 8601 date, optional"}
            }),
        ]
        
        for action_id, description, properties in actions:
            self.register_tool(MCPTool(
                name=f"action_{action_id}",
                description=description,
                input_schema={
                    "type": "object",
                    "properties": properties,
                    "required": list(properties.keys())[:2]  # First 2 are required
                },
                handler=self._create_direct_action_handler(action_id),
                category="actions",
                requires_auth=True
            ))
    
    def register_tool(self, tool: MCPTool):
        """Register a new tool"""
        self._tools[tool.name] = tool
        if tool.category not in self._categories:
            self._categories[tool.category] = []
        self._categories[tool.category].append(tool.name)
        logger.debug("Tool registered", name=tool.name, category=tool.category)
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self, category: str = None) -> List[Dict[str, Any]]:
        """List all available tools (MCP format)"""
        tools = []
        for name, tool in self._tools.items():
            if category and tool.category != category:
                continue
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "category": tool.category,
                "requires_auth": tool.requires_auth
            })
        return tools
    
    def get_mcp_manifest(self) -> Dict[str, Any]:
        """Get full MCP manifest for tool discovery"""
        return {
            "name": "momentaic",
            "version": "1.0.0",
            "description": "MomentAIc AI Co-Founder tools for entrepreneurs",
            "tools": self.list_tools(),
            "categories": list(self._categories.keys()),
            "total_tools": len(self._tools)
        }
    
    async def execute_tool(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with params"""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool not found: {name}"}
        
        try:
            result = await tool.handler(params)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error("Tool execution failed", tool=name, error=str(e))
            return {"error": str(e)}
    
    # Handler factories
    def _create_sync_handler(self, provider: str):
        async def handler(params: Dict[str, Any]):
            from app.integrations import INTEGRATION_REGISTRY
            cls = INTEGRATION_REGISTRY.get(provider)
            if not cls:
                return {"error": "Provider not found"}
            # In production, would get credentials from DB
            instance = cls(None)
            return await instance.sync_data(params.get("data_types"))
        return handler
    
    def _create_action_handler(self, provider: str):
        async def handler(params: Dict[str, Any]):
            from app.integrations import INTEGRATION_REGISTRY
            cls = INTEGRATION_REGISTRY.get(provider)
            if not cls:
                return {"error": "Provider not found"}
            instance = cls(None)
            return await instance.execute_action(params["action"], params.get("params", {}))
        return handler
    
    def _create_agent_handler(self, agent_id: str):
        async def handler(params: Dict[str, Any]):
            # Import and invoke the appropriate agent
            from app.agents import AGENT_MAP
            agent = AGENT_MAP.get(agent_id)
            if not agent:
                return {"error": f"Agent not found: {agent_id}"}
            return await agent.process(params["query"], params.get("context"))
        return handler
    
    def _create_direct_action_handler(self, action_id: str):
        async def handler(params: Dict[str, Any]):
            # Check if this is an OpenClaw action
            if action_id in ["browser_navigate", "browser_scrape", "browser_interact", "system_command"]:
                from app.integrations import OpenClawIntegration
                claw = OpenClawIntegration()
                return await claw.execute_action(action_id, params)

            if action_id in ["enrich_company", "find_people"]:
                from app.integrations import ClayIntegration
                clay = ClayIntegration()
                return await clay.execute_action(action_id, params)

            # Attio CRM actions
            if action_id in ["sync_crm_person", "sync_crm_company"]:
                from app.integrations import AttioIntegration
                attio = AttioIntegration()
                # Map action to Attio method
                attio_action = "sync_person" if action_id == "sync_crm_person" else "sync_company"
                return await attio.execute_action(attio_action, params)

            # Instantly email actions
            if action_id in ["add_lead_to_campaign", "check_email_replies"]:
                from app.integrations import InstantlyIntegration
                instantly = InstantlyIntegration()
                instantly_action = "add_lead_to_campaign" if action_id == "add_lead_to_campaign" else "check_replies"
                return await instantly.execute_action(instantly_action, params)

            # Typefully actions
            if action_id == "schedule_social_thread":
                from app.integrations import TypefullyIntegration
                typefully = TypefullyIntegration()
                action = "schedule_thread" if params.get("date") else "create_draft"
                return await typefully.execute_action(action, params)

            # Direct action execution
            # In production, would need approval workflow for sensitive actions
            return {"executed": action_id, "params": params, "status": "pending_approval"}
        return handler


# Singleton registry
_registry: Optional[MCPToolRegistry] = None


def get_mcp_registry() -> MCPToolRegistry:
    """Get the global MCP tool registry"""
    global _registry
    if _registry is None:
        _registry = MCPToolRegistry()
    return _registry
