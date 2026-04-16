"""
Risk Manager Agent
Monitors portfolio risk and enforces limits
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from agents.base_agent import BaseAgent, Signal
from core.redis_queue import MessageBus, SwarmChannels
from core.config import TRADING_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class RiskMetrics:
    """Portfolio risk metrics"""
    total_exposure: float
    daily_pnl: float
    daily_drawdown: float
    var_95: float  # Value at Risk (95%)
    sharpe_ratio: float
    win_rate: float
    largest_loss: float
    open_positions: int

class RiskManager(BaseAgent):
    """
    Risk management specialist agent
    Monitors all positions and enforces risk limits
    """
    
    def __init__(self):
        super().__init__(agent_id="risk_manager", market="all")
        
        # Risk limits
        self.max_position_size = TRADING_CONFIG.MAX_POSITION_SIZE_PCT
        self.max_daily_loss = TRADING_CONFIG.MAX_DAILY_LOSS_PCT
        self.max_total_exposure = TRADING_CONFIG.MAX_TOTAL_EXPOSURE
        self.max_open_positions = 10
        
        # Tracking
        self.positions = {}
        self.daily_trades = []
        self.risk_alerts = []
        
        # Calculation interval
        self.decision_interval = 30  # Check every 30 seconds
        
    async def gather_data(self) -> Dict[str, Any]:
        """Gather risk data from all sources"""
        data = {
            'timestamp': datetime.utcnow(),
            'positions': self.positions,
            'exposure': self._calculate_exposure(),
            'daily_stats': self._calculate_daily_stats(),
            'correlation_matrix': self._calculate_correlations()
        }
        return data
    
    async def analyze(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyze risk and issue alerts if needed"""
        exposure = data.get('exposure', {})
        daily_stats = data.get('daily_stats', {})
        
        # Check various risk limits
        alerts = []
        
        # 1. Position size check
        for symbol, pos in self.positions.items():
            pos_size = abs(pos.get('size', 0))
            if pos_size > self.max_position_size:
                alerts.append({
                    'level': 'high',
                    'type': 'oversized_position',
                    'symbol': symbol,
                    'message': f'Position {symbol} exceeds max size ({pos_size:.2%})'
                })
        
        # 2. Daily loss check
        daily_pnl = daily_stats.get('pnl', 0)
        if daily_pnl < -self.max_daily_loss:
            alerts.append({
                'level': 'critical',
                'type': 'daily_loss_limit',
                'message': f'Daily loss limit breached: {daily_pnl:.2%}'
            })
        
        # 3. Total exposure check
        total_exposure = exposure.get('total', 0)
        if total_exposure > self.max_total_exposure:
            alerts.append({
                'level': 'high',
                'type': 'exposure_limit',
                'message': f'Total exposure {total_exposure:.2%} exceeds limit'
            })
        
        # 4. Open positions check
        open_count = len(self.positions)
        if open_count >= self.max_open_positions:
            alerts.append({
                'level': 'warning',
                'type': 'max_positions',
                'message': f'Max positions reached: {open_count}'
            })
        
        # 5. Correlation check
        correlations = data.get('correlation_matrix', {})
        high_corr_pairs = self._find_high_correlations(correlations, threshold=0.8)
        if high_corr_pairs:
            alerts.append({
                'level': 'warning',
                'type': 'high_correlation',
                'message': f'High correlation detected: {high_corr_pairs}'
            })
        
        # Publish alerts
        for alert in alerts:
            await self._publish_risk_alert(alert)
        
        # Return signal if critical
        critical_alerts = [a for a in alerts if a['level'] == 'critical']
        if critical_alerts:
            return Signal(
                agent=self.agent_id,
                market='all',
                symbol='PORTFOLIO',
                action='emergency_close',
                confidence=1.0,
                strategy='risk_management',
                reasoning=f"Critical risk alerts: {len(critical_alerts)}"
            )
        
        return None
    
    async def execute_command(self, command: str, params: Dict[str, Any]):
        """Execute risk-related commands"""
        if command == 'update_position':
            self._update_position(params)
        elif command == 'close_all':
            await self._close_all_positions()
        elif command == 'get_risk_report':
            return self._generate_risk_report()
    
    def _update_position(self, params: Dict):
        """Update position tracking"""
        symbol = params['symbol']
        size = params.get('size', 0)
        
        if size == 0:
            if symbol in self.positions:
                del self.positions[symbol]
        else:
            self.positions[symbol] = {
                'size': size,
                'entry_price': params.get('entry_price', 0),
                'timestamp': datetime.utcnow()
            }
    
    def _calculate_exposure(self) -> Dict[str, float]:
        """Calculate total exposure by market"""
        exposure = {
            'crypto': 0.0,
            'forex': 0.0,
            'futures': 0.0,
            'total': 0.0
        }
        
        for symbol, pos in self.positions.items():
            size = abs(pos.get('size', 0))
            
            if 'USDT' in symbol or 'BTC' in symbol or 'ETH' in symbol:
                exposure['crypto'] += size
            elif 'USD' in symbol and '/' in symbol:
                exposure['forex'] += size
            else:
                exposure['futures'] += size
            
            exposure['total'] += size
        
        return exposure
    
    def _calculate_daily_stats(self) -> Dict[str, float]:
        """Calculate daily trading statistics"""
        today = datetime.utcnow().date()
        todays_trades = [t for t in self.daily_trades 
                        if t.get('timestamp', datetime.utcnow()).date() == today]
        
        if not todays_trades:
            return {'pnl': 0, 'trades': 0, 'win_rate': 0}
        
        total_pnl = sum(t.get('pnl', 0) for t in todays_trades)
        winning_trades = sum(1 for t in todays_trades if t.get('pnl', 0) > 0)
        
        return {
            'pnl': total_pnl,
            'trades': len(todays_trades),
            'win_rate': winning_trades / len(todays_trades) if todays_trades else 0
        }
    
    def _calculate_correlations(self) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between positions"""
        # Simplified - would use actual price history
        return {}
    
    def _find_high_correlations(self, correlations: Dict, threshold: float) -> List:
        """Find pairs with high correlation"""
        high_corr = []
        for sym1, corrs in correlations.items():
            for sym2, corr in corrs.items():
                if abs(corr) > threshold and sym1 != sym2:
                    high_corr.append((sym1, sym2, corr))
        return high_corr
    
    async def _publish_risk_alert(self, alert: Dict):
        """Publish risk alert to swarm"""
        message = {
            'agent': self.agent_id,
            'level': alert['level'],
            'type': alert['type'],
            'reason': alert['message'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.bus.publish(SwarmChannels.RISK_ALERTS, message)
        
        logger.warning(f"🛡️ Risk Alert [{alert['level'].upper()}]: {alert['message']}")
    
    async def _close_all_positions(self):
        """Emergency close all positions"""
        logger.critical("🛡️ Risk Manager initiating emergency position close")
        
        for symbol in list(self.positions.keys()):
            # Find which agent owns this position
            market = self._determine_market(symbol)
            agent_map = {
                'crypto': 'crypto_agent',
                'forex': 'forex_agent',
                'futures': 'futures_agent'
            }
            target = agent_map.get(market)
            
            if target:
                command = {
                    'target': target,
                    'command': 'close_position',
                    'params': {'symbol': symbol},
                    'priority': 'critical'
                }
                self.bus.publish(SwarmChannels.OPENCLAW_COMMANDS, command)
    
    def _determine_market(self, symbol: str) -> str:
        """Determine market from symbol"""
        if 'USDT' in symbol or 'BTC' in symbol:
            return 'crypto'
        elif 'USD' in symbol and '/' in symbol:
            return 'forex'
        else:
            return 'futures'
    
    def _generate_risk_report(self) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        exposure = self._calculate_exposure()
        daily_stats = self._calculate_daily_stats()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'exposure': exposure,
            'daily_stats': daily_stats,
            'open_positions': len(self.positions),
            'positions': self.positions,
            'alerts_24h': len(self.risk_alerts),
            'status': 'healthy' if not self.risk_alerts else 'at_risk'
        }
