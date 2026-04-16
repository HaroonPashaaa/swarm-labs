# Contributing to Swarm Labs

Thank you for your interest in contributing to Swarm Labs!

## Development Setup

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Run `black` and `flake8` before committing

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_openclaw.py
```

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## Areas for Contribution

- Additional trading strategies
- New exchange integrations
- Improved risk management
- Backtesting framework
- Web dashboard
- Mobile app

## Code of Conduct

Be respectful and constructive in all interactions.
