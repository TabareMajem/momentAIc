"""
Integrations Module
Complete hub for connecting 40+ external business tools
"""

# Base classes
from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult

# Core Integrations (Previously implemented)
from app.integrations.stripe import StripeIntegration
from app.integrations.github import GitHubIntegration
from app.integrations.slack import SlackIntegration
from app.integrations.hubspot import HubSpotIntegration
from app.integrations.notion import NotionIntegration
from app.integrations.mcp import MCPIntegration

# Payments
from app.integrations.payments import (
    PayPalIntegration,
    GumroadIntegration,
    LemonSqueezyIntegration,
    PaddleIntegration,
)

# Analytics
from app.integrations.analytics import (
    GoogleAnalyticsIntegration,
    MixpanelIntegration,
    AmplitudeIntegration,
    PostHogIntegration,
    PlausibleIntegration,
)

# Development
from app.integrations.development import (
    GitLabIntegration,
    LinearIntegration,
    JiraIntegration,
    VercelIntegration,
)

# Communication
from app.integrations.communication import (
    DiscordIntegration,
    TelegramIntegration,
    MicrosoftTeamsIntegration,
)

# CRM
from app.integrations.crm import (
    PipedriveIntegration,
    SalesforceIntegration,
    CloseIntegration,
)

# Marketing
from app.integrations.marketing import (
    LinkedInIntegration,
    TwitterIntegration,
    InstagramIntegration,
    TikTokIntegration,
    MailchimpIntegration,
    ConvertKitIntegration,
    BeehiivIntegration,
)

# E-commerce
from app.integrations.ecommerce import (
    ShopifyIntegration,
    WooCommerceIntegration,
)

# Scheduling
from app.integrations.scheduling import (
    CalendlyIntegration,
    CalComIntegration,
    GoogleCalendarIntegration,
)

# Support
from app.integrations.support import (
    IntercomIntegration,
    ZendeskIntegration,
    CrispIntegration,
)

# Productivity
from app.integrations.productivity import (
    AirtableIntegration,
    GoogleDriveIntegration,
    CodaIntegration,
)

# Video
from app.integrations.video import (
    ZoomIntegration,
    LoomIntegration,
)

# Design
from app.integrations.design import (
    FigmaIntegration,
    CanvaIntegration,
)

# Accounting
from app.integrations.accounting import (
    QuickBooksIntegration,
    XeroIntegration,
)

# Integration registry - maps provider string to class
INTEGRATION_REGISTRY = {
    # Core
    "stripe": StripeIntegration,
    "github": GitHubIntegration,
    "slack": SlackIntegration,
    "hubspot": HubSpotIntegration,
    "notion": NotionIntegration,
    "mcp": MCPIntegration,
    # Payments
    "paypal": PayPalIntegration,
    "gumroad": GumroadIntegration,
    "lemonsqueezy": LemonSqueezyIntegration,
    "paddle": PaddleIntegration,
    # Analytics
    "google_analytics": GoogleAnalyticsIntegration,
    "mixpanel": MixpanelIntegration,
    "amplitude": AmplitudeIntegration,
    "posthog": PostHogIntegration,
    "plausible": PlausibleIntegration,
    # Development
    "gitlab": GitLabIntegration,
    "linear": LinearIntegration,
    "jira": JiraIntegration,
    "vercel": VercelIntegration,
    # Communication
    "discord": DiscordIntegration,
    "telegram": TelegramIntegration,
    "microsoft_teams": MicrosoftTeamsIntegration,
    # CRM
    "pipedrive": PipedriveIntegration,
    "salesforce": SalesforceIntegration,
    "close": CloseIntegration,
    # Marketing
    "linkedin": LinkedInIntegration,
    "twitter": TwitterIntegration,
    "instagram": InstagramIntegration,
    "tiktok": TikTokIntegration,
    "mailchimp": MailchimpIntegration,
    "convertkit": ConvertKitIntegration,
    "beehiiv": BeehiivIntegration,
    # E-commerce
    "shopify": ShopifyIntegration,
    "woocommerce": WooCommerceIntegration,
    # Scheduling
    "calendly": CalendlyIntegration,
    "calcom": CalComIntegration,
    "google_calendar": GoogleCalendarIntegration,
    # Support
    "intercom": IntercomIntegration,
    "zendesk": ZendeskIntegration,
    "crisp": CrispIntegration,
    # Productivity
    "airtable": AirtableIntegration,
    "google_drive": GoogleDriveIntegration,
    "coda": CodaIntegration,
    # Video
    "zoom": ZoomIntegration,
    "loom": LoomIntegration,
    # Design
    "figma": FigmaIntegration,
    "canva": CanvaIntegration,
    # Accounting
    "quickbooks": QuickBooksIntegration,
    "xero": XeroIntegration,
}


def get_integration_class(provider: any):
    """Get integration class by provider name or enum"""
    if hasattr(provider, "value"):
        provider = provider.value
    return INTEGRATION_REGISTRY.get(str(provider))


def list_available_integrations():
    """List all available integrations with metadata"""
    integrations = []
    for provider, cls in INTEGRATION_REGISTRY.items():
        integrations.append({
            "provider": provider,
            "name": cls.display_name,
            "description": cls.description,
            "oauth_required": cls.oauth_required,
        })
    return integrations


__all__ = [
    # Base
    "BaseIntegration",
    "IntegrationCredentials",
    "SyncResult",
    # Registry
    "INTEGRATION_REGISTRY",
    "get_integration_class",
    "list_available_integrations",
    # Core
    "StripeIntegration",
    "GitHubIntegration",
    "SlackIntegration",
    "HubSpotIntegration",
    "NotionIntegration",
    # All 42 integrations...
]
