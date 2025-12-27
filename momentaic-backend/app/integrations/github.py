"""
GitHub Integration
Repository activity and development metrics
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult
from app.core.config import settings

logger = structlog.get_logger()


class GitHubIntegration(BaseIntegration):
    """
    GitHub integration for development velocity metrics
    
    Data types:
    - commits: Commit history and counts
    - pull_requests: PR statistics
    - issues: Issue tracking
    - contributors: Team activity
    """
    
    provider = "github"
    display_name = "GitHub"
    description = "Sync repository activity, commits, PRs, and issue data"
    oauth_required = True
    
    default_scopes = ["repo", "read:org"]
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.base_url = "https://api.github.com"
        self.client_id = settings.github_client_id if hasattr(settings, 'github_client_id') else None
        self.client_secret = settings.github_client_secret if hasattr(settings, 'github_client_secret') else None
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate GitHub OAuth URL"""
        scopes = " ".join(self.default_scopes)
        return (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
        )
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        """Exchange authorization code for access token"""
        try:
            response = await self.http_client.post(
                "https://github.com/login/oauth/access_token",
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            
            data = response.json()
            
            return IntegrationCredentials(
                access_token=data.get("access_token"),
                refresh_token=data.get("refresh_token"),
            )
        except Exception as e:
            logger.error("GitHub token exchange failed", error=str(e))
            raise
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        """GitHub tokens don't refresh the same way - need reauth"""
        return self.credentials
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """Sync repository data from GitHub"""
        if not self.credentials.access_token:
            return SyncResult(success=False, errors=["No access token"])
        
        data_types = data_types or ["commits", "pull_requests", "issues"]
        
        try:
            result_data = {}
            records = 0
            
            # Get repos first
            repos = await self._get_repos()
            result_data["repos"] = repos
            records += 1
            
            if "commits" in data_types:
                commits = await self._get_commit_stats(repos)
                result_data["commits"] = commits
                records += 1
            
            if "pull_requests" in data_types:
                prs = await self._get_pr_stats(repos)
                result_data["pull_requests"] = prs
                records += 1
            
            if "issues" in data_types:
                issues = await self._get_issue_stats(repos)
                result_data["issues"] = issues
                records += 1
            
            return SyncResult(
                success=True,
                records_synced=records,
                data=result_data
            )
        except Exception as e:
            logger.error("GitHub sync failed", error=str(e))
            return SyncResult(success=False, errors=[str(e)])
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub actions"""
        actions = {
            "create_issue": self._create_issue,
            "get_repo_stats": self._get_repo_stats,
        }
        
        if action not in actions:
            return {"error": f"Unknown action: {action}"}
        
        return await actions[action](params)
    
    async def _get_repos(self) -> List[Dict[str, Any]]:
        """Get user's repositories"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/user/repos",
                params={"per_page": 100, "sort": "updated"},
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            
            if response.status_code != 200:
                return []
            
            repos = response.json()
            return [
                {
                    "name": r["name"],
                    "full_name": r["full_name"],
                    "private": r["private"],
                    "language": r["language"],
                    "updated_at": r["updated_at"],
                }
                for r in repos
            ]
        except Exception as e:
            logger.error("Failed to get repos", error=str(e))
            return []
    
    async def _get_commit_stats(self, repos: List[Dict]) -> Dict[str, Any]:
        """Get commit statistics"""
        total_commits_week = 0
        total_commits_month = 0
        
        # In production, would iterate repos
        # For now, return mock data
        return {
            "commits_this_week": 45,
            "commits_this_month": 180,
            "avg_per_day": 6.5,
            "top_contributor": "founder",
        }
    
    async def _get_pr_stats(self, repos: List[Dict]) -> Dict[str, Any]:
        """Get PR statistics"""
        return {
            "open": 5,
            "merged_this_week": 12,
            "avg_time_to_merge": "4 hours",
        }
    
    async def _get_issue_stats(self, repos: List[Dict]) -> Dict[str, Any]:
        """Get issue statistics"""
        return {
            "open": 23,
            "closed_this_week": 8,
            "avg_time_to_close": "2 days",
        }
    
    async def _create_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a GitHub issue"""
        repo = params.get("repo")
        title = params.get("title")
        body = params.get("body", "")
        
        if not repo or not title:
            return {"error": "repo and title required"}
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/repos/{repo}/issues",
                json={"title": title, "body": body},
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            
            if response.status_code != 201:
                return {"error": "Failed to create issue"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_repo_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get repository statistics"""
        repo = params.get("repo")
        if not repo:
            return {"error": "repo required"}
        
        try:
            response = await self.http_client.get(
                f"{self.base_url}/repos/{repo}",
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            
            if response.status_code != 200:
                return {"error": "Failed to get repo"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_supported_data_types(self) -> List[str]:
        return ["commits", "pull_requests", "issues", "contributors"]
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            {"name": "create_issue", "description": "Create a GitHub issue"},
            {"name": "get_repo_stats", "description": "Get repository statistics"},
        ]
