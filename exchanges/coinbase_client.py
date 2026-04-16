"""
Coinbase Exchange Client
Crypto spot trading via Coinbase API
"""

import logging
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class CoinbaseClient:
    """
    Coinbase API Client
    
    For spot trading (not futures)
    """
    
    def __init__(self, api_key: str, secret: str, passphrase: str, sandbox: bool = True):
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.sandbox = sandbox
        
        if sandbox:
            self.base_url = "https://api-public.sandbox.pro.coinbase.com"
        else:
            self.base_url = "https://api.pro.coinbase.com"
        
        self.connected = False
        
    def connect(self):
        """Test connection"""
        try:
            response = requests.get(f"{self.base_url}/products")
            response.raise_for_status()
            self.connected = True
            logger.info("Connected to Coinbase" + (" SANDBOX" if self.sandbox else ""))
        except Exception as e:
            logger.error(f"Failed to connect to Coinbase: {e}")
            raise
    
    def get_products(self) -> List[Dict]:
        """Get available trading pairs"""
        try:
            response = requests.get(f"{self.base_url}/products")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    def get_candles(self, product_id: str, granularity: int = 3600) -> List[List]:
        """Get OHLCV candles
        
        Granularity in seconds: 60, 300, 900, 3600, 21600, 86400
        """
        try:
            params = {
                'granularity': granularity
            }
            
            response = requests.get(
                f"{self.base_url}/products/{product_id}/candles",
                params=params
            )
            response.raise_for_status()
            
            candles = response.json()
            
            # Format: [time, low, high, open, close, volume]
            formatted = []
            for c in candles:
                formatted.append([
                    c[0],      # timestamp
                    c[3],      # open
                    c[2],      # high
                    c[1],      # low
                    c[4],      # close
                    c[5]       # volume
                ])
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error fetching candles: {e}")
            return []
    
    def get_ticker(self, product_id: str) -> Optional[Dict]:
        """Get ticker"""
        try:
            response = requests.get(f"{self.base_url}/products/{product_id}/ticker")
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'symbol': product_id,
                'price': float(data.get('price', 0)),
                'bid': float(data.get('bid', 0)),
                'ask': float(data.get('ask', 0)),
                'volume': float(data.get('volume', 0)),
                'time': data.get('time')
            }
            
        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")
            return None
    
    def get_orderbook(self, product_id: str, level: int = 2) -> Dict:
        """Get order book"""
        try:
            response = requests.get(
                f"{self.base_url}/products/{product_id}/book",
                params={'level': level}
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'bids': data.get('bids', []),
                'asks': data.get('asks', []),
                'sequence': data.get('sequence')
            }
            
        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
            return {'bids': [], 'asks': []}
    
    def get_accounts(self) -> List[Dict]:
        """Get account balances"""
        # Would require authentication
        logger.warning("Coinbase get_accounts requires authentication implementation")
        return []
