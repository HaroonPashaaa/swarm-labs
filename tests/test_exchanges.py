"""
Tests for Exchange Clients
"""

import pytest
from unittest.mock import Mock, patch

from exchanges.binance_client import BinanceClient
from exchanges.bybit_client import BybitClient

@pytest.fixture
def binance_client():
    return BinanceClient('test_key', 'test_secret', testnet=True)

@pytest.fixture
def bybit_client():
    return BybitClient('test_key', 'test_secret', testnet=True)

def test_binance_initialization(binance_client):
    """Test Binance client initialization"""
    assert binance_client.api_key == 'test_key'
    assert binance_client.testnet == True
    assert binance_client.connected == False

def test_bybit_initialization(bybit_client):
    """Test Bybit client initialization"""
    assert bybit_client.api_key == 'test_key'
    assert bybit_client.testnet == True

def test_binance_symbol_format(binance_client):
    """Test symbol formatting"""
    # Test getting available symbols
    binance_client.exchange = Mock()
    binance_client.exchange.markets = {
        'BTC/USDT:USDT': {'type': 'swap'},
        'ETH/USDT:USDT': {'type': 'swap'}
    }
    
    symbols = binance_client.get_symbols()
    assert len(symbols) == 2
    assert 'BTC/USDT:USDT' in symbols
