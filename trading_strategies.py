import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from config import Config

logger = logging.getLogger(__name__)

class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.positions = {}
        self.trade_history = []
        
    def calculate_signals(self, market_data: Dict) -> Dict:
        """Calculate trading signals based on market data"""
        raise NotImplementedError
        
    def should_buy(self, symbol: str, market_data: Dict) -> bool:
        """Determine if we should buy the symbol"""
        raise NotImplementedError
        
    def should_sell(self, symbol: str, market_data: Dict) -> bool:
        """Determine if we should sell the symbol"""
        raise NotImplementedError
        
    def get_position_size(self, symbol: str, account_value: float) -> int:
        """Calculate position size based on risk management rules"""
        raise NotImplementedError

class MovingAverageCrossover(TradingStrategy):
    """Moving Average Crossover Strategy"""
    
    def __init__(self, short_window: int = 10, long_window: int = 30):
        super().__init__("Moving Average Crossover")
        self.short_window = short_window
        self.long_window = long_window
        self.price_history = {}
        
    def update_price_history(self, symbol: str, price: float):
        """Update price history for a symbol"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(price)
        
        # Keep only the last long_window + 1 prices
        if len(self.price_history[symbol]) > self.long_window + 1:
            self.price_history[symbol] = self.price_history[symbol][-self.long_window-1:]
            
    def calculate_signals(self, market_data: Dict) -> Dict:
        signals = {}
        
        for reqId, data in market_data.items():
            if 'price' in data and data['price'] > 0:
                # This is a simplified version - in practice you'd get symbol from reqId mapping
                symbol = f"SYMBOL_{reqId}"  # You'd need to maintain a reqId to symbol mapping
                price = data['price']
                
                self.update_price_history(symbol, price)
                
                if len(self.price_history[symbol]) >= self.long_window:
                    prices = np.array(self.price_history[symbol])
                    short_ma = np.mean(prices[-self.short_window:])
                    long_ma = np.mean(prices[-self.long_window:])
                    
                    signals[symbol] = {
                        'short_ma': short_ma,
                        'long_ma': long_ma,
                        'signal': 'BUY' if short_ma > long_ma else 'SELL' if short_ma < long_ma else 'HOLD',
                        'price': price
                    }
                    
        return signals
        
    def should_buy(self, symbol: str, market_data: Dict) -> bool:
        signals = self.calculate_signals(market_data)
        return symbol in signals and signals[symbol]['signal'] == 'BUY'
        
    def should_sell(self, symbol: str, market_data: Dict) -> bool:
        signals = self.calculate_signals(market_data)
        return symbol in signals and signals[symbol]['signal'] == 'SELL'
        
    def get_position_size(self, symbol: str, account_value: float) -> int:
        # Simple position sizing: 5% of account value per position
        return max(1, int(account_value * 0.05 / 100))  # Assuming $100 per share average

class MeanReversion(TradingStrategy):
    """Mean Reversion Strategy using Bollinger Bands"""
    
    def __init__(self, window: int = 20, std_dev: float = 2.0):
        super().__init__("Mean Reversion")
        self.window = window
        self.std_dev = std_dev
        self.price_history = {}
        
    def update_price_history(self, symbol: str, price: float):
        """Update price history for a symbol"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(price)
        
        # Keep only the last window + 1 prices
        if len(self.price_history[symbol]) > self.window + 1:
            self.price_history[symbol] = self.price_history[symbol][-self.window-1:]
            
    def calculate_bollinger_bands(self, prices: List[float]) -> Dict:
        """Calculate Bollinger Bands"""
        if len(prices) < self.window:
            return {}
            
        prices_array = np.array(prices[-self.window:])
        sma = np.mean(prices_array)
        std = np.std(prices_array)
        
        return {
            'upper_band': sma + (self.std_dev * std),
            'lower_band': sma - (self.std_dev * std),
            'middle_band': sma,
            'std': std
        }
        
    def calculate_signals(self, market_data: Dict) -> Dict:
        signals = {}
        
        for reqId, data in market_data.items():
            if 'price' in data and data['price'] > 0:
                symbol = f"SYMBOL_{reqId}"
                price = data['price']
                
                self.update_price_history(symbol, price)
                
                if len(self.price_history[symbol]) >= self.window:
                    bands = self.calculate_bollinger_bands(self.price_history[symbol])
                    
                    if bands:
                        signal = 'HOLD'
                        if price <= bands['lower_band']:
                            signal = 'BUY'
                        elif price >= bands['upper_band']:
                            signal = 'SELL'
                            
                        signals[symbol] = {
                            'price': price,
                            'upper_band': bands['upper_band'],
                            'lower_band': bands['lower_band'],
                            'middle_band': bands['middle_band'],
                            'signal': signal
                        }
                        
        return signals
        
    def should_buy(self, symbol: str, market_data: Dict) -> bool:
        signals = self.calculate_signals(market_data)
        return symbol in signals and signals[symbol]['signal'] == 'BUY'
        
    def should_sell(self, symbol: str, market_data: Dict) -> bool:
        signals = self.calculate_signals(market_data)
        return symbol in signals and signals[symbol]['signal'] == 'SELL'
        
    def get_position_size(self, symbol: str, account_value: float) -> int:
        # Conservative position sizing for mean reversion
        return max(1, int(account_value * 0.03 / 100))

