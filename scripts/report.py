#!/usr/bin/env python3
"""
Performance Report Generator
Generate and display trading performance reports
"""

import asyncio
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '/app')

from core.database import DatabaseManager
from core.performance import PerformanceTracker

async def main():
    """Generate performance report"""
    print("📊 Wojak Capital Performance Report")
    print("=" * 50)
    print()
    
    # Connect to database
    db = DatabaseManager('postgresql://swarm:swarm@localhost:5432/swarm_labs')
    await db.connect()
    
    tracker = PerformanceTracker(db)
    
    # Daily report
    print("📅 DAILY REPORT")
    print("-" * 50)
    daily = await tracker.generate_daily_report()
    print(tracker.format_report(daily))
    print()
    
    # Weekly report
    print("📅 WEEKLY REPORT")
    print("-" * 50)
    weekly = await tracker.generate_weekly_report()
    print(tracker.format_report(weekly))
    print()
    
    await db.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
