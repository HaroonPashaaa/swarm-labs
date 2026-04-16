# Benchmarking Guide

## Performance Benchmarks

### Latency Targets

| Operation | Target | Maximum |
|-----------|--------|---------|
| Signal generation | < 100ms | 500ms |
| Database write | < 50ms | 200ms |
| Redis publish | < 10ms | 50ms |
| Order execution | < 500ms | 2000ms |

### Throughput Targets

| Metric | Target |
|--------|--------|
| Signals per second | 100 |
| Trades per minute | 10 |
| Market data updates | 1000/sec |

## Load Testing

```bash
# Run load test
python scripts/benchmark.py --duration 60 --agents 4
```

## Optimization Tips

1. **Database**
   - Use connection pooling
   - Enable query caching
   - Optimize indexes

2. **Redis**
   - Use pipelining
   - Enable persistence
   - Monitor memory usage

3. **Python**
   - Use async/await
   - Profile hot paths
   - Consider Cython for critical code
