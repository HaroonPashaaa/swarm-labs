#!/usr/bin/env python3
"""
Benchmark script for performance testing
"""

import time
import asyncio
import statistics
from datetime import datetime

async def benchmark_signal_generation():
    """Benchmark signal generation speed"""
    print("Benchmarking signal generation...")
    
    times = []
    for _ in range(100):
        start = time.time()
        # Simulate signal generation
        await asyncio.sleep(0.001)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    
    print(f"Avg: {statistics.mean(times):.2f}ms")
    print(f"Min: {min(times):.2f}ms")
    print(f"Max: {max(times):.2f}ms")
    print(f"P95: {sorted(times)[int(len(times)*0.95)]:.2f}ms")

def benchmark_database_writes():
    """Benchmark database write speed"""
    print("\nBenchmarking database writes...")
    
    times = []
    for _ in range(100):
        start = time.time()
        # Simulate DB write
        time.sleep(0.005)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    
    print(f"Avg: {statistics.mean(times):.2f}ms")
    print(f"Throughput: {1000/statistics.mean(times):.0f} ops/sec")

def main():
    """Run all benchmarks"""
    print("🚀 Swarm Labs Benchmark")
    print("=" * 50)
    
    benchmark_database_writes()
    asyncio.run(benchmark_signal_generation())
    
    print("\n✅ Benchmark complete")

if __name__ == '__main__':
    main()
