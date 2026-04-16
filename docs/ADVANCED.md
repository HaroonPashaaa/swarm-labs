# Advanced Configuration

## Custom Strategies

### Adding Your Own Strategy

1. Create file in `strategies/`
2. Implement `evaluate()` method
3. Register in `StrategyEvaluator`

```python
class MyStrategy:
    def evaluate(self, market, symbol, data, position, context):
        # Your logic here
        return {
            'strategy_name': 'my_strategy',
            'action': 'buy',
            'confidence': 0.8,
            'reasoning': 'My custom signal'
        }
```

## Custom Risk Rules

### Implementing Risk Checks

```python
class CustomRiskRule:
    def check(self, portfolio, trade):
        # Your risk logic
        if portfolio.exposure > 0.5:
            return False, 'Too much exposure'
        return True, 'OK'
```

## Custom Indicators

### Technical Indicators

```python
def calculate_custom_indicator(data):
    # Your indicator logic
    return indicator_value
```
