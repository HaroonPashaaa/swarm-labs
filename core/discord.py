"""
Discord integration for real-time alerts
"""

import logging
from typing import Dict, Any
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class DiscordNotifier:
    """Send alerts and updates to Discord"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.session = None
        
    async def connect(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def send_message(self, message: str, embed: Dict = None):
        """Send message to Discord"""
        if not self.webhook_url or not self.session:
            return
        
        try:
            payload = {
                'content': message,
            }
            
            if embed:
                payload['embeds'] = [embed]
            
            async with self.session.post(self.webhook_url, json=payload) as response:
                if response.status != 204:
                    logger.error(f"Failed to send Discord message: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
    
    async def notify_trade(self, symbol: str, action: str, confidence: float,
                          pnl: float = None):
        """Notify about trade"""
        color = 0x00FF00 if pnl and pnl > 0 else 0xFF0000 if pnl and pnl < 0 else 0xFFFF00
        
        embed = {
            'title': f'🐝 Trade {action.upper()}: {symbol}',
            'color': color,
            'fields': [
                {
                    'name': 'Confidence',
                    'value': f'{confidence:.1%}',
                    'inline': True
                }
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if pnl is not None:
            embed['fields'].append({
                'name': 'P&L',
                'value': f'${pnl:,.2f}',
                'inline': True
            })
        
        await self.send_message('', embed)
    
    async def notify_signal(self, agent: str, symbol: str, action: str,
                           confidence: float, strategy: str):
        """Notify about trading signal"""
        message = f"📡 **{agent}**: {action.upper()} {symbol} ({confidence:.0%}) - {strategy}"
        await self.send_message(message)
    
    async def notify_alert(self, level: str, message: str):
        """Notify about system alert"""
        emoji = {'critical': '🚨', 'high': '⚠️', 'warning': '⚡', 'info': 'ℹ️'}.get(level, 'ℹ️')
        formatted = f"{emoji} **[{level.upper()}]** {message}"
        await self.send_message(formatted)
    
    async def notify_performance(self, report: Any):
        """Notify about performance report"""
        embed = {
            'title': f'📊 {report.period.upper()} Performance Report',
            'color': 0x3498db,
            'fields': [
                {
                    'name': 'Total P&L',
                    'value': f'${report.total_pnl:,.2f}',
                    'inline': True
                },
                {
                    'name': 'Win Rate',
                    'value': f'{report.win_rate:.1%}',
                    'inline': True
                },
                {
                    'name': 'Total Trades',
                    'value': str(report.total_trades),
                    'inline': True
                },
                {
                    'name': 'Profit Factor',
                    'value': f'{report.profit_factor:.2f}',
                    'inline': True
                },
                {
                    'name': 'Max Drawdown',
                    'value': f'{report.max_drawdown:.1%}',
                    'inline': True
                },
                {
                    'name': 'Sharpe Ratio',
                    'value': f'{report.sharpe_ratio:.2f}',
                    'inline': True
                }
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_message('', embed)
