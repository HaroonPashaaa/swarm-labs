"""
Strategy Evaluator
Evaluates all 8 trading strategies and calculates consensus
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np

from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.scalping import ScalpingStrategy
from strategies.news_sentiment import NewsSentimentStrategy
from strategies.volatility_breakout import VolatilityBreakoutStrategy
from strategies.grid_trading import GridTradingStrategy
from strategies.arbitrage import ArbitrageStrategy
from strategies.session_based import SessionBasedStrategy

logger = logging.getLogger(__name__)

@dataclass
class StrategyResult:
    """Result from single strategy evaluation"""
    strategy_name: str
    action: str  # buy, sell, hold
    confidence: float
    reasoning: str
    indicators: Dict[str, Any]

class StrategyEvaluator:
    """
    Evaluates all trading strategies and calculates weighted consensus
    """
    
    def __init__(self):
        # Initialize all 8 strategies
        self.strategies = {
            'momentum': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'scalping': ScalpingStrategy(),
            'news_sentiment': NewsSentimentStrategy(),
            'volatility_breakout': VolatilityBreakoutStrategy(),
            'grid_trading': GridTradingStrategy(),
            'arbitrage': ArbitrageStrategy(),
            'session_based': SessionBasedStrategy()
        }
        
        # Strategy weights based on historical performance
        self.strategy_weights = {
            'momentum': 1.0,
            'mean_reversion': 1.0,
            'scalping': 0.8,
            'news_sentiment': 0.9,
            'volatility_breakout': 1.1,
            'grid_trading': 0.7,
            'arbitrage': 1.2,
            'session_based': 0.9
        }
        
        # Track strategy performance
        self.strategy_performance = {name: {'wins': 0, 'losses': 0} 
                                     for name in self.strategies.keys()}
    
    def evaluate_all(self, market: str, symbol: str, data: Dict, 
                     positions: Dict, context: Dict = None) -> Dict[str, Any]:
        """
        Evaluate all strategies and return consensus
        
        Returns:
            {
                'action': 'buy'/'sell'/'hold',
                'confidence': float,
                'consensus': float,
                'primary_strategy': str,
                'reasoning': str,
                'strategy_scores': Dict[str, float]
            }
        """
        results = []
        
        # Evaluate each strategy
        for name, strategy in self.strategies.items():
            try:
                result = strategy.evaluate(
                    market=market,
                    symbol=symbol,
                    data=data,
                    position=positions.get(symbol),
                    context=context
                )
                
                if result:
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Error evaluating {name} strategy: {e}")
                continue
        
        if not results:
            return {
                'action': 'hold',
                'confidence': 0.0,
                'consensus': 0.0,
                'primary_strategy': 'none',
                'reasoning': 'No strategy generated signals',
                'strategy_scores': {}
            }
        
        # Calculate weighted consensus
        return self._calculate_consensus(results, context)
    
    def _calculate_consensus(self, results: List[StrategyResult], 
                            context: Dict) -> Dict[str, Any]:
        """Calculate weighted consensus from strategy results"""
        
        # Weight by strategy performance
        weighted_votes = {'buy': 0.0, 'sell': 0.0, 'hold': 0.0}
        strategy_scores = {}
        
        for result in results:
            # Get base weight
            weight = self.strategy_weights.get(result.strategy_name, 1.0)
            
            # Adjust by recent performance
            perf = self.strategy_performance.get(result.strategy_name, {'wins': 1, 'losses': 1})
            win_rate = perf['wins'] / (perf['wins'] + perf['losses']) if (perf['wins'] + perf['losses']) > 0 else 0.5
            weight *= (0.5 + win_rate)  # Scale by win rate
            
            # Apply confidence
            weighted_score = weight * result.confidence
            
            weighted_votes[result.action] += weighted_score
            strategy_scores[result.strategy_name] = {
                'action': result.action,
                'confidence': result.confidence,
                'weighted_score': weighted_score,
                'reasoning': result.reasoning
            }
        
        # Determine winning action
        total_weight = sum(weighted_votes.values())
        if total_weight == 0:
            return {
                'action': 'hold',
                'confidence': 0.0,
                'consensus': 0.0,
                'primary_strategy': 'none',
                'reasoning': 'No weighted signals',
                'strategy_scores': strategy_scores
            }
        
        winning_action = max(weighted_votes.keys(), key=lambda k: weighted_votes[k])
        consensus_pct = weighted_votes[winning_action] / total_weight
        
        # Get primary strategy (highest weighted score for winning action)
        winning_strategies = [
            (name, scores['weighted_score']) 
            for name, scores in strategy_scores.items()
            if scores['action'] == winning_action
        ]
        
        primary_strategy = max(winning_strategies, key=lambda x: x[1])[0] if winning_strategies else 'none'
        
        # Calculate average confidence for winning action
        winning_results = [r for r in results if r.action == winning_action]
        avg_confidence = sum(r.confidence for r in winning_results) / len(winning_results) if winning_results else 0
        
        # Build reasoning
        reasoning = self._build_reasoning(results, winning_action, primary_strategy)
        
        return {
            'action': winning_action,
            'confidence': avg_confidence,
            'consensus': consensus_pct,
            'primary_strategy': primary_strategy,
            'reasoning': reasoning,
            'strategy_scores': strategy_scores
        }
    
    def _build_reasoning(self, results: List[StrategyResult], 
                        winning_action: str, primary_strategy: str) -> str:
        """Build human-readable reasoning"""
        primary = next((r for r in results if r.strategy_name == primary_strategy), None)
        
        if not primary:
            return f"Consensus for {winning_action}"
        
        reasoning = f"{primary_strategy.replace('_', ' ').title()}: {primary.reasoning}"
        
        # Add supporting strategies
        supporting = [r.strategy_name for r in results 
                     if r.action == winning_action and r.strategy_name != primary_strategy]
        if supporting:
            reasoning += f". Supported by: {', '.join(s.replace('_', ' ') for s in supporting[:3])}"
        
        return reasoning
    
    def update_performance(self, strategy_name: str, pnl: float):
        """Update strategy performance tracking"""
        if strategy_name not in self.strategy_performance:
            return
        
        if pnl > 0:
            self.strategy_performance[strategy_name]['wins'] += 1
        else:
            self.strategy_performance[strategy_name]['losses'] += 1
    
    def get_strategy_stats(self) -> Dict[str, Dict]:
        """Get performance statistics for all strategies"""
        stats = {}
        for name, perf in self.strategy_performance.items():
            total = perf['wins'] + perf['losses']
            stats[name] = {
                'win_rate': perf['wins'] / total if total > 0 else 0,
                'total_trades': total,
                'wins': perf['wins'],
                'losses': perf['losses']
            }
        return stats
