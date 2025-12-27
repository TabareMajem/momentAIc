"""
Base Integration Class
Foundation for all external service integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import structlog
import httpx

logger = structlog.get_logger()


@dataclass
class IntegrationCredentials:
    """Credentials for an integration"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at


@dataclass
class SyncResult:
    """Result of a data sync operation"""
    success: bool
    records_synced: int = 0
    errors: List[str] = None
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.data is None:
            self.data = {}


class BaseIntegration(ABC):
    """
    Base class for all integrations
    
    Subclasses must implement:
    - get_auth_url(): Return OAuth URL
    - exchange_code(): Exchange auth code for tokens
    - refresh_tokens(): Refresh expired tokens
    - sync_data(): Sync data from the service
    - execute_action(): Execute an action on the service
    """
    
    provider: str = "base"
    display_name: str = "Base Integration"
    description: str = "Base integration class"
    oauth_required: bool = True
    
    # Scopes to request during OAuth
    default_scopes: List[str] = []
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        self.credentials = credentials or IntegrationCredentials()
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate OAuth authorization URL"""
        pass
    
    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        """Exchange authorization code for tokens"""
        pass
    
    @abstractmethod
    async def refresh_tokens(self) -> IntegrationCredentials:
        """Refresh expired tokens"""
        pass
    
    @abstractmethod
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """Sync data from the service"""
        pass
    
    @abstractmethod
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action on the service (send email, post, etc.)"""
        pass
    
    async def verify_connection(self) -> bool:
        """Verify the integration is still connected"""
        try:
            result = await self.sync_data([])
            return result.success
        except Exception as e:
            logger.error("Connection verification failed", provider=self.provider, error=str(e))
            return False
    
    async def ensure_valid_token(self) -> bool:
        """Ensure access token is valid, refresh if needed"""
        if self.credentials.is_expired():
            try:
                self.credentials = await self.refresh_tokens()
                return True
            except Exception as e:
                logger.error("Token refresh failed", provider=self.provider, error=str(e))
                return False
        return True
    
    def get_supported_data_types(self) -> List[str]:
        """Return list of data types this integration can sync"""
        return []
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        """Return list of actions this integration supports"""
        return []
    
    async def close(self):
        """Cleanup resources"""
        await self.http_client.aclose()
