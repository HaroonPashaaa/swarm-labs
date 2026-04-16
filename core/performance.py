"""
Performance tracking and reporting
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
import json

from core.database import DatabaseManager
from core.utils import calculate_drawdown, calculate_sharpe_ratio

logger = logging.getLogger(__name__)

@dataclass
class PerformanceReport:
    """Trading performance report"""
    period: str
    start_date: datetime
    end_date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float

class PerformanceTracker:
    """Track and report trading performance"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        
    async def generate_daily_report(self) -> PerformanceReport:
        """Generate daily performance report"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        
        return await self._generate_report(start_date, end_date, 'daily')
    
    async def generate_weekly_report(self) -> PerformanceReport:
        """Generate weekly performance report"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(weeks=1)
        
        return await self._generate_report(start_date, end_date, 'weekly')
    
    async def generate_monthly_report(self) -> PerformanceReport:
        """Generate monthly performance report"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        return await self._generate_report(start_date, end_date, 'monthly')
    
    async def _generate_report(self, start_date: datetime, end_date: datetime,
                              period: str) -> PerformanceReport:
        """Generate performance report for period"""
        
        # Get trades from database
        trades = await self.db.get_recent_trades(limit=1000)
        
        # Filter by date
        period_trades = [
            t for t in trades
            if start_date <= t.timestamp <= end_date
        ]
        
        if not period_trades:
            return PerformanceReport(
                period=period,
                start_date=start_date,
                end_date=end_date,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                profit_factor=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0
            )
        
        # Calculate metrics
        total_trades = len(period_trades)
        winning_trades = [t for t in period_trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in period_trades if t.pnl and t.pnl <= 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(t.pnl or 0 for t in period_trades)
        
        avg_win = sum(t.pnl or 0 for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl or 0 for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        gross_profit = sum(t.pnl or 0 for t in winning_trades)
        gross_loss = abs(sum(t.pnl or 0 for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Build equity curve for drawdown calculation
        equity_curve = []
        running_pnl = 0
        for t in sorted(period_trades, key=lambda x: x.timestamp):
            running_pnl += t.pnl or 0
            equity_curve.append(running_pnl)
        
        max_drawdown = calculate_drawdown(equity_curve) if equity_curve else 0
        
        # Calculate returns for Sharpe
        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i-1] != 0:
                ret = (equity_curve[i] - equity_curve[i-1]) / abs(equity_curve[i-1])
                returns.append(ret)
        
        sharpe_ratio = calculate_sharpe_ratio(returns) if len(returns) > 1 else 0
        
        return PerformanceReport(
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            total_pnl=total_pnl,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio
        )
    
    def format_report(self, report: PerformanceReport) -> str:
        """Format report as readable string"""
        lines = [
            f"📊 {report.period.upper()} PERFORMANCE REPORT",
            f"Period: {report.start_date.strftime('%Y-%m-%d')} to {report.end_date.strftime('%Y-%m-%d')}",
            "",
            "📈 TRADE STATISTICS",
            f"Total Trades: {report.total_trades}",
            f"Winning Trades: {report.winning_trades}",
            f"Losing Trades: {report.losing_trades}",
            f"Win Rate: {report.win_rate:.1%}",
            "",
            "💰 P&L",
            f"Total P&L: ${report.total_pnl:,.2f}",
            f"Average Win: ${report.avg_win:,.2f}",
            f"Average Loss: ${report.avg_loss:,.2f}",
            f"Profit Factor: {report.profit_factor:.2f}",
            "",
            "📉 RISK METRICS",
            f"Max Drawdown: {report.max_drawdown:.1%}",
            f"Sharpe Ratio: {report.sharpe_ratio:.2f}",
        ]
        
        return "\n".join(lines)
