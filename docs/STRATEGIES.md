# Strategy Guide

## Available Strategies

### 1. Momentum / Trend Following
**Best For**: Strong directional markets

**Logic**:
- Enter when price breaks above/below moving averages
- Use ATR for position sizing and stops
- Ride the trend until reversal signals

**Parameters**:
- Fast MA: 9 periods
- Slow MA: 21 periods
- ATR Period: 14

**Markets**: All

---

### 2. Mean Reversion
**Best For**: Range-bound markets

**Logic**:
- Fade overextended moves
- Buy near support, sell near resistance
- Use Bollinger Bands and RSI

**Parameters**:
- BB Period: 20
- BB StdDev: 2.0
- RSI Threshold: 30/70

**Markets**: All

---

### 3. Scalping
**Best For**: High liquidity periods

**Logic**:
- Trade order book imbalances
- Hold for seconds to minutes
- Tight stops, quick profits

**Parameters**:
- Profit Target: 0.2%
- Stop Loss: 0.1%
- Max Hold: 60 seconds

**Markets**: Crypto, Forex (overlap sessions)

---

### 4. News / Sentiment
**Best For**: Event-driven moves

**Logic**:
- Trade economic releases
- Monitor news sentiment
- React to unexpected events

**Events**:
- FOMC
- NFP
- CPI
- GDP
- Earnings

**Markets**: Forex, Futures

---

### 5. Volatility Breakout
**Best For**: Low volatility expanding

**Logic**:
- Wait for Bollinger Band squeeze
- Enter on breakout
- Volume confirmation required

**Parameters**:
- Squeeze Threshold: 60% of average
- Min Profit: 0.1%

**Markets**: All

---

### 6. Grid Trading
**Best For**: Sideways markets

**Logic**:
- Place buy orders at regular intervals below price
- Place sell orders above price
- Profit from oscillations

**Parameters**:
- Grid Levels: 10
- Grid Spacing: 0.5%

**Markets**: Crypto, Forex

---

### 7. Arbitrage
**Best For**: Price discrepancies

**Logic**:
- Monitor prices across exchanges
- Buy low, sell high simultaneously
- Account for fees and slippage

**Min Spread**: 0.1%

**Markets**: Crypto (Binance/Bybit)

---

### 8. Session-Based
**Best For**: Time-specific patterns

**Logic**:
- Asian Session: Range trading
- London Open: Breakouts
- NY Session: Trend following
- Overlap: High confidence trades

**Markets**: Forex, Futures

## Strategy Selection

The Strategy Evaluator automatically selects the best strategy based on:
- Market conditions
- Volatility
- Time of day
- Recent performance

Weights are adjusted based on historical performance.

## Adding New Strategies

1. Create file in `strategies/`
2. Inherit from base strategy class
3. Implement `evaluate()` method
4. Add to Strategy Evaluator
5. Set initial weight

Example:

```python
class MyStrategy:
    def evaluate(self, market, symbol, data, position, context):
        # Your logic here
        return {
            'strategy_name': 'my_strategy',
            'action': 'buy',
            'confidence': 0.8,
            'reasoning': 'Signal description'
        }
```
