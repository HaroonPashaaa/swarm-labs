"""
Validation utilities
Input validation and sanitization
"""

import re
from typing import Optional

class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate trading symbol format"""
        if not symbol or len(symbol) > 20:
            return False
        
        # Allow alphanumeric and common separators
        pattern = r'^[A-Z0-9]+[/_-][A-Z0-9]+$'
        return bool(re.match(pattern, symbol.upper()))
    
    @staticmethod
    def validate_api_key(key: str) -> bool:
        """Validate API key format"""
        if not key:
            return False
        
        # Minimum length check
        return len(key) >= 16
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate price is positive and reasonable"""
        return price > 0 and price < 100000000
    
    @staticmethod
    def validate_quantity(qty: float) -> bool:
        """Validate quantity is positive"""
        return qty > 0
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input"""
        if not value:
            return ""
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1F\x7F]', '', value)
        
        # Strip whitespace
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
