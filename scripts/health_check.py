#!/usr/bin/env python3
"""
Health Check Script
Verify all services are running
"""

import sys
import requests
import redis
import asyncpg
import asyncio

async def check_postgres():
    """Check PostgreSQL connection"""
    try:
        conn = await asyncpg.connect('postgresql://swarm:swarm@localhost:5432/swarm_labs')
        await conn.execute('SELECT 1')
        await conn.close()
        print("✅ PostgreSQL: OK")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL: {e}")
        return False

def check_redis():
    """Check Redis connection"""
    try:
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        print("✅ Redis: OK")
        return True
    except Exception as e:
        print(f"❌ Redis: {e}")
        return False

def check_swarm_api():
    """Check Swarm API"""
    try:
        response = requests.get('http://localhost:8080/health', timeout=5)
        if response.status_code == 200:
            print("✅ Swarm API: OK")
            return True
        else:
            print(f"❌ Swarm API: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Swarm API: {e}")
        return False

async def main():
    """Run all health checks"""
    print("🔍 Running health checks...\n")
    
    checks = [
        await check_postgres(),
        check_redis(),
        check_swarm_api()
    ]
    
    print()
    if all(checks):
        print("✅ All systems operational")
        sys.exit(0)
    else:
        print("❌ Some systems are down")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
