"""
Platform Action Mappings
Defines submission flows, selectors, and fields for each launch platform
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FormField:
    """Single form field definition"""
    name: str  # Field identifier (maps to product data)
    selector: str  # CSS selector
    field_type: str  # text, textarea, select, file, checkbox
    required: bool = True
    max_length: Optional[int] = None
    placeholder: Optional[str] = None


@dataclass
class PlatformAction:
    """Complete action mapping for a platform"""
    platform_id: str
    name: str
    submit_url: str
    requires_login: bool
    login_url: Optional[str]
    fields: List[FormField]
    submit_button: str  # CSS selector for submit
    success_indicators: List[str]  # CSS selectors indicating success
    error_indicators: List[str]  # CSS selectors indicating failure
    pre_submit_wait: int = 1000  # ms to wait before submit
    post_submit_wait: int = 3000  # ms to wait after submit
    notes: str = ""


# ==================
# PLATFORM DEFINITIONS
# ==================

PLATFORM_ACTIONS: Dict[str, PlatformAction] = {
    
    # === EASY PLATFORMS (No Login Required) ===
    
    "startupbase": PlatformAction(
        platform_id="startupbase",
        name="StartupBase",
        submit_url="https://startupbase.io/submit",
        requires_login=False,
        login_url=None,
        fields=[
            FormField("name", "input[name='name'], input[placeholder*='name' i]", "text", max_length=100),
            FormField("tagline", "input[name='tagline'], input[placeholder*='tagline' i]", "text", max_length=140),
            FormField("url", "input[name='url'], input[type='url'], input[placeholder*='url' i]", "text"),
            FormField("description", "textarea[name='description'], textarea[placeholder*='description' i]", "textarea", max_length=500),
            FormField("email", "input[name='email'], input[type='email']", "text"),
        ],
        submit_button="button[type='submit'], input[type='submit'], button:has-text('Submit')",
        success_indicators=[".success", ".thank-you", "[class*='success']", "text=Thank you"],
        error_indicators=[".error", "[class*='error']", ".alert-danger"],
        notes="Simple form, no login needed",
    ),
    
    "launching_io": PlatformAction(
        platform_id="launching_io",
        name="Launching.io",
        submit_url="https://launching.io/submit",
        requires_login=False,
        login_url=None,
        fields=[
            FormField("name", "input[name='name']", "text", max_length=100),
            FormField("url", "input[name='url']", "text"),
            FormField("tagline", "input[name='tagline']", "text", max_length=100),
            FormField("description", "textarea[name='description']", "textarea", max_length=1000),
        ],
        submit_button="button[type='submit']",
        success_indicators=[".success", "text=submitted"],
        error_indicators=[".error"],
        notes="Quick submission",
    ),
    
    "alternativeto": PlatformAction(
        platform_id="alternativeto",
        name="AlternativeTo",
        submit_url="https://alternativeto.net/add-application/",
        requires_login=False,
        login_url=None,
        fields=[
            FormField("name", "input#Name, input[name='Name']", "text", max_length=100),
            FormField("url", "input#Url, input[name='Url']", "text"),
            FormField("description", "textarea#Description, textarea[name='Description']", "textarea", max_length=2000),
            FormField("category", "select#Category, select[name='Category']", "select"),
        ],
        submit_button="button[type='submit'], input[value='Add Application']",
        success_indicators=[".success", "text=added"],
        error_indicators=[".error", ".validation-error"],
        notes="List as alternative to competitors",
    ),
    
    "saashub": PlatformAction(
        platform_id="saashub",
        name="SaaSHub",
        submit_url="https://www.saashub.com/submit",
        requires_login=False,
        login_url=None,
        fields=[
            FormField("name", "input[name='name']", "text", max_length=100),
            FormField("url", "input[name='url']", "text"),
            FormField("tagline", "input[name='tagline']", "text", max_length=150),
            FormField("description", "textarea[name='description']", "textarea"),
        ],
        submit_button="button[type='submit']",
        success_indicators=[".success", "text=Thank"],
        error_indicators=[".error"],
        notes="SaaS alternatives directory",
    ),
    
    "theresanaiforthat": PlatformAction(
        platform_id="theresanaiforthat",
        name="There's An AI For That",
        submit_url="https://theresanaiforthat.com/submit/",
        requires_login=False,
        login_url=None,
        fields=[
            FormField("name", "input[name='tool_name'], input[placeholder*='name' i]", "text", max_length=100),
            FormField("url", "input[name='website'], input[name='url']", "text"),
            FormField("tagline", "input[name='short_description'], input[name='tagline']", "text", max_length=150),
            FormField("description", "textarea[name='description'], textarea[name='long_description']", "textarea"),
            FormField("email", "input[name='email'], input[type='email']", "text"),
        ],
        submit_button="button[type='submit'], input[type='submit']",
        success_indicators=[".success", "text=submitted", "text=review"],
        error_indicators=[".error"],
        notes="Top AI tools directory - high traffic",
    ),
    
    "futuretools": PlatformAction(
        platform_id="futuretools",
        name="FutureTools",
        submit_url="https://www.futuretools.io/submit-a-tool",
        requires_login=False,
        login_url=None,
        fields=[
            FormField("name", "input[name='Tool Name'], input[placeholder*='Tool Name' i]", "text"),
            FormField("url", "input[name='Website URL'], input[placeholder*='URL' i]", "text"),
            FormField("tagline", "input[name='Short Description']", "text", max_length=150),
            FormField("description", "textarea[name='Long Description']", "textarea"),
            FormField("email", "input[name='Email'], input[type='email']", "text"),
        ],
        submit_button="button[type='submit']",
        success_indicators=[".success", "text=Thank you"],
        error_indicators=[".error"],
        notes="Curated by Matt Wolfe",
    ),
    
    "toolify": PlatformAction(
        platform_id="toolify",
        name="Toolify.ai",
        submit_url="https://www.toolify.ai/submit",
        requires_login=False,
        login_url=None,
        fields=[
            FormField("name", "input[name='name']", "text"),
            FormField("url", "input[name='url'], input[name='website']", "text"),
            FormField("description", "textarea[name='description']", "textarea"),
            FormField("email", "input[name='email']", "text"),
        ],
        submit_button="button[type='submit']",
        success_indicators=[".success", "text=submitted"],
        error_indicators=[".error"],
        notes="Large AI tools database",
    ),
    
    # === MEDIUM PLATFORMS (Login Required) ===
    
    "betalist": PlatformAction(
        platform_id="betalist",
        name="BetaList",
        submit_url="https://betalist.com/submit",
        requires_login=True,
        login_url="https://betalist.com/users/sign_in",
        fields=[
            FormField("name", "input[name='startup[name]'], input#startup_name", "text", max_length=100),
            FormField("tagline", "input[name='startup[tagline]'], input#startup_tagline", "text", max_length=140),
            FormField("url", "input[name='startup[url]'], input#startup_url", "text"),
            FormField("description", "textarea[name='startup[description]'], textarea#startup_description", "textarea", max_length=500),
        ],
        submit_button="input[type='submit'], button[type='submit']",
        success_indicators=[".success", ".flash-success", "text=submitted"],
        error_indicators=[".error", ".flash-error", ".alert-error"],
        notes="Popular startup directory, premium option available",
    ),
    
    "indie_hackers": PlatformAction(
        platform_id="indie_hackers",
        name="Indie Hackers",
        submit_url="https://www.indiehackers.com/products/new",
        requires_login=True,
        login_url="https://www.indiehackers.com/sign-in",
        fields=[
            FormField("name", "input[name='name'], input[placeholder*='name' i]", "text", max_length=100),
            FormField("tagline", "input[name='tagline']", "text", max_length=150),
            FormField("url", "input[name='url'], input[name='website']", "text"),
            FormField("description", "textarea[name='description']", "textarea"),
        ],
        submit_button="button[type='submit'], button:has-text('Create')",
        success_indicators=[".success", "text=created"],
        error_indicators=[".error"],
        notes="Community of indie makers",
    ),
    
    # === HARD PLATFORMS (Complex Flow) ===
    
    "product_hunt": PlatformAction(
        platform_id="product_hunt",
        name="Product Hunt",
        submit_url="https://www.producthunt.com/posts/new",
        requires_login=True,
        login_url="https://www.producthunt.com/login",
        fields=[
            FormField("name", "input[name='name'], input[placeholder*='name' i]", "text", max_length=60),
            FormField("tagline", "input[name='tagline'], input[placeholder*='tagline' i]", "text", max_length=60),
            FormField("url", "input[name='url'], input[name='website']", "text"),
            FormField("description", "textarea[name='description']", "textarea", max_length=260),
        ],
        submit_button="button[type='submit'], button:has-text('Launch')",
        success_indicators=[".success", "text=scheduled", "text=launched"],
        error_indicators=[".error"],
        pre_submit_wait=2000,
        post_submit_wait=5000,
        notes="High-stakes launch - prepare carefully!",
    ),
    
    "hacker_news": PlatformAction(
        platform_id="hacker_news",
        name="Hacker News (Show HN)",
        submit_url="https://news.ycombinator.com/submit",
        requires_login=True,
        login_url="https://news.ycombinator.com/login",
        fields=[
            FormField("title", "input[name='title']", "text", max_length=80, placeholder="Show HN: {name} - {tagline}"),
            FormField("url", "input[name='url']", "text"),
        ],
        submit_button="input[type='submit']",
        success_indicators=["text=Saved", "a:has-text('newest')"],
        error_indicators=["text=error", "text=Error"],
        notes="Start title with 'Show HN:' for visibility",
    ),
}


# ==================
# HELPER FUNCTIONS
# ==================

def get_platform_action(platform_id: str) -> Optional[PlatformAction]:
    """Get action mapping for a platform"""
    return PLATFORM_ACTIONS.get(platform_id)


def get_all_platform_ids() -> List[str]:
    """Get list of all supported platform IDs"""
    return list(PLATFORM_ACTIONS.keys())


def get_easy_platforms() -> List[PlatformAction]:
    """Get platforms that don't require login"""
    return [p for p in PLATFORM_ACTIONS.values() if not p.requires_login]


def get_platforms_by_difficulty() -> Dict[str, List[PlatformAction]]:
    """Group platforms by difficulty"""
    return {
        "easy": [p for p in PLATFORM_ACTIONS.values() if not p.requires_login],
        "medium": [p for p in PLATFORM_ACTIONS.values() if p.requires_login and p.platform_id not in ("product_hunt", "hacker_news")],
        "hard": [p for p in PLATFORM_ACTIONS.values() if p.platform_id in ("product_hunt", "hacker_news")],
    }


def map_product_to_fields(product_info: Dict[str, Any], fields: List[FormField]) -> Dict[str, str]:
    """Map product info to form fields"""
    mapping = {}
    
    for field in fields:
        value = product_info.get(field.name, "")
        
        # Handle special mappings
        if not value:
            if field.name == "title" and "name" in product_info:
                # For HN, construct title
                name = product_info.get("name", "")
                tagline = product_info.get("tagline", "")
                value = f"Show HN: {name} - {tagline}"
            elif field.name == "email":
                value = product_info.get("contact_email", product_info.get("email", ""))
        
        # Apply max length
        if field.max_length and len(value) > field.max_length:
            value = value[:field.max_length - 3] + "..."
        
        mapping[field.selector] = value
    
    return mapping
