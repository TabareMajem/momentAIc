"""
Cross-Platform SSO Service
Share premium users between MomentAIc and AgentForgeai.com
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac
import json
import base64
import structlog

logger = structlog.get_logger()


class PlatformTier(str, Enum):
    """Premium tiers across platforms"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    SCALE = "scale"
    ACCELERATOR = "accelerator"


@dataclass
class CrossPlatformUser:
    """User synced across platforms"""
    user_id: str
    email: str
    tier: PlatformTier
    platforms: list  # ["momentaic", "agentforge"]
    expires_at: Optional[datetime] = None
    linked_at: datetime = None


class CrossPlatformSSO:
    """
    Cross-Platform Single Sign-On
    
    Allows premium users from AgentForgeai.com to access MomentAIc
    and vice versa without separate subscriptions.
    """
    
    PLATFORMS = {
        "momentaic": {
            "name": "MomentAIc",
            "domain": "momentaic.ai",
            "api_url": "https://api.momentaic.ai"
        },
        "agentforge": {
            "name": "AgentForge AI",
            "domain": "agentforgeai.com",
            "api_url": "https://api.agentforgeai.com"
        }
    }
    
    def __init__(self, shared_secret: str = None):
        """
        Initialize with shared secret between platforms.
        Both platforms must use the same secret for token validation.
        """
        from app.core.config import settings
        self.shared_secret = shared_secret or getattr(settings, 'cross_platform_secret', 'default-secret')
        self._linked_users: Dict[str, CrossPlatformUser] = {}
    
    def generate_sso_token(
        self,
        user_id: str,
        email: str,
        tier: str,
        source_platform: str,
        expires_in_hours: int = 24
    ) -> str:
        """
        Generate SSO token for cross-platform authentication.
        
        This token can be passed to another platform to authenticate.
        """
        payload = {
            "user_id": user_id,
            "email": email,
            "tier": tier,
            "source": source_platform,
            "iat": datetime.utcnow().isoformat(),
            "exp": (datetime.utcnow() + timedelta(hours=expires_in_hours)).isoformat()
        }
        
        # Create signature
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.shared_secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine payload + signature
        token_data = {
            "payload": payload,
            "signature": signature
        }
        
        # Base64 encode
        token = base64.urlsafe_b64encode(
            json.dumps(token_data).encode()
        ).decode()
        
        return token
    
    def validate_sso_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate an SSO token from another platform.
        
        Returns user info if valid, None if invalid.
        """
        try:
            # Decode token
            token_json = base64.urlsafe_b64decode(token.encode()).decode()
            token_data = json.loads(token_json)
            
            payload = token_data.get("payload", {})
            signature = token_data.get("signature", "")
            
            # Verify signature
            payload_json = json.dumps(payload, sort_keys=True)
            expected_sig = hmac.new(
                self.shared_secret.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_sig):
                logger.warning("SSO token signature invalid")
                return None
            
            # Check expiration
            exp = datetime.fromisoformat(payload.get("exp", "2000-01-01"))
            if datetime.utcnow() > exp:
                logger.warning("SSO token expired")
                return None
            
            return payload
            
        except Exception as e:
            logger.error("SSO token validation failed", error=str(e))
            return None
    
    def link_accounts(
        self,
        local_user_id: str,
        sso_token: str
    ) -> Optional[CrossPlatformUser]:
        """
        Link a local account to an external platform account.
        
        After linking, premium tier is shared between platforms.
        """
        # Validate the external token
        external_user = self.validate_sso_token(sso_token)
        if not external_user:
            return None
        
        # Create or update linked user
        email = external_user.get("email")
        external_tier = PlatformTier(external_user.get("tier", "free"))
        source = external_user.get("source")
        
        # Determine highest tier between platforms
        # (If user has PRO on AgentForge, they get PRO on MomentAIc too)
        linked_user = CrossPlatformUser(
            user_id=local_user_id,
            email=email,
            tier=external_tier,
            platforms=["momentaic", source],
            linked_at=datetime.utcnow()
        )
        
        self._linked_users[local_user_id] = linked_user
        
        logger.info(
            "Accounts linked",
            local_user=local_user_id,
            external_source=source,
            tier=external_tier.value
        )
        
        return linked_user
    
    def get_premium_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get cross-platform premium status for a user.
        """
        linked = self._linked_users.get(user_id)
        
        if not linked:
            return {
                "is_linked": False,
                "tier": "free",
                "platforms": ["momentaic"]
            }
        
        return {
            "is_linked": True,
            "tier": linked.tier.value,
            "platforms": linked.platforms,
            "linked_at": linked.linked_at.isoformat() if linked.linked_at else None
        }
    
    def generate_redirect_url(
        self,
        target_platform: str,
        user_id: str,
        email: str,
        tier: str,
        return_url: str = None
    ) -> str:
        """
        Generate redirect URL for cross-platform login.
        
        User clicks this link to seamlessly login to the other platform.
        """
        token = self.generate_sso_token(
            user_id=user_id,
            email=email,
            tier=tier,
            source_platform="momentaic"
        )
        
        platform = self.PLATFORMS.get(target_platform, {})
        api_url = platform.get("api_url", "")
        
        redirect_url = f"{api_url}/sso/login?token={token}"
        if return_url:
            redirect_url += f"&return_url={return_url}"
        
        return redirect_url


# Singleton
_sso_service: Optional[CrossPlatformSSO] = None


def get_sso_service() -> CrossPlatformSSO:
    """Get the cross-platform SSO service"""
    global _sso_service
    if _sso_service is None:
        _sso_service = CrossPlatformSSO()
    return _sso_service
