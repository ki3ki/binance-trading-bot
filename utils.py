"""
Utility functions for the Binance Trading Bot
Includes logging, validation, and formatting helpers
"""

import logging
import os
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate

# Initialize colorama for Windows
init(autoreset=True)

def setup_logging(log_file='logs/trading_bot.log', log_level=logging.INFO):
    """
    Setup logging configuration with both file and console handlers
    
    Args:
        log_file (str): Path to log file
        log_level: Logging level (default: INFO)
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('TradingBot')
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(levelname)-8s | %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def print_header(text):
    """Print a formatted header"""
    print("\n" + Fore.CYAN + "="*60)
    print(Fore.CYAN + text.center(60))
    print(Fore.CYAN + "="*60 + Style.RESET_ALL)


def print_success(text):
    """Print success message in green"""
    print(Fore.GREEN + "✓ " + text + Style.RESET_ALL)


def print_error(text):
    """Print error message in red"""
    print(Fore.RED + "✗ " + text + Style.RESET_ALL)


def print_warning(text):
    """Print warning message in yellow"""
    print(Fore.YELLOW + "⚠ " + text + Style.RESET_ALL)


def print_info(text):
    """Print info message in blue"""
    print(Fore.BLUE + "ℹ " + text + Style.RESET_ALL)


def format_order_details(order_data):
    """
    Format order details for display
    
    Args:
        order_data (dict): Order response from Binance API
    
    Returns:
        str: Formatted order details
    """
    if not order_data:
        return "No order data available"
    
    table_data = [
        ["Order ID", order_data.get('orderId', 'N/A')],
        ["Symbol", order_data.get('symbol', 'N/A')],
        ["Side", order_data.get('side', 'N/A')],
        ["Type", order_data.get('type', 'N/A')],
        ["Quantity", order_data.get('origQty', 'N/A')],
        ["Price", order_data.get('price', 'Market Price')],
        ["Status", order_data.get('status', 'N/A')],
        ["Time", datetime.fromtimestamp(order_data.get('updateTime', 0)/1000).strftime('%Y-%m-%d %H:%M:%S') if order_data.get('updateTime') else 'N/A']
    ]
    
    return tabulate(table_data, tablefmt="grid")


def validate_symbol(symbol):
    """
    Validate trading symbol format
    
    Args:
        symbol (str): Trading pair symbol
    
    Returns:
        str: Uppercase symbol
    
    Raises:
        ValueError: If symbol format is invalid
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string")
    
    symbol = symbol.upper().strip()
    
    if len(symbol) < 6:
        raise ValueError("Symbol too short. Example: BTCUSDT")
    
    return symbol


def validate_quantity(quantity):
    """
    Validate order quantity
    
    Args:
        quantity: Quantity to validate
    
    Returns:
        float: Validated quantity
    
    Raises:
        ValueError: If quantity is invalid
    """
    try:
        qty = float(quantity)
        if qty <= 0:
            raise ValueError("Quantity must be greater than 0")
        return qty
    except (TypeError, ValueError):
        raise ValueError("Invalid quantity. Must be a positive number")


def validate_price(price):
    """
    Validate order price
    
    Args:
        price: Price to validate
    
    Returns:
        float: Validated price
    
    Raises:
        ValueError: If price is invalid
    """
    try:
        p = float(price)
        if p <= 0:
            raise ValueError("Price must be greater than 0")
        return p
    except (TypeError, ValueError):
        raise ValueError("Invalid price. Must be a positive number")


def get_user_confirmation(prompt):
    """
    Get yes/no confirmation from user
    
    Args:
        prompt (str): Confirmation prompt
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    while True:
        response = input(f"\n{prompt} (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print_warning("Please enter 'yes' or 'no'")


def format_balance(balance_data):
    """
    Format account balance for display
    
    Args:
        balance_data (list): List of balance dictionaries
    
    Returns:
        str: Formatted balance table
    """
    if not balance_data:
        return "No balance data available"
    
    # Filter out zero balances and format
    filtered_balances = [
        [b['asset'], f"{float(b['balance']):.8f}", f"{float(b['availableBalance']):.8f}"]
        for b in balance_data
        if float(b['balance']) > 0
    ]
    
    if not filtered_balances:
        return "No non-zero balances found"
    
    headers = ["Asset", "Balance", "Available"]
    return tabulate(filtered_balances, headers=headers, tablefmt="grid")