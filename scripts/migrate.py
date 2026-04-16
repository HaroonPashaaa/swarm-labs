#!/usr/bin/env python3
"""
Database migration script
"""

import asyncio
import asyncpg
import sys
from datetime import datetime

async def get_current_version(conn):
    """Get current schema version"""
    try:
        row = await conn.fetchrow(
            "SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1"
        )
        return row['version'] if row else 0
    except:
        return 0

async def apply_migration(conn, version, sql):
    """Apply a migration"""
    print(f"Applying migration {version}...")
    
    async with conn.transaction():
        await conn.execute(sql)
        await conn.execute(
            "INSERT INTO schema_version (version, applied_at) VALUES ($1, $2)",
            version, datetime.utcnow()
        )
    
    print(f"✅ Migration {version} applied")

async def migrate():
    """Run all pending migrations"""
    database_url = 'postgresql://swarm:swarm@localhost:5432/swarm_labs'
    
    conn = await asyncpg.connect(database_url)
    
    try:
        # Create version table if not exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        current = await get_current_version(conn)
        print(f"Current version: {current}")
        
        # Define migrations
        migrations = {
            1: "CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY)",
        }
        
        for version, sql in sorted(migrations.items()):
            if version > current:
                await apply_migration(conn, version, sql)
        
        print("\n✅ All migrations complete")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(migrate())
