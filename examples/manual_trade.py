"""
Example: Manual Trade

This example shows how to execute a manual trade through OpenClaw.
"""

import asyncio
from openclaw.core import OpenClaw

async def manual_trade_example():
    """Execute a manual trade"""
    
    openclaw = OpenClaw()
    
    # Connect to database
    await openclaw.db.connect()
    
    # Execute manual override
    await openclaw.manual_override(
        symbol='BTC/USDT',
        action='buy',
        reason='Testing manual override functionality'
    )
    
    print("✅ Manual trade executed")
    
    # Get status
    status = openclaw.get_status()
    print(f"OpenClaw Status: {status}")
    
    await openclaw.db.disconnect()

if __name__ == '__main__':
    asyncio.run(manual_trade_example())