class MomentumStrategy(TradingStrategy):
    """Momentum Strategy based on price momentum"""
    
    def __init__(self, lookback_period: int = 10, momentum_threshold: float = 0.02):
        super().__init__("Momentum Strategy")
        self.lookback_period = lookback_period
        self.momentum_threshold = momentum_threshold
        self.price_history = {}
        
    def update_price_history(self, symbol: str, price: float):
        """Update price history for a symbol"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(price)
        
        # Keep only the last lookback_period + 1 prices
        if len(self.price_history[symbol]) > self.lookback_period + 1:
            self.price_history[symbol] = self.price_history[symbol][-self.lookback_period-1:]
            
    def calculate_momentum(self, prices: List[float]) -> float:
        """Calculate price momentum"""
        if len(prices) < 2:
            return 0.0
            
        current_price = prices[-1]
        past_price = prices[-min(len(prices), self.lookback_period)]
        
        if past_price == 0:
            return 0.0
            
        return (current_price - past_price) / past_price
        
    def calculate_signals(self, market_data: Dict) -> Dict:
        signals = {}
        
        for reqId, data in market_data.items():
            if 'price' in data and data['price'] > 0:
                symbol = f"SYMBOL_{reqId}"
                price = data['price']
                
                self.update_price_history(symbol, price)
                
                if len(self.price_history[symbol]) >= 2:
                    momentum = self.calculate_momentum(self.price_history[symbol])
                    
                    signal = 'HOLD'
                    if momentum > self.momentum_threshold:
                        signal = 'BUY'
                    elif momentum < -self.momentum_threshold:
                        signal = 'SELL'
                        
                    signals[symbol] = {
                        'price': price,
                        'momentum': momentum,
                        'signal': signal
                    }
                    
        return signals
        
    def should_buy(self, symbol: str, market_data: Dict) -> bool:
        signals = self.calculate_signals(market_data)
        return symbol in signals and signals[symbol]['signal'] == 'BUY'
        
    def should_sell(self, symbol: str, market_data: Dict) -> bool:
        signals = self.calculate_signals(market_data)
        return symbol in signals and signals[symbol]['signal'] == 'SELL'
        
    def get_position_size(self, symbol: str, account_value: float) -> int:
        # Aggressive position sizing for momentum strategy
        return max(1, int(account_value * 0.07 / 100))

class StrategyManager:
    """Manages multiple trading strategies"""
    
    def __init__(self):
        self.strategies = {
            'ma_crossover': MovingAverageCrossover(),
            'mean_reversion': MeanReversion(),
            'momentum': MomentumStrategy()
        }
        self.active_strategy = 'ma_crossover'
        
    def get_strategy(self, name: str) -> Optional[TradingStrategy]:
        """Get a strategy by name"""
        return self.strategies.get(name)
        
    def set_active_strategy(self, name: str):
        """Set the active strategy"""
        if name in self.strategies:
            self.active_strategy = name
            logger.info(f"Active strategy set to: {name}")
        else:
            logger.error(f"Strategy {name} not found")
            
    def get_active_strategy(self) -> TradingStrategy:
        """Get the currently active strategy"""
        return self.strategies[self.active_strategy]
        
    def get_all_strategies(self) -> Dict[str, TradingStrategy]:
        """Get all available strategies"""
        return self.strategies.copy()
