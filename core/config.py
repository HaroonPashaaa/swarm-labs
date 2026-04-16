# Core Configuration
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TradingConfig:
    """Trading parameters"""
    # Mode
    PAPER_TRADING: bool = True
    
    # Risk Limits
    MAX_POSITION_SIZE_PCT: float = 0.02  # 2% of portfolio per trade
    MAX_DAILY_LOSS_PCT: float = 0.05     # 5% daily stop
    MAX_TOTAL_EXPOSURE: float = 0.20     # 20% total exposure
    MAX_LEVERAGE_CRYPTO: float = 5.0     # 5x max for crypto
    MAX_LEVERAGE_FOREX: float = 20.0     # 20x max for forex
    MAX_LEVERAGE_FUTURES: float = 10.0   # 10x max for futures
    
    # Position Management
    DEFAULT_STOP_LOSS_PCT: float = 0.02   # 2% stop loss
    DEFAULT_TAKE_PROFIT_PCT: float = 0.04 # 4% take profit
    TRAILING_STOP_PCT: float = 0.015      # 1.5% trailing stop
    
    # Strategy Weights
    MIN_CONFIDENCE_THRESHOLD: float = 0.65  # 65% min confidence for trade
    CONSENSUS_THRESHOLD: float = 0.60       # 60% consensus required

@dataclass
class AgentConfig:
    """Agent behavior settings"""
    # Decision Frequency
    DECISION_INTERVAL_SECONDS: int = 60  # Re-evaluate every minute
    
    # Communication
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/swarm_labs"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    DISCORD_WEBHOOK_URL: str = ""
    GITHUB_REPO: str = "HaroonPashaaa/swarm-labs"

@dataclass
class ExchangeConfig:
    """Exchange API configurations"""
    # Binance
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET: str = ""
    BINANCE_TESTNET: bool = True
    
    # Bybit
    BYBIT_API_KEY: str = ""
    BYBIT_SECRET: str = ""
    BYBIT_TESTNET: bool = True
    
    # Interactive Brokers
    IBKR_ACCOUNT_ID: str = ""
    IBKR_PORT: int = 7497  # TWS API port
    
    # OANDA
    OANDA_API_KEY: str = ""
    OANDA_ACCOUNT_ID: str = ""
    OANDA_PRACTICE: bool = True

# Global config instances
TRADING_CONFIG = TradingConfig()
AGENT_CONFIG = AgentConfig()
EXCHANGE_CONFIG = ExchangeConfig()

# Load from environment variables
def load_config_from_env():
    """Override defaults with environment variables"""
    TRADING_CONFIG.PAPER_TRADING = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
    TRADING_CONFIG.MAX_POSITION_SIZE_PCT = float(os.getenv('MAX_POSITION_SIZE_PCT', '0.02'))
    TRADING_CONFIG.MAX_DAILY_LOSS_PCT = float(os.getenv('MAX_DAILY_LOSS_PCT', '0.05'))
    
    AGENT_CONFIG.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    AGENT_CONFIG.REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    AGENT_CONFIG.DATABASE_URL = os.getenv('DATABASE_URL', AGENT_CONFIG.DATABASE_URL)
    AGENT_CONFIG.DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    EXCHANGE_CONFIG.BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    EXCHANGE_CONFIG.BINANCE_SECRET = os.getenv('BINANCE_SECRET', '')
    EXCHANGE_CONFIG.BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
    EXCHANGE_CONFIG.BYBIT_SECRET = os.getenv('BYBIT_SECRET', '')
    EXCHANGE_CONFIG.OANDA_API_KEY = os.getenv('OANDA_API_KEY', '')
    EXCHANGE_CONFIG.IBKR_ACCOUNT_ID = os.getenv('IBKR_ACCOUNT_ID', '')
