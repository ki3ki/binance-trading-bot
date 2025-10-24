"""
Binance Futures Trading Bot - Main Module
Supports Market, Limit, Stop-Limit, OCO, and TWAP orders
"""

from binance import Client
from binance.exceptions import BinanceAPIException
import sys

from config import Config
from orders import OrderExecutor
from utils import (
    setup_logging, print_header, print_success, print_error, 
    print_info, print_warning, validate_symbol, get_user_confirmation,
    format_balance
)


class BasicBot:
    """Main trading bot class"""
    
    def __init__(self, api_key, api_secret, testnet=True):
        """
        Initialize the trading bot
        
        Args:
            api_key (str): Binance API key
            api_secret (str): Binance API secret
            testnet (bool): Use testnet (default: True)
        """
        # Setup logging
        self.logger = setup_logging(Config.LOG_FILE)
        self.logger.info("Initializing Binance Trading Bot")
        
        # Initialize Binance client
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            
            if testnet:
                self.client.API_URL = 'https://testnet.binancefuture.com'
                self.logger.info("Using Binance Testnet")
                print_success("Connected to Binance Testnet")
            else:
                self.logger.warning("Using LIVE Binance API")
                print_warning("Connected to LIVE Binance API")
            
            # Test connection
            self.test_connection()
            
            # Initialize order executor
            self.order_executor = OrderExecutor(self.client, self.logger)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {str(e)}")
            print_error(f"Failed to initialize bot: {str(e)}")
            raise
    
    def test_connection(self):
        """Test API connection"""
        try:
            # Test connectivity
            self.client.ping()
            
            # Get server time
            server_time = self.client.get_server_time()
            self.logger.info(f"Server time: {server_time['serverTime']}")
            
            # Get account info
            account = self.client.futures_account()
            self.logger.info("Successfully connected to Binance API")
            print_success("API connection successful")
            
            return True
            
        except BinanceAPIException as e:
            error_msg = f"API Connection failed: {e.message} (Code: {e.code})"
            self.logger.error(error_msg)
            print_error(error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Connection test failed: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            return False
    
    def get_account_balance(self):
        """Get and display account balance"""
        try:
            account = self.client.futures_account()
            
            # Handle different response structures
            if 'assets' in account:
                balances = account['assets']
            elif 'positions' in account:
                # Alternative: use positions data
                balances = [
                    {
                        'asset': pos.get('asset', 'USDT'),
                        'balance': pos.get('initialMargin', '0'),
                        'availableBalance': pos.get('availableBalance', '0')
                    }
                    for pos in account['positions']
                ]
            else:
                # Fallback: show total balance
                total_balance = account.get('totalWalletBalance', account.get('totalMarginBalance', '0'))
                available = account.get('availableBalance', account.get('maxWithdrawAmount', '0'))
                
                balances = [{
                    'asset': 'USDT',
                    'balance': total_balance,
                    'availableBalance': available
                }]
            
            print_header("ACCOUNT BALANCE")
            print(format_balance(balances))
            
            # Also show additional account info
            print(f"\nTotal Wallet Balance: {account.get('totalWalletBalance', 'N/A')} USDT")
            print(f"Available Balance: {account.get('availableBalance', 'N/A')} USDT")
            
            return balances
            
        except Exception as e:
            error_msg = f"Failed to get account balance: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            
            # Debug: print the actual account structure
            try:
                print_warning("Debug: Fetching account data...")
                account = self.client.futures_account()
                print(f"Account keys available: {list(account.keys())}")
                
                # Try to show any balance info available
                if 'totalWalletBalance' in account:
                    print(f"\nTotal Wallet Balance: {account['totalWalletBalance']} USDT")
                if 'availableBalance' in account:
                    print(f"Available Balance: {account['availableBalance']} USDT")
                    
            except Exception as debug_error:
                print_error(f"Debug error: {str(debug_error)}")
            
            return None
    
    def get_current_price(self, symbol):
        """
        Get current market price for a symbol
        
        Args:
            symbol (str): Trading pair
        
        Returns:
            float: Current price or None if failed
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            print_info(f"Current {symbol} price: {price}")
            return price
            
        except Exception as e:
            error_msg = f"Failed to get current price: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
    
    def run_cli(self):
        """Run the command-line interface"""
        print_header("BINANCE FUTURES TRADING BOT")
        print_info("Type 'help' for available commands or 'exit' to quit")
        
        while True:
            try:
                print("\n" + "-"*60)
                command = input("\nEnter command: ").strip().lower()
                
                if command == 'exit' or command == 'quit':
                    print_info("Shutting down bot...")
                    break
                
                elif command == 'help':
                    self.show_help()
                
                elif command == 'balance':
                    self.get_account_balance()
                
                elif command == 'price':
                    self.handle_price_command()
                
                elif command == 'market':
                    self.handle_market_order()
                
                elif command == 'limit':
                    self.handle_limit_order()
                
                elif command == 'stop-limit':
                    self.handle_stop_limit_order()
                
                elif command == 'oco':
                    self.handle_oco_order()
                
                elif command == 'twap':
                    self.handle_twap_order()
                
                elif command == 'status':
                    self.handle_order_status()
                
                elif command == 'cancel':
                    self.handle_cancel_order()
                
                elif command == 'config':
                    Config.display()
                
                else:
                    print_error(f"Unknown command: '{command}'. Type 'help' for available commands")
            
            except KeyboardInterrupt:
                print("\n")
                print_info("Interrupted. Type 'exit' to quit")
            
            except Exception as e:
                print_error(f"Error: {str(e)}")
                self.logger.error(f"CLI error: {str(e)}")
    
    def show_help(self):
        """Display help information"""
        print_header("AVAILABLE COMMANDS")
        
        help_text = """
        ACCOUNT COMMANDS:
          balance         - Show account balance
          price           - Get current price for a symbol
          config          - Show current configuration
        
        ORDER COMMANDS:
          market          - Place a market order (buy/sell at current price)
          limit           - Place a limit order (buy/sell at specific price)
          stop-limit      - Place a stop-limit order (triggers at stop price)
          oco             - Place an OCO order (One-Cancels-Other)
          twap            - Place a TWAP order (Time-Weighted Average Price)
        
        ORDER MANAGEMENT:
          status          - Check status of an order
          cancel          - Cancel an existing order
        
        GENERAL:
          help            - Show this help message
          exit/quit       - Exit the bot
        
        EXAMPLE USAGE:
          1. Check balance: Type 'balance'
          2. Get BTC price: Type 'price' then enter 'BTCUSDT'
          3. Buy 0.001 BTC at market: Type 'market' then follow prompts
        """
        
        print(help_text)
    
    def handle_price_command(self):
        """Handle price check command"""
        try:
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            symbol = validate_symbol(symbol)
            self.get_current_price(symbol)
            
        except ValueError as e:
            print_error(str(e))
        except Exception as e:
            print_error(f"Error getting price: {str(e)}")
    
    def handle_market_order(self):
        """Handle market order placement"""
        try:
            print_header("MARKET ORDER")
            
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            symbol = validate_symbol(symbol)
            
            side = input("Enter side (BUY/SELL): ").strip().upper()
            if side not in ['BUY', 'SELL']:
                print_error("Side must be BUY or SELL")
                return
            
            quantity = float(input("Enter quantity: ").strip())
            
            # Show current price
            current_price = self.get_current_price(symbol)
            if not current_price:
                return
            
            # Confirmation
            print_info(f"\nOrder Summary:")
            print(f"  Type: MARKET")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Quantity: {quantity}")
            print(f"  Estimated Price: {current_price}")
            
            if get_user_confirmation("Confirm and place order?"):
                self.order_executor.place_market_order(symbol, side, quantity)
            else:
                print_warning("Order cancelled")
        
        except ValueError as e:
            print_error(f"Invalid input: {str(e)}")
        except Exception as e:
            print_error(f"Error placing market order: {str(e)}")
    
    def handle_limit_order(self):
        """Handle limit order placement"""
        try:
            print_header("LIMIT ORDER")
            
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            symbol = validate_symbol(symbol)
            
            side = input("Enter side (BUY/SELL): ").strip().upper()
            if side not in ['BUY', 'SELL']:
                print_error("Side must be BUY or SELL")
                return
            
            quantity = float(input("Enter quantity: ").strip())
            price = float(input("Enter limit price: ").strip())
            
            # Show current price for reference
            current_price = self.get_current_price(symbol)
            
            # Confirmation
            print_info(f"\nOrder Summary:")
            print(f"  Type: LIMIT")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Quantity: {quantity}")
            print(f"  Limit Price: {price}")
            if current_price:
                print(f"  Current Price: {current_price}")
            
            if get_user_confirmation("Confirm and place order?"):
                self.order_executor.place_limit_order(symbol, side, quantity, price)
            else:
                print_warning("Order cancelled")
        
        except ValueError as e:
            print_error(f"Invalid input: {str(e)}")
        except Exception as e:
            print_error(f"Error placing limit order: {str(e)}")
    
    def handle_stop_limit_order(self):
        """Handle stop-limit order placement"""
        try:
            print_header("STOP-LIMIT ORDER")
            
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            symbol = validate_symbol(symbol)
            
            side = input("Enter side (BUY/SELL): ").strip().upper()
            if side not in ['BUY', 'SELL']:
                print_error("Side must be BUY or SELL")
                return
            
            quantity = float(input("Enter quantity: ").strip())
            stop_price = float(input("Enter stop price (trigger price): ").strip())
            limit_price = float(input("Enter limit price (execution price): ").strip())
            
            # Show current price for reference
            current_price = self.get_current_price(symbol)
            
            # Confirmation
            print_info(f"\nOrder Summary:")
            print(f"  Type: STOP-LIMIT")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Quantity: {quantity}")
            print(f"  Stop Price: {stop_price}")
            print(f"  Limit Price: {limit_price}")
            if current_price:
                print(f"  Current Price: {current_price}")
            
            if get_user_confirmation("Confirm and place order?"):
                self.order_executor.place_stop_limit_order(
                    symbol, side, quantity, stop_price, limit_price
                )
            else:
                print_warning("Order cancelled")
        
        except ValueError as e:
            print_error(f"Invalid input: {str(e)}")
        except Exception as e:
            print_error(f"Error placing stop-limit order: {str(e)}")
    
    def handle_oco_order(self):
        """Handle OCO order placement"""
        try:
            print_header("OCO ORDER (One-Cancels-Other)")
            print_info("This creates a limit order and a stop-limit order")
            
            symbol = input("\nEnter symbol (e.g., BTCUSDT): ").strip().upper()
            symbol = validate_symbol(symbol)
            
            side = input("Enter side (BUY/SELL): ").strip().upper()
            if side not in ['BUY', 'SELL']:
                print_error("Side must be BUY or SELL")
                return
            
            quantity = float(input("Enter total quantity: ").strip())
            price = float(input("Enter limit order price: ").strip())
            stop_price = float(input("Enter stop trigger price: ").strip())
            stop_limit_price = float(input("Enter stop-limit price: ").strip())
            
            # Show current price for reference
            current_price = self.get_current_price(symbol)
            
            # Confirmation
            print_info(f"\nOrder Summary:")
            print(f"  Type: OCO (One-Cancels-Other)")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Total Quantity: {quantity}")
            print(f"  Limit Price: {price}")
            print(f"  Stop Price: {stop_price}")
            print(f"  Stop-Limit Price: {stop_limit_price}")
            if current_price:
                print(f"  Current Price: {current_price}")
            
            if get_user_confirmation("Confirm and place order?"):
                self.order_executor.place_oco_order(
                    symbol, side, quantity, price, stop_price, stop_limit_price
                )
            else:
                print_warning("Order cancelled")
        
        except ValueError as e:
            print_error(f"Invalid input: {str(e)}")
        except Exception as e:
            print_error(f"Error placing OCO order: {str(e)}")
    
    def handle_twap_order(self):
        """Handle TWAP order placement"""
        try:
            print_header("TWAP ORDER (Time-Weighted Average Price)")
            print_info("Splits your order into multiple smaller orders over time")
            
            symbol = input("\nEnter symbol (e.g., BTCUSDT): ").strip().upper()
            symbol = validate_symbol(symbol)
            
            side = input("Enter side (BUY/SELL): ").strip().upper()
            if side not in ['BUY', 'SELL']:
                print_error("Side must be BUY or SELL")
                return
            
            total_quantity = float(input("Enter total quantity: ").strip())
            intervals = int(input("Enter number of intervals (orders): ").strip())
            duration = int(input("Enter total duration in seconds: ").strip())
            
            # Show current price for reference
            current_price = self.get_current_price(symbol)
            
            # Confirmation
            print_info(f"\nOrder Summary:")
            print(f"  Type: TWAP")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Total Quantity: {total_quantity}")
            print(f"  Intervals: {intervals}")
            print(f"  Duration: {duration}s ({duration/60:.1f} minutes)")
            print(f"  Quantity per order: {total_quantity/intervals}")
            print(f"  Time between orders: {duration/intervals:.1f}s")
            if current_price:
                print(f"  Current Price: {current_price}")
            
            if get_user_confirmation("Confirm and start TWAP execution?"):
                self.order_executor.place_twap_order(
                    symbol, side, total_quantity, intervals, duration
                )
            else:
                print_warning("Order cancelled")
        
        except ValueError as e:
            print_error(f"Invalid input: {str(e)}")
        except Exception as e:
            print_error(f"Error placing TWAP order: {str(e)}")
    
    def handle_order_status(self):
        """Handle order status check"""
        try:
            print_header("CHECK ORDER STATUS")
            
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            symbol = validate_symbol(symbol)
            
            order_id = int(input("Enter order ID: ").strip())
            
            self.order_executor.get_order_status(symbol, order_id)
        
        except ValueError as e:
            print_error(f"Invalid input: {str(e)}")
        except Exception as e:
            print_error(f"Error checking order status: {str(e)}")
    
    def handle_cancel_order(self):
        """Handle order cancellation"""
        try:
            print_header("CANCEL ORDER")
            
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            symbol = validate_symbol(symbol)
            
            order_id = int(input("Enter order ID: ").strip())
            
            if get_user_confirmation(f"Cancel order {order_id}?"):
                self.order_executor.cancel_order(symbol, order_id)
            else:
                print_warning("Cancellation aborted")
        
        except ValueError as e:
            print_error(f"Invalid input: {str(e)}")
        except Exception as e:
            print_error(f"Error cancelling order: {str(e)}")


def main():
    """Main entry point"""
    try:
        # Validate configuration
        Config.validate()
        
        # Display configuration
        Config.display()
        
        # Initialize bot
        bot = BasicBot(
            api_key=Config.API_KEY,
            api_secret=Config.API_SECRET,
            testnet=Config.TESTNET
        )
        
        # Run CLI
        bot.run_cli()
        
    except KeyboardInterrupt:
        print("\n")
        print_info("Bot stopped by user")
        sys.exit(0)
        
    except Exception as e:
        print_error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()