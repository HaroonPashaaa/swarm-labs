#!/usr/bin/env python3
"""
Lint check script
"""

import subprocess
import sys

def run_flake8():
    """Run flake8 linter"""
    print("🔍 Running flake8...")
    result = subprocess.run(
        ['flake8', '.', '--count', '--statistics'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ No linting errors")
        return True
    else:
        print(result.stdout)
        return False

def run_black_check():
    """Check black formatting"""
    print("\n🔍 Checking black formatting...")
    result = subprocess.run(
        ['black', '--check', '.'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Code is formatted")
        return True
    else:
        print("⚠️  Code needs formatting: black .")
        return False

def main():
    """Run all lint checks"""
    print("🧹 Lint Checks")
    print("=" * 50)
    
    flake8_ok = run_flake8()
    black_ok = run_black_check()
    
    if flake8_ok and black_ok:
        print("\n✅ All checks passed")
        sys.exit(0)
    else:
        print("\n❌ Some checks failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
