"""
Tests for Validation utilities
"""

import pytest
from core.validation import Validator

def test_validate_symbol_crypto():
    """Test crypto symbol validation"""
    assert Validator.validate_symbol('BTC/USDT') == True
    assert Validator.validate_symbol('ETH/USDT') == True
    assert Validator.validate_symbol('INVALID') == False

def test_validate_symbol_forex():
    """Test forex symbol validation"""
    assert Validator.validate_symbol('EUR_USD') == True
    assert Validator.validate_symbol('GBP_USD') == True

def test_validate_api_key():
    """Test API key validation"""
    assert Validator.validate_api_key('a' * 32) == True
    assert Validator.validate_api_key('short') == False
    assert Validator.validate_api_key('') == False

def test_validate_price():
    """Test price validation"""
    assert Validator.validate_price(50000) == True
    assert Validator.validate_price(0) == False
    assert Validator.validate_price(-100) == False
    assert Validator.validate_price(999999999) == False

def test_validate_quantity():
    """Test quantity validation"""
    assert Validator.validate_quantity(1.5) == True
    assert Validator.validate_quantity(0) == False
    assert Validator.validate_quantity(-1) == False

def test_sanitize_string():
    """Test string sanitization"""
    assert Validator.sanitize_string('  test  ') == 'test'
    assert Validator.sanitize_string('') == ''
    assert Validator.sanitize_string('test\x00') == 'test'
