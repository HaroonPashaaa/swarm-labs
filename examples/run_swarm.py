"""
Example: Running the Swarm

This example shows how to start and run the swarm.
"""

import asyncio
import logging

from openclaw.core import OpenClaw
from agents.crypto_agent import CryptoAgent
from agents.forex_agent import ForexAgent
from agents.futures_agent import FuturesAgent
from agents.risk_manager import RiskManager
from core.config import AGENT_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main function to run the swarm"""
    
    print("🐝 Starting Wojak Capital...")
    
    # Initialize OpenClaw
    openclaw = OpenClaw()
    
    # Initialize agents
    agents = [
        CryptoAgent(),
        ForexAgent(),
        FuturesAgent(),
        RiskManager()
    ]
    
    # Start all agents
    agent_tasks = [asyncio.create_task(agent.start()) for agent in agents]
    
    # Start OpenClaw
    openclaw_task = asyncio.create_task(openclaw.start())
    
    print("✅ Swarm is running!")
    print("Press Ctrl+C to stop")
    
    try:
        # Run indefinitely
        await asyncio.gather(*agent_tasks, openclaw_task)
    except KeyboardInterrupt:
        print("\n🛑 Stopping swarm...")
        
        # Stop all components
        for agent in agents:
            await agent.stop()
        
        await openclaw.stop()
        
        print("✅ Swarm stopped")

if __name__ == '__main__':
    asyncio.run(main())
