"""
Utility Helper Functions
Common utilities used across the application
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import hashlib
import secrets
import string

def generate_transaction_id(prefix: str = "VTX") -> str:
    """Generate unique transaction ID"""
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    random_part = secrets.token_hex(4).upper()
    return f"{prefix}{timestamp}{random_part}"

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)

def hash_string(text: str) -> str:
    """Generate SHA256 hash of string"""
    return hashlib.sha256(text.encode()).hexdigest()

def format_currency(amount: float, currency: str = "INR", symbol: str = "₹") -> str:
    """Format amount as currency"""
    return f"{symbol}{amount:,.2f}"

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return (part / total) * 100

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def parse_phone_number(phone: str) -> str:
    """Normalize phone number format"""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Add +91 if not present
    if not digits.startswith('91') and len(digits) == 10:
        digits = '91' + digits
    
    return '+' + digits

def get_date_range(days: int) -> tuple[datetime, datetime]:
    """Get date range from now to N days ago"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks"""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers"""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result

def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks}w ago"

def validate_json_structure(data: Dict, required_keys: List[str]) -> bool:
    """Validate if dictionary has required keys"""
    return all(key in data for key in required_keys)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in filename if c in valid_chars)

def paginate(items: List[Any], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """Paginate list of items"""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': end < total
    }
