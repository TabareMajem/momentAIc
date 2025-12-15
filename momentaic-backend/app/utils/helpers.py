"""
MomentAIc Utilities
Helper functions and common utilities
"""

import re
import hashlib
import secrets
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import json


def generate_webhook_url() -> str:
    """Generate a unique webhook URL identifier"""
    return f"wh_{secrets.token_urlsafe(16)}"


def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"mk_{secrets.token_urlsafe(32)}"


def hash_string(value: str) -> str:
    """Create a hash of a string"""
    return hashlib.sha256(value.encode()).hexdigest()


def slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length"""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def parse_json_safely(text: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON, returning None on failure"""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from text that may contain other content"""
    # Try to find JSON object
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        return parse_json_safely(match.group())
    
    # Try to find JSON array
    match = re.search(r'\[[\s\S]*\]', text)
    if match:
        return parse_json_safely(match.group())
    
    return None


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format a number as currency"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "JPY":
        return f"¥{amount:,.0f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_number(num: float) -> str:
    """Format a number with K/M/B suffixes"""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(int(num))


def calculate_runway(burn_rate: float, cash: float) -> float:
    """Calculate runway in months"""
    if burn_rate <= 0:
        return float('inf')
    return cash / burn_rate


def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate percentage growth rate"""
    if previous == 0:
        return 0.0 if current == 0 else 100.0
    return ((current - previous) / previous) * 100


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))


def get_date_range(period: str) -> tuple[datetime, datetime]:
    """Get start and end dates for a period"""
    now = datetime.utcnow()
    
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == "yesterday":
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - timedelta(days=7)
        end = now
    elif period == "month":
        start = now - timedelta(days=30)
        end = now
    elif period == "quarter":
        start = now - timedelta(days=90)
        end = now
    elif period == "year":
        start = now - timedelta(days=365)
        end = now
    else:
        start = now - timedelta(days=30)
        end = now
    
    return start, end


def mask_email(email: str) -> str:
    """Mask email address for privacy"""
    if "@" not in email:
        return email
    
    local, domain = email.split("@")
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage"""
    # Remove path components
    filename = filename.split("/")[-1].split("\\")[-1]
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200 - len(ext) - 1] + '.' + ext if ext else name[:200]
    
    return filename


class Timer:
    """Context manager for timing code execution"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start = None
        self.end = None
        self.duration = None
    
    def __enter__(self):
        self.start = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = datetime.utcnow()
        self.duration = (self.end - self.start).total_seconds()
    
    @property
    def duration_ms(self) -> float:
        """Duration in milliseconds"""
        return self.duration * 1000 if self.duration else 0
