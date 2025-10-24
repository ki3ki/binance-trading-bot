"""
Configuration management for Binance Trading Bot
Handles API credentials and settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for bot settings"""
    
    # API Credentials
    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_API_SECRET')
    
    # Testnet Settings
    TESTNET = os.getenv('TESTNET', 'True').lower() == 'true'
    TESTNET_URL = 'https://testnet.binancefuture.com'
    
    # Trading Settings
    DEFAULT_SYMBOL = 'BTCUSDT'
    DEFAULT_QUANTITY = 0.001
    
    # Logging Settings
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/trading_bot.log'
    
    # TWAP Settings
    TWAP_DEFAULT_INTERVALS = 5
    TWAP_DEFAULT_DURATION = 300  # 5 minutes in seconds
    
    @classmethod
    def validate(cls):
        """Validate that all required settings are present"""
        if not cls.API_KEY or not cls.API_SECRET:
            raise ValueError(
                "API credentials not found! Please set BINANCE_API_KEY and "
                "BINANCE_API_SECRET in your .env file"
            )
        return True
    
    @classmethod
    def display(cls):
        """Display current configuration (hide sensitive data)"""
        print("\n" + "="*60)
        print("CONFIGURATION")
        print("="*60)
        print(f"Testnet Mode: {cls.TESTNET}")
        print(f"API Key: {cls.API_KEY[:8]}...{cls.API_KEY[-4:] if cls.API_KEY else 'NOT SET'}")
        print(f"Default Symbol: {cls.DEFAULT_SYMBOL}")
        print(f"Default Quantity: {cls.DEFAULT_QUANTITY}")
        print("="*60 + "\n")