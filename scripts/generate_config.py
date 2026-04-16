#!/usr/bin/env python3
"""
Generate configuration template
"""

import json
from pathlib import Path

def generate_strategy_config():
    """Generate strategy configuration"""
    config = {
        'strategies': {
            'momentum': {
                'enabled': True,
                'weight': 1.0,
                'params': {
                    'fast_period': 9,
                    'slow_period': 21,
                    'atr_period': 14
                }
            },
            'mean_reversion': {
                'enabled': True,
                'weight': 1.0,
                'params': {
                    'bb_period': 20,
                    'bb_std': 2.0,
                    'rsi_period': 14
                }
            },
            'scalping': {
                'enabled': False,
                'weight': 0.8,
                'params': {
                    'profit_target': 0.002,
                    'stop_loss': 0.001
                }
            }
        }
    }
    
    return config

def generate_exchange_config():
    """Generate exchange configuration"""
    config = {
        'exchanges': {
            'binance': {
                'enabled': True,
                'testnet': True,
                'symbols': ['BTC/USDT', 'ETH/USDT']
            },
            'bybit': {
                'enabled': True,
                'testnet': True,
                'symbols': ['BTC/USDT', 'ETH/USDT']
            },
            'oanda': {
                'enabled': False,
                'practice': True,
                'symbols': ['EUR_USD', 'GBP_USD']
            }
        }
    }
    
    return config

def main():
    """Generate all configs"""
    print("⚙️  Generating configuration templates...")
    
    Path('config').mkdir(exist_ok=True)
    
    # Strategy config
    with open('config/strategies.json', 'w') as f:
        json.dump(generate_strategy_config(), f, indent=2)
    print("✅ config/strategies.json")
    
    # Exchange config
    with open('config/exchanges.json', 'w') as f:
        json.dump(generate_exchange_config(), f, indent=2)
    print("✅ config/exchanges.json")
    
    print("\n✅ Configuration templates generated")

if __name__ == '__main__':
    main()
