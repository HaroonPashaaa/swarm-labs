"""
Kraken Exchange Client
Crypto futures and spot via Kraken API
"""

import logging
from typing import Dict, List, Optional, Any
import requests
import base64
import hashlib
import hmac
import time

logger = logging.getLogger(__name__)

class KrakenClient:
    """
    Kraken API Client
    
    Supports both spot and futures trading
    """
    
    def __init__(self, api_key: str, secret: str):
        self.api_key = api_key
        self.secret = secret
        self.base_url = "https://api.kraken.com"
        self.connected = False
        
    def connect(self):
        """Test connection"""
        try:
            response = requests.get(f"{self.base_url}/0/public/Time")
            response.raise_for_status()
            self.connected = True
            logger.info("Connected to Kraken")
        except Exception as e:
            logger.error(f"Failed to connect to Kraken: {e}")
            raise
    
    def _generate_signature(self, urlpath: str, data: Dict) -> str:
        """Generate API signature"""
        postdata = requests.compat.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        signature = hmac.new(
            base64.b64decode(self.secret),
            message,
            hashlib.sha512
        )
        
        return base64.b64encode(signature.digest()).decode()
    
    def get_ohlc(self, pair: str, interval: int = 60) -> List[List]:
        """Get OHLC data
        
        Interval in minutes: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600
        """
        try:
            params = {
                'pair': pair,
                'interval': interval
            }
            
            response = requests.get(
                f"{self.base_url}/0/public/OHLC",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('error'):
                logger.error(f"Kraken API error: {data['error']}")
                return []
            
            # Extract result
            result_key = list(data['result'].keys())[0]
            ohlc_data = data['result'][result_key]
            
            # Format: [time, open, high, low, close, vwap, volume, count]
            formatted = []
            for c in ohlc_data:
                formatted.append([
                    c[0],           # timestamp
                    float(c[1]),    # open
                    float(c[2]),    # high
                    float(c[3]),    # low
                    float(c[4]),    # close
                    float(c[6])     # volume
                ])
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error fetching OHLC: {e}")
            return []
    
    def get_ticker(self, pair: str) -> Optional[Dict]:
        """Get ticker"""
        try:
            response = requests.get(
                f"{self.base_url}/0/public/Ticker",
                params={'pair': pair}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('error'):
                return None
            
            result_key = list(data['result'].keys())[0]
            ticker = data['result'][result_key]
            
            return {
                'symbol': pair,
                'bid': float(ticker['b'][0]),
                'ask': float(ticker['a'][0]),
                'last': float(ticker['c'][0]),
                'volume': float(ticker['v'][1]),
                'high': float(ticker['h'][1]),
                'low': float(ticker['l'][1])
            }
            
        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")
            return None
    
    def get_orderbook(self, pair: str, count: int = 100) -> Dict:
        """Get order book"""
        try:
            params = {
                'pair': pair,
                'count': count
            }
            
            response = requests.get(
                f"{self.base_url}/0/public/Depth",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('error'):
                return {'bids': [], 'asks': []}
            
            result_key = list(data['result'].keys())[0]
            book = data['result'][result_key]
            
            return {
                'bids': [[float(b[0]), float(b[1])] for b in book['bids']],
                'asks': [[float(a[0]), float(a[1])] for a in book['asks']]
            }
            
        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
            return {'bids': [], 'asks': []}
    
    def get_assets(self) -> List[str]:
        """Get available assets"""
        try:
            response = requests.get(f"{self.base_url}/0/public/Assets")
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('error'):
                return []
            
            return list(data['result'].keys())
            
        except Exception as e:
            logger.error(f"Error fetching assets: {e}")
            return []
