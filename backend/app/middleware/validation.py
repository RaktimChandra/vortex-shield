"""
Input Validation Middleware
Provides additional security validation beyond Pydantic
"""
import re
from typing import Optional
from fastapi import HTTPException, status

class InputValidator:
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Indian phone number"""
        # Accepts +91XXXXXXXXXX or 10 digits
        pattern = r'^(\+91)?[6-9]\d{9}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username (alphanumeric, underscore, 3-20 chars)"""
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        Returns (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        return True, "Password is strong"
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 500) -> str:
        """Sanitize string input - remove dangerous characters"""
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """Validate GPS coordinates"""
        # India bounds approximately
        if not (-90 <= latitude <= 90):
            return False
        if not (-180 <= longitude <= 180):
            return False
        
        # India specific bounds (rough)
        if not (6.0 <= latitude <= 37.0):
            return False
        if not (68.0 <= longitude <= 97.0):
            return False
        
        return True
    
    @staticmethod
    def validate_amount(amount: float, min_val: float = 0, max_val: float = 100000) -> bool:
        """Validate monetary amount"""
        return min_val <= amount <= max_val
    
    @staticmethod
    def validate_positive_number(value: float) -> bool:
        """Validate positive number"""
        return value > 0
    
    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """Basic SQL injection pattern detection"""
        # Common SQL injection patterns
        sql_patterns = [
            r"(\bOR\b|\bAND\b).+?=.+?",
            r";\s*(DROP|DELETE|UPDATE|INSERT)",
            r"--",
            r"/\*.*?\*/",
            r"xp_cmdshell",
            r"exec\s*\(",
        ]
        
        text_upper = text.upper()
        for pattern in sql_patterns:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def check_xss(text: str) -> bool:
        """Basic XSS pattern detection"""
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onerror=",
            r"onload=",
            r"<iframe",
        ]
        
        text_lower = text.lower()
        for pattern in xss_patterns:
            if pattern in text_lower:
                return True
        return False

validator = InputValidator()

def validate_request_data(data: dict):
    """
    Validate request data for common security issues
    Raises HTTPException if validation fails
    """
    for key, value in data.items():
        if isinstance(value, str):
            # Check for SQL injection
            if validator.check_sql_injection(value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
            # Check for XSS
            if validator.check_xss(value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
