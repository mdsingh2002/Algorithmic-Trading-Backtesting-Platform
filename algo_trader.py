import time
import threading
import logging
import schedule
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ib_client import IBConnection
from trading_strategies import StrategyManager
from config import Config

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class AlgoTrader:
    """Main algorithmic trading engine"""
    
    def __init__(self):
        self.ib_connection = IBConnection()
        self.strategy_manager = StrategyManager()
        self.trading_enabled = False
        self.watchlist = []
        self.symbol_to_reqid = {}
        self.reqid_to_symbol = {}
        self.trade_history = []
        self.performance_metrics = {}
        
    def connect_to_ib(self) -> bool:
        """Connect to Interactive Brokers"""
        logger.info("Connecting to Interactive Brokers...")
        success = self.ib_connection.connect()
        
        if success:
            # Request account information
            self.ib_connection.request_account_summary()
            time.sleep(1)  # Give time for data to arrive
            
        return success
        
    def disconnect_from_ib(self):
        """Disconnect from Interactive Brokers"""
        self.ib_connection.disconnect()
        
    def add_to_watchlist(self, symbol: str) -> bool:
        """Add a symbol to the watchlist and request market data"""
        if symbol in self.watchlist:
            logger.warning(f"Symbol {symbol} already in watchlist")
            return False
            
        try:
            reqId = self.ib_connection.request_market_data(symbol)
            if reqId:
                self.watchlist.append(symbol)
                self.symbol_to_reqid[symbol] = reqId
                self.reqid_to_symbol[reqId] = symbol
                logger.info(f"Added {symbol} to watchlist with reqId {reqId}")
                return True
            else:
                logger.error(f"Failed to request market data for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding {symbol} to watchlist: {e}")
            return False
            
    def remove_from_watchlist(self, symbol: str) -> bool:
        """Remove a symbol from the watchlist"""
        if symbol not in self.watchlist:
            logger.warning(f"Symbol {symbol} not in watchlist")
            return False
            
        try:
            reqId = self.symbol_to_reqid.get(symbol)
            if reqId:
                # Cancel market data subscription
                self.ib_connection.client.cancelMktData(reqId)
                
            self.watchlist.remove(symbol)
            if symbol in self.symbol_to_reqid:
                del self.symbol_to_reqid[symbol]
            if reqId in self.reqid_to_symbol:
                del self.reqid_to_symbol[reqId]
                
            logger.info(f"Removed {symbol} from watchlist")
            return True
            
        except Exception as e:
            logger.error(f"Error removing {symbol} from watchlist: {e}")
            return False
            
    def get_market_data(self) -> Dict:
        """Get current market data for all symbols in watchlist"""
        market_data = {}
        for symbol in self.watchlist:
            reqId = self.symbol_to_reqid.get(symbol)
            if reqId:
                data = self.ib_connection.get_market_data(reqId)
                if data:
                    market_data[symbol] = data
                    
        return market_data
        
    def execute_trade(self, symbol: str, action: str, quantity: int, order_type: str = "MKT") -> Optional[int]:
        """Execute a trade"""
        try:
            orderId = self.ib_connection.place_order(symbol, action, quantity, order_type)
            
            if orderId:
                trade_record = {
                    'timestamp': datetime.now(),
                    'order_id': orderId,
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'order_type': order_type,
                    'status': 'PENDING'
                }
                self.trade_history.append(trade_record)
                logger.info(f"Executed {action} order for {quantity} {symbol}")
                
            return orderId
            
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return None
            
    def run_strategy(self):
        """Run the active trading strategy"""
        if not self.trading_enabled or not self.ib_connection.client.connected:
            return
            
        try:
            # Get current market data
            market_data = self.get_market_data()
            if not market_data:
                logger.warning("No market data available")
                return
                
            # Get account information
            account_info = self.ib_connection.get_account_info()
            account_value = float(account_info.get('NetLiquidation', 100000))  # Default to 100k if not available
            
            # Get current positions
            positions = self.ib_connection.get_positions()
            
            # Get active strategy
            strategy = self.strategy_manager.get_active_strategy()
            
            # Process each symbol in watchlist
            for symbol in self.watchlist:
                if symbol not in market_data:
                    continue
                    
                current_position = positions.get(symbol, {}).get('position', 0)
                
                # Check for buy signal
                if strategy.should_buy(symbol, market_data) and current_position == 0:
                    quantity = strategy.get_position_size(symbol, account_value)
                    if quantity > 0:
                        self.execute_trade(symbol, "BUY", quantity)
                        
                # Check for sell signal
                elif strategy.should_sell(symbol, market_data) and current_position > 0:
                    self.execute_trade(symbol, "SELL", current_position)
                    
        except Exception as e:
            logger.error(f"Error running strategy: {e}")
            
    def start_trading(self):
        """Start automated trading"""
        if not self.ib_connection.client.connected:
            logger.error("Not connected to Interactive Brokers")
            return False
            
        self.trading_enabled = True
        logger.info("Automated trading started")
        
        # Schedule strategy execution every minute
        schedule.every().minute.do(self.run_strategy)
        
        # Start the scheduler in a separate thread
        def run_scheduler():
            while self.trading_enabled:
                schedule.run_pending()
                time.sleep(1)
                
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        return True
        
    def stop_trading(self):
        """Stop automated trading"""
        self.trading_enabled = False
        schedule.clear()
        logger.info("Automated trading stopped")
        
    def set_strategy(self, strategy_name: str):
        """Set the active trading strategy"""
        self.strategy_manager.set_active_strategy(strategy_name)
        
    def get_trade_history(self) -> List[Dict]:
        """Get trade history"""
        return self.trade_history.copy()
        
    def get_positions(self) -> Dict:
        """Get current positions"""
        return self.ib_connection.get_positions()
        
    def get_account_info(self) -> Dict:
        """Get account information"""
        return self.ib_connection.get_account_info()
        
    def get_performance_metrics(self) -> Dict:
        """Calculate and return performance metrics"""
        if not self.trade_history:
            return {}
            
        total_trades = len(self.trade_history)
        completed_trades = [trade for trade in self.trade_history if trade.get('status') == 'FILLED']
        
        metrics = {
            'total_trades': total_trades,
            'completed_trades': len(completed_trades),
            'completion_rate': len(completed_trades) / total_trades if total_trades > 0 else 0,
            'last_trade': self.trade_history[-1] if self.trade_history else None
        }
        
        return metrics
        
    def get_status(self) -> Dict:
        """Get current system status"""
        return {
            'connected': self.ib_connection.client.connected,
            'trading_enabled': self.trading_enabled,
            'watchlist': self.watchlist,
            'active_strategy': self.strategy_manager.active_strategy,
            'available_strategies': list(self.strategy_manager.strategies.keys())
        }
