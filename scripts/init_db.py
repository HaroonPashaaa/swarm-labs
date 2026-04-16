"""
Database initialization script
Creates tables and sets up TimescaleDB
"""

import asyncio
import asyncpg
import os
from core.database import DatabaseManager

async def init_database():
    """Initialize database schema"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://swarm:swarm@localhost:5432/swarm_labs')
    
    db = DatabaseManager(database_url)
    
    print("Connecting to database...")
    await db.connect()
    
    print("Creating tables...")
    await db.init_tables()
    
    print("✅ Database initialized successfully!")
    
    await db.disconnect()

if __name__ == '__main__':
    asyncio.run(init_database())
