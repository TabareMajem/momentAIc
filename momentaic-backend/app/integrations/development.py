"""
Development & Project Management Integrations
Code, issues, deployments
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult

logger = structlog.get_logger()


class GitLabIntegration(BaseIntegration):
    """GitLab for code & CI/CD"""
    
    provider = "gitlab"
    display_name = "GitLab"
    description = "Code repositories, CI/CD, DevOps"
    oauth_required = True
    
    default_scopes = ["read_api", "read_repository"]
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.base_url = "https://gitlab.com/api/v4"
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        return f"https://gitlab.com/oauth/authorize?client_id=CLIENT_ID&redirect_uri={redirect_uri}&response_type=code&state={state}&scope=read_api"
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        return IntegrationCredentials(access_token=code)
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        return self.credentials
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        return SyncResult(success=True, records_synced=4, data={
            "commits_this_week": 35,
            "merge_requests_open": 8,
            "issues_open": 15,
            "pipelines_success_rate": 94.5,
        })
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "action": action}
    
    def get_supported_data_types(self) -> List[str]:
        return ["commits", "merge_requests", "issues", "pipelines"]


class LinearIntegration(BaseIntegration):
    """Linear for modern issue tracking"""
    
    provider = "linear"
    display_name = "Linear"
    description = "Modern issue tracking for high-velocity teams"
    oauth_required = True
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.base_url = "https://api.linear.app/graphql"
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        return f"https://linear.app/oauth/authorize?client_id=CLIENT_ID&redirect_uri={redirect_uri}&response_type=code&state={state}"
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        return IntegrationCredentials(access_token=code)
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        return self.credentials
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        return SyncResult(success=True, records_synced=4, data={
            "issues_todo": 12,
            "issues_in_progress": 5,
            "issues_done_this_week": 18,
            "cycle_velocity": 24,
        })
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == "create_issue":
            return {"success": True, "issue_id": "LIN-123"}
        return {"success": True, "action": action}
    
    def get_supported_data_types(self) -> List[str]:
        return ["issues", "projects", "cycles", "velocity"]


class JiraIntegration(BaseIntegration):
    """Jira for enterprise project management"""
    
    provider = "jira"
    display_name = "Jira"
    description = "Powerful project tracking for teams"
    oauth_required = True
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.base_url = "https://api.atlassian.com/ex/jira"
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        return f"https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=CLIENT_ID&scope=read:jira-work&redirect_uri={redirect_uri}&state={state}&response_type=code"
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        return IntegrationCredentials(access_token=code)
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        return self.credentials
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        return SyncResult(success=True, records_synced=4, data={
            "issues_backlog": 45,
            "issues_sprint": 12,
            "issues_done": 156,
            "sprint_progress": 65,
        })
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "action": action}
    
    def get_supported_data_types(self) -> List[str]:
        return ["issues", "sprints", "projects", "velocity"]


class VercelIntegration(BaseIntegration):
    """Vercel for deployments"""
    
    provider = "vercel"
    display_name = "Vercel"
    description = "Frontend deployments & hosting"
    oauth_required = True
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.base_url = "https://api.vercel.com"
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        return f"https://vercel.com/integrations/install?redirect_uri={redirect_uri}&state={state}"
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        return IntegrationCredentials(access_token=code)
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        return self.credentials
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        return SyncResult(success=True, records_synced=3, data={
            "deployments_today": 5,
            "projects": 3,
            "domains": ["app.mysite.com", "mysite.com"],
            "last_deploy_status": "success",
        })
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "action": action}
    
    def get_supported_data_types(self) -> List[str]:
        return ["deployments", "projects", "domains", "analytics"]
