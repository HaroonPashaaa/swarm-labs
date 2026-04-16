"""
Example: Strategy Backtest

This example shows how to backtest a strategy on historical data.
"""

from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy

# Mock historical data
def create_mock_data():
    """Create mock OHLCV data"""
    import random
    
    base_price = 50000
    data = []
    
    for i in range(100):
        change = random.uniform(-0.02, 0.02)
        close = base_price * (1 + change)
        high = close * (1 + random.uniform(0, 0.01))
        low = close * (1 - random.uniform(0, 0.01))
        open_price = base_price
        volume = random.randint(1000, 10000)
        
        data.append([i, open_price, high, low, close, volume])
        base_price = close
    
    return data

def backtest_strategy(strategy_class, data):
    """Backtest a strategy"""
    strategy = strategy_class()
    
    signals = []
    
    # Walk forward analysis
    for i in range(50, len(data)):
        window = data[:i]
        
        result = strategy.evaluate(
            market='crypto',
            symbol='BTC/USDT',
            data={'ohlcv': window},
            position=None
        )
        
        if result and result['action'] != 'hold':
            signals.append({
                'index': i,
                'action': result['action'],
                'confidence': result['confidence'],
                'price': data[i][4]
            })
    
    return signals

def main():
    """Run backtest"""
    print("📊 Running Strategy Backtest")
    print()
    
    # Create mock data
    data = create_mock_data()
    
    # Backtest momentum strategy
    print("Testing Momentum Strategy...")
    momentum_signals = backtest_strategy(MomentumStrategy, data)
    print(f"Signals generated: {len(momentum_signals)}")
    
    for sig in momentum_signals[:5]:
        print(f"  {sig['action'].upper()} at ${sig['price']:,.2f} "
              f"(confidence: {sig['confidence']:.0%})")
    
    print()
    
    # Backtest mean reversion
    print("Testing Mean Reversion Strategy...")
    mr_signals = backtest_strategy(MeanReversionStrategy, data)
    print(f"Signals generated: {len(mr_signals)}")
    
    for sig in mr_signals[:5]:
        print(f"  {sig['action'].upper()} at ${sig['price']:,.2f} "
              f"(confidence: {sig['confidence']:.0%})")

if __name__ == '__main__':
    main()
