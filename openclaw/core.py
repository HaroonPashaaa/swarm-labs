"""
OpenClaw - Central Orchestrator & CEO
The brain of the swarm that makes final trading decisions
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import json

from core.redis_queue import MessageBus, SwarmChannels
from core.database import DatabaseManager, AgentDecision, Trade
from core.config import AGENT_CONFIG, TRADING_CONFIG
from agents.base_agent import Signal

logger = logging.getLogger(__name__)

@dataclass
class SwarmConsensus:
    """Consensus result from swarm deliberation"""
    action: str  # buy, sell, hold
    confidence: float
    consensus_pct: float
    participating_agents: List[str]
    strategy_breakdown: Dict[str, float]
    market_context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TradingCommand:
    """Command issued by OpenClaw"""
    command: str
    target: str  # agent_id or 'all'
    params: Dict[str, Any]
    priority: str  # low, normal, high, critical
    timestamp: datetime = field(default_factory=datetime.utcnow)

class OpenClaw:
    """
    Central orchestrator for the swarm
    - Receives signals from all agents
    - Calculates weighted consensus
    - Makes final trading decisions
    - Issues commands to agents
    - Manages risk and exposure
    """
    
    def __init__(self):
        self.bus = MessageBus(
            host=AGENT_CONFIG.REDIS_HOST,
            port=AGENT_CONFIG.REDIS_PORT,
            db=AGENT_CONFIG.REDIS_DB
        )
        self.db = DatabaseManager(AGENT_CONFIG.DATABASE_URL)
        
        # Signal aggregation
        self.pending_signals: Dict[str, List[Signal]] = defaultdict(list)
        self.signal_timeout = 30  # seconds to wait for all agents
        
        # Decision tracking
        self.last_decisions: Dict[str, datetime] = {}
        self.decision_cooldown = 60  # seconds between decisions on same symbol
        
        # Risk management
        self.daily_pnl = 0.0
        self.daily_loss_limit = -1000.0  # $1000 daily loss limit
        self.max_open_positions = 10
        self.open_positions = 0
        
        # Performance tracking
        self.decision_history: List[Dict] = []
        self.win_rate = 0.0
        
        self.running = False
        
    async def start(self):
        """Start OpenClaw orchestrator"""
        logger.info("🧠 OpenClaw starting...")
        self.running = True
        
        # Connect to database
        await self.db.connect()
        await self.db.init_tables()
        
        # Subscribe to agent signals
        self.bus.subscribe(SwarmChannels.AGENT_DECISIONS, self._handle_agent_signal)
        self.bus.subscribe(SwarmChannels.RISK_ALERTS, self._handle_risk_alert)
        self.bus.subscribe(SwarmChannels.SYSTEM_STATUS, self._handle_system_status)
        
        # Start message listener
        asyncio.create_task(self.bus.listen())
        
        # Start main decision loop
        await self._decision_loop()
    
    async def stop(self):
        """Stop OpenClaw"""
        logger.info("🛑 OpenClaw stopping...")
        self.running = False
        await self.db.disconnect()
    
    async def _decision_loop(self):
        """Main decision processing loop"""
        while self.running:
            try:
                # Process any pending signal groups
                await self._process_pending_signals()
                
                # Check risk limits
                await self._check_risk_limits()
                
                # Wait before next cycle
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in OpenClaw decision loop: {e}")
                await asyncio.sleep(10)
    
    async def _handle_agent_signal(self, message: Dict):
        """Handle incoming signal from agent"""
        try:
            # Convert message to Signal
            signal = Signal(
                agent=message['agent'],
                market=message['market'],
                symbol=message['symbol'],
                action=message['action'],
                confidence=message['confidence'],
                strategy=message['strategy'],
                reasoning=message['reasoning'],
                metadata=message.get('metadata', {}),
                timestamp=datetime.fromisoformat(message['timestamp'])
            )
            
            # Group by symbol
            symbol_key = f"{signal.market}:{signal.symbol}"
            self.pending_signals[symbol_key].append(signal)
            
            logger.info(f"📡 OpenClaw received signal from {signal.agent}: "
                       f"{signal.action} {signal.symbol} ({signal.confidence:.2f})")
            
            # Log to database
            await self.db.log_agent_decision(AgentDecision(
                timestamp=signal.timestamp,
                agent=signal.agent,
                market=signal.market,
                decision=signal.action,
                confidence=signal.confidence,
                strategy=signal.strategy,
                reasoning=signal.reasoning,
                signals=signal.metadata
            ))
            
        except Exception as e:
            logger.error(f"Error handling agent signal: {e}")
    
    async def _process_pending_signals(self):
        """Process groups of pending signals"""
        current_time = datetime.utcnow()
        
        for symbol_key, signals in list(self.pending_signals.items()):
            if not signals:
                continue
            
            # Check if we have signals from all agents or timeout reached
            agents_responded = set(s.agent for s in signals)
            time_since_first = (current_time - signals[0].timestamp).total_seconds()
            
            if len(agents_responded) >= 3 or time_since_first > self.signal_timeout:
                # Calculate consensus
                consensus = self._calculate_consensus(signals)
                
                # Make decision
                await self._make_decision(symbol_key, consensus, signals)
                
                # Clear processed signals
                self.pending_signals[symbol_key] = []
    
    def _calculate_consensus(self, signals: List[Signal]) -> SwarmConsensus:
        """Calculate weighted consensus from agent signals"""
        if not signals:
            return SwarmConsensus('hold', 0.0, 0.0, [], {}, {})
        
        # Weight by confidence
        weighted_votes = defaultdict(float)
        strategy_scores = defaultdict(float)
        
        for signal in signals:
            # Weight = confidence * market expertise factor
            weight = signal.confidence
            
            # Add to weighted votes
            weighted_votes[signal.action] += weight
            
            # Track strategy performance
            strategy_scores[signal.strategy] += weight
        
        # Determine winning action
        total_weight = sum(weighted_votes.values())
        if total_weight == 0:
            return SwarmConsensus('hold', 0.0, 0.0, [], {}, {})
        
        winning_action = max(weighted_votes.keys(), key=lambda k: weighted_votes[k])
        consensus_pct = weighted_votes[winning_action] / total_weight
        
        # Calculate average confidence for winning action
        winning_signals = [s for s in signals if s.action == winning_action]
        avg_confidence = sum(s.confidence for s in winning_signals) / len(winning_signals)
        
        # Build market context
        market_context = {
            'signals_received': len(signals),
            'agents_participating': list(set(s.agent for s in signals)),
            'vote_distribution': dict(weighted_votes),
            'time_window': (signals[-1].timestamp - signals[0].timestamp).total_seconds()
        }
        
        return SwarmConsensus(
            action=winning_action,
            confidence=avg_confidence,
            consensus_pct=consensus_pct,
            participating_agents=[s.agent for s in signals],
            strategy_breakdown=dict(strategy_scores),
            market_context=market_context
        )
    
    async def _make_decision(self, symbol_key: str, consensus: SwarmConsensus, 
                            signals: List[Signal]):
        """Make final trading decision based on consensus"""
        market, symbol = symbol_key.split(':', 1)
        
        # Check cooldown
        if symbol_key in self.last_decisions:
            time_since = (datetime.utcnow() - self.last_decisions[symbol_key]).total_seconds()
            if time_since < self.decision_cooldown:
                logger.debug(f"Decision cooldown active for {symbol_key}")
                return
        
        # Decision criteria
        if consensus.action == 'hold':
            logger.info(f"⏸️ OpenClaw: HOLD {symbol} (consensus: {consensus.consensus_pct:.2f})")
            return
        
        if consensus.confidence < TRADING_CONFIG.MIN_CONFIDENCE_THRESHOLD:
            logger.info(f"⏸️ OpenClaw: LOW CONFIDENCE on {symbol} "
                       f"({consensus.confidence:.2f} < {TRADING_CONFIG.MIN_CONFIDENCE_THRESHOLD})")
            return
        
        if consensus.consensus_pct < TRADING_CONFIG.CONSENSUS_THRESHOLD:
            logger.info(f"⏸️ OpenClaw: NO CONSENSUS on {symbol} "
                       f"({consensus.consensus_pct:.2f} < {TRADING_CONFIG.CONSENSUS_THRESHOLD})")
            return
        
        # Check risk limits
        if self.open_positions >= self.max_open_positions:
            logger.warning(f"⚠️ OpenClaw: Max positions reached ({self.max_open_positions})")
            return
        
        if self.daily_pnl <= self.daily_loss_limit:
            logger.critical(f"🛑 OpenClaw: Daily loss limit hit! No new trades.")
            return
        
        # APPROVE TRADE
        logger.info(f"✅ OpenClaw: APPROVE {consensus.action.upper()} {symbol} "
                   f"(confidence: {consensus.confidence:.2f}, "
                   f"consensus: {consensus.consensus_pct:.2f})")
        
        # Update tracking
        self.last_decisions[symbol_key] = datetime.utcnow()
        self.open_positions += 1
        
        # Issue command to appropriate agent
        await self._issue_trade_command(market, symbol, consensus.action, signals)
        
        # Log decision
        self._log_decision(symbol_key, consensus, signals)
    
    async def _issue_trade_command(self, market: str, symbol: str, 
                                   action: str, signals: List[Signal]):
        """Issue trade command to appropriate agent"""
        # Determine which agent should execute
        agent_map = {
            'crypto': 'crypto_agent',
            'forex': 'forex_agent',
            'futures': 'futures_agent'
        }
        
        target_agent = agent_map.get(market)
        if not target_agent:
            logger.error(f"Unknown market: {market}")
            return
        
        # Build command
        signal = signals[0]  # Use first signal for sizing
        command = {
            'target': target_agent,
            'command': 'place_order',
            'params': {
                'symbol': symbol,
                'side': action,
                'reason': f"Swarm consensus: {signal.strategy}",
                'confidence': signal.confidence,
                'metadata': {
                    'openclaw_decision': True,
                    'swarm_consensus': signal.confidence
                }
            },
            'priority': 'high'
        }
        
        # Publish command
        self.bus.publish(SwarmChannels.OPENCLAW_COMMANDS, command)
        
        # Broadcast to all agents for awareness
        self.bus.broadcast({
            'type': 'trade_approved',
            'market': market,
            'symbol': symbol,
            'action': action,
            'agent': target_agent,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        logger.info(f"📤 OpenClaw issued {action} command to {target_agent} for {symbol}")
    
    async def _check_risk_limits(self):
        """Check and enforce risk limits"""
        # Update daily PnL from database
        stats = await self.db.get_performance_stats(days=1)
        self.daily_pnl = stats.get('total_pnl', 0)
        
        # Check if we're near limits
        if self.daily_pnl <= self.daily_loss_limit * 0.8:  # 80% of limit
            logger.warning(f"⚠️ OpenClaw: Approaching daily loss limit "
                          f"({self.daily_pnl:.2f} / {self.daily_loss_limit:.2f})")
        
        # Emergency stop if limit hit
        if self.daily_pnl <= self.daily_loss_limit:
            await self._emergency_stop("Daily loss limit reached")
    
    async def _emergency_stop(self, reason: str):
        """Emergency stop - close all positions"""
        logger.critical(f"🚨 OPENCLAW EMERGENCY STOP: {reason}")
        
        command = {
            'target': 'all',
            'command': 'emergency_stop',
            'params': {'reason': reason},
            'priority': 'critical'
        }
        
        self.bus.publish(SwarmChannels.OPENCLAW_COMMANDS, command)
    
    async def _handle_risk_alert(self, message: Dict):
        """Handle risk alerts from Risk Manager"""
        alert_level = message.get('level', 'info')
        alert_reason = message.get('reason', '')
        
        logger.warning(f"🛡️ OpenClaw received risk alert [{alert_level}]: {alert_reason}")
        
        if alert_level == 'critical':
            await self._emergency_stop(alert_reason)
        elif alert_level == 'high':
            # Reduce position sizes
            pass
    
    async def _handle_system_status(self, message: Dict):
        """Handle system status updates"""
        pass
    
    def _log_decision(self, symbol_key: str, consensus: SwarmConsensus, 
                     signals: List[Signal]):
        """Log decision to history"""
        decision_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'symbol': symbol_key,
            'consensus': consensus,
            'signals': [self._signal_to_dict(s) for s in signals]
        }
        
        self.decision_history.append(decision_record)
        
        # Keep only last 1000 decisions
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
    
    def _signal_to_dict(self, signal: Signal) -> Dict:
        """Convert signal to dictionary"""
        return {
            'agent': signal.agent,
            'market': signal.market,
            'symbol': signal.symbol,
            'action': signal.action,
            'confidence': signal.confidence,
            'strategy': signal.strategy,
            'reasoning': signal.reasoning,
            'timestamp': signal.timestamp.isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get OpenClaw status"""
        return {
            'status': 'running' if self.running else 'stopped',
            'daily_pnl': self.daily_pnl,
            'open_positions': self.open_positions,
            'max_positions': self.max_open_positions,
            'pending_signals': {k: len(v) for k, v in self.pending_signals.items()},
            'recent_decisions': len(self.decision_history),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def manual_override(self, symbol: str, action: str, reason: str):
        """Manual override - force trade decision"""
        logger.info(f"👤 OpenClaw MANUAL OVERRIDE: {action} {symbol} - {reason}")
        
        # Determine market from symbol
        market = 'crypto'  # default
        if 'USD' in symbol and '/' in symbol:
            market = 'forex'
        elif symbol in ['ES', 'NQ', 'YM']:
            market = 'futures'
        
        await self._issue_trade_command(market, symbol, action, [])
