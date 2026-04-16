# Troubleshooting

## Common Issues

### Connection Errors

**Problem**: Cannot connect to exchange

**Solution**:
```bash
# Check API keys
export BINANCE_API_KEY=your_key
export BINANCE_SECRET=your_secret

# Test connection
python -c "from exchanges.binance_client import BinanceClient; import asyncio; c = BinanceClient('key', 'secret', True); asyncio.run(c.connect())"
```

### Database Connection

**Problem**: Cannot connect to PostgreSQL

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
python scripts/init_db.py
```

### Redis Connection

**Problem**: Cannot connect to Redis

**Solution**:
```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Should return PONG
```

### Import Errors

**Problem**: Module not found

**Solution**:
```bash
# Ensure virtual environment is active
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Rate Limiting

**Problem**: Getting rate limited by exchange

**Solution**:
- Reduce `DECISION_INTERVAL_SECONDS` in config
- Check API tier limits
- Enable rate limiting in exchange client

### Memory Issues

**Problem**: Out of memory

**Solution**:
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart
```

## Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m openclaw.core
```

## Getting Help

1. Check logs: `docker-compose logs -f`
2. Enable debug mode
3. Check GitHub Issues
4. Join Discord community

## Reporting Bugs

Please include:
- Error message
- Logs (with sensitive info removed)
- Steps to reproduce
- Environment details
