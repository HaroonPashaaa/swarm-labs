#!/usr/bin/env python3
"""
Backup Script
Create database and configuration backups
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

def backup_postgres():
    """Backup PostgreSQL database"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backups/postgres_{timestamp}.sql"
    
    Path("backups").mkdir(exist_ok=True)
    
    try:
        subprocess.run([
            'pg_dump',
            '-h', 'localhost',
            '-U', 'swarm',
            '-d', 'swarm_labs',
            '-f', backup_file
        ], check=True)
        
        print(f"✅ PostgreSQL backup: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL backup failed: {e}")
        return False

def backup_redis():
    """Backup Redis data"""
    try:
        subprocess.run([
            'docker', 'exec', 'swarm-redis',
            'redis-cli', 'SAVE'
        ], check=True)
        
        subprocess.run([
            'docker', 'cp',
            'swarm-redis:/data/dump.rdb',
            f'backups/redis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.rdb'
        ], check=True)
        
        print("✅ Redis backup complete")
        return True
    except Exception as e:
        print(f"❌ Redis backup failed: {e}")
        return False

def backup_env():
    """Backup environment files"""
    try:
        subprocess.run([
            'cp', '.env', 
            f'backups/env_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        ], check=True)
        
        print("✅ Environment backup complete")
        return True
    except Exception as e:
        print(f"❌ Environment backup failed: {e}")
        return False

def main():
    """Run all backups"""
    print("💾 Starting backup...\n")
    
    results = [
        backup_postgres(),
        backup_redis(),
        backup_env()
    ]
    
    print()
    if all(results):
        print("✅ All backups completed successfully")
    else:
        print("⚠️  Some backups failed")

if __name__ == '__main__':
    main()
