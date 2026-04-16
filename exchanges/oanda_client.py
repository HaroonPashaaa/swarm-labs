"""
OANDA Forex Client
Forex trading via OANDA API
"""

import logging
from typing import Dict, List, Optional, Any
import requests

logger = logging.getLogger(__name__)

class OandaClient:
    """
    OANDA Forex API Client
    
    Handles forex spot and CFD trading
    """
    
    def __init__(self, api_key: str, account_id: str, practice: bool = True):
        self.api_key = api_key
        self.account_id = account_id
        self.practice = practice
        
        # Base URL
        if practice:
            self.base_url = "https://api-fxpractice.oanda.com/v3"
        else:
            self.base_url = "https://api-fxtrade.oanda.com/v3"
        
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
    def fetch_candles(self, instrument: str, granularity: str = 'H1', count: int = 100) -> List[Dict]:
        """Fetch candlestick data"""
        try:
            url = f"{self.base_url}/instruments/{instrument}/candles"
            params = {
                'granularity': granularity,
                'count': count,
                'price': 'M'  # Midpoint
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            candles = data.get('candles', [])
            
            # Format candles
            formatted = []
            for c in candles:
                formatted.append({
                    'time': c['time'],
                    'open': float(c['mid']['o']),
                    'high': float(c['mid']['h']),
                    'low': float(c['mid']['l']),
                    'close': float(c['mid']['c']),
                    'volume': int(c['volume'])
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error fetching candles for {instrument}: {e}")
            return []
    
    def fetch_price(self, instrument: str) -> Optional[Dict]:
        """Fetch current price"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/pricing"
            params = {'instruments': instrument}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            price = data.get('prices', [{}])[0]
            
            return {
                'instrument': instrument,
                'bid': float(price.get('bid', 0)),
                'ask': float(price.get('ask', 0)),
                'spread': float(price.get('ask', 0)) - float(price.get('bid', 0)),
                'time': price.get('time')
            }
            
        except Exception as e:
            logger.error(f"Error fetching price for {instrument}: {e}")
            return None
    
    def fetch_orderbook(self, instrument: str) -> Dict:
        """Fetch order book (limited on OANDA)"""
        try:
            url = f"{self.base_url}/instruments/{instrument}/orderBook"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
            return {}
    
    def fetch_positions(self) -> Dict:
        """Fetch open positions"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/openPositions"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            positions = {}
            
            for pos in data.get('positions', []):
                instrument = pos['instrument']
                long_units = float(pos.get('long', {}).get('units', 0))
                short_units = float(pos.get('short', {}).get('units', 0))
                
                net_units = long_units + short_units
                
                if net_units != 0:
                    positions[instrument] = {
                        'units': net_units,
                        'side': 'long' if net_units > 0 else 'short',
                        'avg_price': pos.get('long', {}).get('averagePrice') if net_units > 0 
                                     else pos.get('short', {}).get('averagePrice')
                    }
            
            return positions
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return {}
    
    def fetch_economic_calendar(self) -> List[Dict]:
        """Fetch economic calendar events"""
        try:
            # Note: OANDA doesn't provide economic calendar directly
            # This is a placeholder for integration with external service
            return []
            
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
            return []
    
    def create_order(self, instrument: str, side: str, units: float) -> Optional[Dict]:
        """Create market order"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/orders"
            
            # OANDA uses negative units for short
            if side == 'sell':
                units = -abs(units)
            else:
                units = abs(units)
            
            order_data = {
                'order': {
                    'type': 'MARKET',
                    'instrument': instrument,
                    'units': str(units)
                }
            }
            
            response = requests.post(url, headers=self.headers, json=order_data)
            response.raise_for_status()
            
            logger.info(f"OANDA order created: {side} {abs(units)} {instrument}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    def close_position(self, instrument: str) -> bool:
        """Close position for instrument"""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/positions/{instrument}/close"
            
            # Close both long and short
            data = {'longUnits': 'ALL', 'shortUnits': 'ALL'}
            
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Position closed for {instrument}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False
