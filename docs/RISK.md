# Risk Management

## Overview

Wojak Capital implements comprehensive risk management across multiple layers:

1. **Position Level**: Size limits, stop losses
2. **Strategy Level**: Confidence thresholds
3. **Portfolio Level**: Exposure limits, correlation checks
4. **System Level**: Emergency stops, circuit breakers

## Position Limits

### Maximum Position Size
- **Crypto**: 2% of portfolio per trade
- **Forex**: 2% of portfolio per trade
- **Futures**: 2% of portfolio per trade

### Leverage Limits
- **Crypto**: Max 5x
- **Forex**: Max 20x
- **Futures**: Max 10x

## Daily Limits

### Loss Limits
- **Daily Stop**: -5% of portfolio
- **Weekly Stop**: -10% of portfolio
- **Monthly Stop**: -20% of portfolio

### Trade Limits
- **Max Daily Trades**: 50
- **Max Open Positions**: 10
- **Max Correlated Positions**: 3

## Risk Checks

### Pre-Trade
1. Position size within limits
2. Portfolio exposure acceptable
3. No high correlation with existing positions
4. Strategy confidence above threshold

### Post-Trade
1. Monitor unrealized PnL
2. Track drawdown
3. Update risk metrics

## Emergency Procedures

### Emergency Stop
Triggered when:
- Daily loss limit reached
- Critical system error
- Manual override

Actions:
1. Stop all new trades
2. Close all positions
3. Notify operators
4. Enter maintenance mode

### Circuit Breakers
- **Volatility Spike**: Pause trading for 15 minutes
- **Connection Loss**: Retry with exponential backoff
- **API Error**: Switch to backup exchange

## Risk Metrics

### Value at Risk (VaR)
Calculated using historical simulation:
- 95% confidence level
- 1-day horizon
- Updated hourly

### Sharpe Ratio
Target: > 1.5

### Maximum Drawdown
Limit: 15%

### Win Rate
Target: > 55%

## Monitoring

Real-time monitoring of:
- Open positions
- Unrealized PnL
- Margin usage
- Exposure by market
- Correlation matrix

Alerts sent to Discord when:
- Position > 90% of limit
- Daily loss > 80% of limit
- Margin < 20%
- Any critical error
