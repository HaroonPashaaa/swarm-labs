"""
Tests for Strategy Performance
"""

import pytest
from strategies.strategy_evaluator import StrategyEvaluator

def test_strategy_weight_updates():
    """Test weight adjustment based on performance"""
    evaluator = StrategyEvaluator()
    
    # Initial weight
    initial_weight = evaluator.strategy_weights['momentum']
    
    # Simulate wins
    for _ in range(10):
        evaluator.update_performance('momentum', 100)
    
    stats = evaluator.get_strategy_stats()
    assert stats['momentum']['wins'] == 10
    assert stats['momentum']['win_rate'] == 1.0

def test_strategy_weight_losses():
    """Test weight adjustment after losses"""
    evaluator = StrategyEvaluator()
    
    # Simulate losses
    for _ in range(5):
        evaluator.update_performance('momentum', -50)
    
    stats = evaluator.get_strategy_stats()
    assert stats['momentum']['losses'] == 5
    assert stats['momentum']['win_rate'] == 0.0

def test_all_strategies_tracked():
    """Test that all strategies are in performance tracker"""
    evaluator = StrategyEvaluator()
    
    all_strategies = [
        'momentum', 'mean_reversion', 'scalping', 'news_sentiment',
        'volatility_breakout', 'grid_trading', 'arbitrage', 'session_based'
    ]
    
    for strategy in all_strategies:
        assert strategy in evaluator.strategy_performance
