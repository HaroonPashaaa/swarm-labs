"""
Tests for Strategy Evaluator
"""

import pytest
from strategies.strategy_evaluator import StrategyEvaluator
from strategies.momentum import MomentumStrategy

@pytest.fixture
def evaluator():
    return StrategyEvaluator()

def test_evaluator_initialization(evaluator):
    """Test evaluator initialization"""
    assert len(evaluator.strategies) == 8
    assert 'momentum' in evaluator.strategies
    assert 'mean_reversion' in evaluator.strategies

def test_strategy_weights(evaluator):
    """Test strategy weights"""
    assert evaluator.strategy_weights['arbitrage'] == 1.2
    assert evaluator.strategy_weights['grid_trading'] == 0.7

def test_update_performance(evaluator):
    """Test performance tracking"""
    evaluator.update_performance('momentum', 100)
    
    stats = evaluator.get_strategy_stats()
    assert stats['momentum']['wins'] == 1
    assert stats['momentum']['losses'] == 0
    
    evaluator.update_performance('momentum', -50)
    stats = evaluator.get_strategy_stats()
    assert stats['momentum']['losses'] == 1

def test_calculate_consensus_buy(evaluator):
    """Test consensus calculation for buy signals"""
    from strategies.strategy_evaluator import StrategyResult
    
    results = [
        StrategyResult('momentum', 'buy', 0.8, 'test', {}),
        StrategyResult('scalping', 'buy', 0.7, 'test', {}),
        StrategyResult('mean_reversion', 'hold', 0.5, 'test', {})
    ]
    
    consensus = evaluator._calculate_consensus(results, {})
    
    assert consensus['action'] == 'buy'
    assert consensus['consensus'] > 0.5

def test_calculate_consensus_sell(evaluator):
    """Test consensus calculation for sell signals"""
    from strategies.strategy_evaluator import StrategyResult
    
    results = [
        StrategyResult('momentum', 'sell', 0.9, 'test', {}),
        StrategyResult('mean_reversion', 'sell', 0.8, 'test', {})
    ]
    
    consensus = evaluator._calculate_consensus(results, {})
    
    assert consensus['action'] == 'sell'
    assert consensus['confidence'] > 0.8
