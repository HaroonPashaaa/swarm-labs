#!/usr/bin/env python3
"""
Clean up old logs and data
"""

import os
import glob
from datetime import datetime, timedelta
from pathlib import Path

def clean_old_logs(days=7):
    """Remove logs older than N days"""
    print(f"Cleaning logs older than {days} days...")
    
    cutoff = datetime.now() - timedelta(days=days)
    log_dir = Path('logs')
    
    if not log_dir.exists():
        return
    
    removed = 0
    for log_file in log_dir.glob('*.log'):
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        if mtime < cutoff:
            log_file.unlink()
            removed += 1
    
    print(f"✅ Removed {removed} old log files")

def clean_backups(keep=10):
    """Keep only N most recent backups"""
    print(f"Keeping {keep} most recent backups...")
    
    backup_dir = Path('backups')
    if not backup_dir.exists():
        return
    
    backups = sorted(backup_dir.glob('*'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    removed = 0
    for backup in backups[keep:]:
        backup.unlink()
        removed += 1
    
    print(f"✅ Removed {removed} old backups")

def clean_cache():
    """Clean Python cache"""
    print("Cleaning Python cache...")
    
    removed = 0
    for pycache in Path('.').rglob('__pycache__'):
        for f in pycache.glob('*'):
            f.unlink()
            removed += 1
        pycache.rmdir()
    
    print(f"✅ Removed {removed} cache files")

def main():
    """Run cleanup"""
    print("🧹 Cleaning up...")
    print("=" * 50)
    
    clean_old_logs()
    clean_backups()
    clean_cache()
    
    print("\n✅ Cleanup complete")

if __name__ == '__main__':
    main()
