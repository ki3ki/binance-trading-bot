"""
Order execution module for Binance Trading Bot
Handles all order types: Market, Limit, Stop-Limit, OCO, and TWAP
"""

import time
from binance.exceptions import BinanceAPIException
from utils import (
    print_success, print_error, print_info, print_warning,
    format_order_details, validate_quantity, validate_price
)


class OrderExecutor:
    """Handles all order execution logic"""
    
    def __init__(self, client, logger):
        """
        Initialize OrderExecutor
        
        Args:
            client: Binance client instance
            logger: Logger instance
        """
        self.client = client
        self.logger = logger
    
    def place_market_order(self, symbol, side, quantity):
        """
        Place a market order
        
        Args:
            symbol (str): Trading pair (e.g., 'BTCUSDT')
            side (str): 'BUY' or 'SELL'
            quantity (float): Order quantity
        
        Returns:
            dict: Order response or None if failed
        """
        try:
            # Validate inputs
            quantity = validate_quantity(quantity)
            side = side.upper()
            
            self.logger.info(f"Placing MARKET {side} order: {quantity} {symbol}")
            print_info(f"Placing MARKET {side} order: {quantity} {symbol}")
            
            # Place order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            self.logger.info(f"Market order placed successfully: {order['orderId']}")
            print_success(f"Market order placed successfully!")
            print("\n" + format_order_details(order))
            
            return order
            
        except BinanceAPIException as e:
            error_msg = f"Binance API Error: {e.message} (Code: {e.code})"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error placing market order: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
    
    def place_limit_order(self, symbol, side, quantity, price):
        """
        Place a limit order
        
        Args:
            symbol (str): Trading pair
            side (str): 'BUY' or 'SELL'
            quantity (float): Order quantity
            price (float): Limit price
        
        Returns:
            dict: Order response or None if failed
        """
        try:
            # Validate inputs
            quantity = validate_quantity(quantity)
            price = validate_price(price)
            side = side.upper()
            
            self.logger.info(f"Placing LIMIT {side} order: {quantity} {symbol} @ {price}")
            print_info(f"Placing LIMIT {side} order: {quantity} {symbol} @ {price}")
            
            # Place order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                timeInForce='GTC',  # Good Till Canceled
                quantity=quantity,
                price=price
            )
            
            self.logger.info(f"Limit order placed successfully: {order['orderId']}")
            print_success(f"Limit order placed successfully!")
            print("\n" + format_order_details(order))
            
            return order
            
        except BinanceAPIException as e:
            error_msg = f"Binance API Error: {e.message} (Code: {e.code})"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error placing limit order: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
    
    def place_stop_limit_order(self, symbol, side, quantity, stop_price, limit_price):
        """
        Place a stop-limit order
        
        Args:
            symbol (str): Trading pair
            side (str): 'BUY' or 'SELL'
            quantity (float): Order quantity
            stop_price (float): Stop trigger price
            limit_price (float): Limit price after stop is triggered
        
        Returns:
            dict: Order response or None if failed
        """
        try:
            # Validate inputs
            quantity = validate_quantity(quantity)
            stop_price = validate_price(stop_price)
            limit_price = validate_price(limit_price)
            side = side.upper()
            
            self.logger.info(
                f"Placing STOP_LIMIT {side} order: {quantity} {symbol} | "
                f"Stop: {stop_price} | Limit: {limit_price}"
            )
            print_info(
                f"Placing STOP_LIMIT {side} order: {quantity} {symbol}\n"
                f"  Stop Price: {stop_price} | Limit Price: {limit_price}"
            )
            
            # Place order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                timeInForce='GTC',
                quantity=quantity,
                price=limit_price,
                stopPrice=stop_price
            )
            
            self.logger.info(f"Stop-limit order placed successfully: {order['orderId']}")
            print_success(f"Stop-limit order placed successfully!")
            print("\n" + format_order_details(order))
            
            return order
            
        except BinanceAPIException as e:
            error_msg = f"Binance API Error: {e.message} (Code: {e.code})"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error placing stop-limit order: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
    
    def place_oco_order(self, symbol, side, quantity, price, stop_price, stop_limit_price):
        """
        Place an OCO (One-Cancels-Other) order
        This creates two orders: a limit order and a stop-limit order
        
        Args:
            symbol (str): Trading pair
            side (str): 'BUY' or 'SELL'
            quantity (float): Order quantity
            price (float): Limit order price
            stop_price (float): Stop trigger price
            stop_limit_price (float): Stop-limit order price
        
        Returns:
            dict: Combined order response or None if failed
        """
        try:
            # Validate inputs
            quantity = validate_quantity(quantity)
            price = validate_price(price)
            stop_price = validate_price(stop_price)
            stop_limit_price = validate_price(stop_limit_price)
            side = side.upper()
            
            self.logger.info(
                f"Placing OCO {side} order: {quantity} {symbol} | "
                f"Limit: {price} | Stop: {stop_price} | Stop-Limit: {stop_limit_price}"
            )
            print_info(
                f"Placing OCO {side} order: {quantity} {symbol}\n"
                f"  Limit Price: {price}\n"
                f"  Stop Price: {stop_price}\n"
                f"  Stop-Limit Price: {stop_limit_price}"
            )
            
            # Note: Binance Futures doesn't support native OCO orders
            # We'll place both orders separately and link them logically
            print_warning("Note: Placing two separate orders (Limit + Stop-Limit)")
            
            # Place limit order
            limit_order = self.place_limit_order(symbol, side, quantity/2, price)
            
            if not limit_order:
                return None
            
            # Place stop-limit order
            stop_order = self.place_stop_limit_order(
                symbol, side, quantity/2, stop_price, stop_limit_price
            )
            
            if not stop_order:
                print_warning("Stop-limit order failed. Limit order was placed successfully.")
                return limit_order
            
            # Return combined result
            result = {
                'oco_type': 'MANUAL_OCO',
                'limit_order': limit_order,
                'stop_order': stop_order
            }
            
            self.logger.info("OCO orders placed successfully")
            print_success("OCO orders placed successfully!")
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error placing OCO order: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
    
    def place_twap_order(self, symbol, side, total_quantity, intervals, duration):
        """
        Place a TWAP (Time-Weighted Average Price) order
        Splits order into multiple market orders over time
        
        Args:
            symbol (str): Trading pair
            side (str): 'BUY' or 'SELL'
            total_quantity (float): Total quantity to trade
            intervals (int): Number of intervals to split the order
            duration (int): Total duration in seconds
        
        Returns:
            list: List of order responses
        """
        try:
            # Validate inputs
            total_quantity = validate_quantity(total_quantity)
            side = side.upper()
            
            if intervals <= 0:
                raise ValueError("Intervals must be greater than 0")
            if duration <= 0:
                raise ValueError("Duration must be greater than 0")
            
            quantity_per_order = total_quantity / intervals
            wait_time = duration / intervals
            
            self.logger.info(
                f"Starting TWAP {side} order: {total_quantity} {symbol} | "
                f"Intervals: {intervals} | Duration: {duration}s"
            )
            print_info(
                f"Starting TWAP {side} order:\n"
                f"  Total Quantity: {total_quantity} {symbol}\n"
                f"  Intervals: {intervals}\n"
                f"  Duration: {duration}s ({duration/60:.1f} minutes)\n"
                f"  Quantity per order: {quantity_per_order}\n"
                f"  Wait between orders: {wait_time:.1f}s"
            )
            
            orders = []
            
            for i in range(intervals):
                print_info(f"\n[{i+1}/{intervals}] Placing order...")
                
                order = self.place_market_order(symbol, side, quantity_per_order)
                
                if order:
                    orders.append(order)
                else:
                    print_error(f"Order {i+1} failed. Stopping TWAP execution.")
                    break
                
                # Wait before next order (except for last order)
                if i < intervals - 1:
                    print_info(f"Waiting {wait_time:.1f}s before next order...")
                    time.sleep(wait_time)
            
            self.logger.info(f"TWAP order completed: {len(orders)}/{intervals} orders executed")
            print_success(f"\nTWAP order completed: {len(orders)}/{intervals} orders executed")
            
            return orders
            
        except Exception as e:
            error_msg = f"Unexpected error in TWAP order: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
    
    def get_order_status(self, symbol, order_id):
        """
        Get status of an existing order
        
        Args:
            symbol (str): Trading pair
            order_id (int): Order ID
        
        Returns:
            dict: Order details or None if failed
        """
        try:
            order = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            
            print("\n" + format_order_details(order))
            return order
            
        except BinanceAPIException as e:
            error_msg = f"Binance API Error: {e.message} (Code: {e.code})"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error getting order status: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
    
    def cancel_order(self, symbol, order_id):
        """
        Cancel an existing order
        
        Args:
            symbol (str): Trading pair
            order_id (int): Order ID
        
        Returns:
            dict: Cancellation response or None if failed
        """
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            
            self.logger.info(f"Order {order_id} cancelled successfully")
            print_success(f"Order {order_id} cancelled successfully")
            
            return result
            
        except BinanceAPIException as e:
            error_msg = f"Binance API Error: {e.message} (Code: {e.code})"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error cancelling order: {str(e)}"
            self.logger.error(error_msg)
            print_error(error_msg)
            return None