import pandas as pd
import numpy as np
import yfinance as yf
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class BacktestEngine:
    """Backtesting engine using pandas and yfinance"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.portfolio_values = []
        self.daily_returns = []
        
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                logger.error(f"No data found for {symbol}")
                return pd.DataFrame()
                
            # Calculate technical indicators
            data['SMA_10'] = data['Close'].rolling(window=10).mean()
            data['SMA_30'] = data['Close'].rolling(window=30).mean()
            data['EMA_12'] = data['Close'].ewm(span=12).mean()
            data['EMA_26'] = data['Close'].ewm(span=26).mean()
            data['MACD'] = data['EMA_12'] - data['EMA_26']
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            data['RSI'] = self.calculate_rsi(data['Close'])
            data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = self.calculate_bollinger_bands(data['Close'])
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    def execute_trade(self, symbol: str, action: str, quantity: int, price: float, date: datetime):
        """Execute a trade and update portfolio"""
        if action == 'BUY':
            cost = quantity * price
            if cost <= self.current_capital:
                if symbol in self.positions:
                    # Average down
                    total_quantity = self.positions[symbol]['quantity'] + quantity
                    total_cost = self.positions[symbol]['cost'] + cost
                    self.positions[symbol] = {
                        'quantity': total_quantity,
                        'avg_price': total_cost / total_quantity,
                        'cost': total_cost
                    }
                else:
                    self.positions[symbol] = {
                        'quantity': quantity,
                        'avg_price': price,
                        'cost': cost
                    }
                self.current_capital -= cost
                
                self.trade_history.append({
                    'date': date,
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'price': price,
                    'cost': cost,
                    'portfolio_value': self.get_portfolio_value(price, symbol)
                })
                
        elif action == 'SELL' and symbol in self.positions:
            quantity_to_sell = min(quantity, self.positions[symbol]['quantity'])
            revenue = quantity_to_sell * price
            
            self.positions[symbol]['quantity'] -= quantity_to_sell
            self.positions[symbol]['cost'] -= (quantity_to_sell * self.positions[symbol]['avg_price'])
            
            if self.positions[symbol]['quantity'] <= 0:
                del self.positions[symbol]
                
            self.current_capital += revenue
            
            self.trade_history.append({
                'date': date,
                'symbol': symbol,
                'action': action,
                'quantity': quantity_to_sell,
                'price': price,
                'revenue': revenue,
                'portfolio_value': self.get_portfolio_value(price, symbol)
            })
    
    def get_portfolio_value(self, current_price: float, symbol: str) -> float:
        """Calculate current portfolio value"""
        portfolio_value = self.current_capital
        
        for pos_symbol, position in self.positions.items():
            if pos_symbol == symbol:
                portfolio_value += position['quantity'] * current_price
            else:
                # For other positions, use their last known price
                portfolio_value += position['quantity'] * position['avg_price']
                
        return portfolio_value
    
    def run_backtest(self, strategy, symbol: str, start_date: str, end_date: str, 
                    initial_capital: float = 100000) -> Dict:
        """Run backtest for a given strategy"""
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.portfolio_values = []
        
        # Get historical data
        data = self.get_historical_data(symbol, start_date, end_date)
        if data.empty:
            return {'error': f'No data available for {symbol}'}
        
        # Run strategy on each day
        for date, row in data.iterrows():
            if pd.isna(row['Close']):
                continue
                
            # Generate signals
            signals = strategy.generate_signals(row)
            
            # Execute trades based on signals
            for signal in signals:
                if signal['action'] == 'BUY' and signal['symbol'] == symbol:
                    quantity = self.calculate_position_size(signal['price'])
                    if quantity > 0:
                        self.execute_trade(symbol, 'BUY', quantity, signal['price'], date)
                        
                elif signal['action'] == 'SELL' and signal['symbol'] == symbol:
                    if symbol in self.positions:
                        self.execute_trade(symbol, 'SELL', self.positions[symbol]['quantity'], 
                                         signal['price'], date)
            
            # Record portfolio value
            portfolio_value = self.get_portfolio_value(row['Close'], symbol)
            self.portfolio_values.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'price': row['Close']
            })
        
        return self.calculate_performance_metrics(data)
    
    def calculate_position_size(self, price: float) -> int:
        """Calculate position size based on risk management"""
        max_position_value = self.current_capital * 0.2  # 20% max per position for more aggressive trading
        return int(max_position_value / price) if price > 0 else 0
    
    def calculate_performance_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate performance metrics"""
        if not self.portfolio_values:
            return {'error': 'No portfolio values recorded'}
        
        df_values = pd.DataFrame(self.portfolio_values)
        df_values.set_index('date', inplace=True)
        
        # Calculate returns
        df_values['returns'] = df_values['portfolio_value'].pct_change()
        df_values['cumulative_returns'] = (1 + df_values['returns']).cumprod()
        
        # Calculate metrics
        total_return = (df_values['portfolio_value'].iloc[-1] - self.initial_capital) / self.initial_capital
        annualized_return = self.calculate_annualized_return(df_values)
        sharpe_ratio = self.calculate_sharpe_ratio(df_values['returns'])
        max_drawdown = self.calculate_max_drawdown(df_values['portfolio_value'])
        
        return {
            'total_return': float(total_return) if not pd.isna(total_return) else 0.0,
            'annualized_return': float(annualized_return) if not pd.isna(annualized_return) else 0.0,
            'sharpe_ratio': float(sharpe_ratio) if not pd.isna(sharpe_ratio) else 0.0,
            'max_drawdown': float(max_drawdown) if not pd.isna(max_drawdown) else 0.0,
            'final_portfolio_value': float(df_values['portfolio_value'].iloc[-1]) if not pd.isna(df_values['portfolio_value'].iloc[-1]) else self.initial_capital,
            'initial_capital': float(self.initial_capital),
            'total_trades': int(len(self.trade_history)),
            'portfolio_values': df_values,
            'trade_history': self.trade_history
        }
    
    def calculate_annualized_return(self, df_values: pd.DataFrame) -> float:
        """Calculate annualized return"""
        if len(df_values) < 2:
            return 0.0
        
        days = (df_values.index[-1] - df_values.index[0]).days
        if days == 0:
            return 0.0
        
        total_return = (df_values['portfolio_value'].iloc[-1] / self.initial_capital) - 1
        annualized_return = (1 + total_return) ** (365 / days) - 1
        return annualized_return
    
    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        returns = returns.dropna()
        if len(returns) == 0:
            return 0.0
        
        return returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0.0
    
    def calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """Calculate maximum drawdown"""
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values - peak) / peak
        return drawdown.min()
    
    def plot_results(self, results: Dict, symbol: str):
        """Plot backtest results"""
        if 'error' in results:
            print(f"Error: {results['error']}")
            return
        
        df_values = results['portfolio_values']
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Portfolio Value', 'Daily Returns', 'Cumulative Returns'),
            vertical_spacing=0.1
        )
        
        # Portfolio value
        fig.add_trace(
            go.Scatter(x=df_values.index, y=df_values['portfolio_value'],
                      mode='lines', name='Portfolio Value'),
            row=1, col=1
        )
        
        # Daily returns
        fig.add_trace(
            go.Scatter(x=df_values.index, y=df_values['returns'],
                      mode='lines', name='Daily Returns'),
            row=2, col=1
        )
        
        # Cumulative returns
        fig.add_trace(
            go.Scatter(x=df_values.index, y=df_values['cumulative_returns'],
                      mode='lines', name='Cumulative Returns'),
            row=3, col=1
        )
        
        fig.update_layout(
            title=f'Backtest Results for {symbol}',
            height=800,
            showlegend=True
        )
        
        fig.show()
        
        # Print summary
        print(f"\n=== Backtest Results for {symbol} ===")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Portfolio Value: ${results['final_portfolio_value']:,.2f}")
        print(f"Total Return: {results['total_return']:.2%}")
        print(f"Annualized Return: {results['annualized_return']:.2%}")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Maximum Drawdown: {results['max_drawdown']:.2%}")
        print(f"Total Trades: {results['total_trades']}")

class PandasStrategy:
    """Base class for pandas-based trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
    
    def generate_signals(self, data: pd.Series) -> List[Dict]:
        """Generate trading signals based on current data"""
        raise NotImplementedError

class MovingAverageCrossoverStrategy(PandasStrategy):
    """Moving Average Crossover Strategy using pandas"""
    
    def __init__(self, short_window: int = 5, long_window: int = 20, symbol: str = 'AAPL'):
        super().__init__("Moving Average Crossover")
        self.short_window = short_window
        self.long_window = long_window
        self.symbol = symbol
        self.last_signal = None
    
    def generate_signals(self, data: pd.Series) -> List[Dict]:
        signals = []
        
        if pd.isna(data['SMA_10']) or pd.isna(data['SMA_30']):
            return signals
        
        current_signal = 'BUY' if data['SMA_10'] > data['SMA_30'] else 'SELL'
        
        # Generate signal more frequently (every day if conditions change)
        if self.last_signal != current_signal:
            signals.append({
                'symbol': self.symbol,
                'action': current_signal,
                'price': data['Close'],
                'short_ma': data['SMA_10'],
                'long_ma': data['SMA_30']
            })
            self.last_signal = current_signal
        
        return signals

class ScalpingStrategy(PandasStrategy):
    """Scalping Strategy - Very short-term trades based on price momentum"""
    
    def __init__(self, symbol: str = 'AAPL'):
        super().__init__("Scalping Strategy")
        self.symbol = symbol
        self.last_price = None
        self.trade_count = 0
    
    def generate_signals(self, data: pd.Series) -> List[Dict]:
        signals = []
        
        if self.last_price is None:
            self.last_price = data['Close']
            return signals
        
        # Calculate price change percentage
        price_change = (data['Close'] - self.last_price) / self.last_price
        
        # Generate signals based on small price movements (scalping)
        if price_change > 0.005:  # 0.5% increase
            signals.append({
                'symbol': self.symbol,
                'action': 'BUY',
                'price': data['Close'],
                'price_change': price_change
            })
        elif price_change < -0.005:  # 0.5% decrease
            signals.append({
                'symbol': self.symbol,
                'action': 'SELL',
                'price': data['Close'],
                'price_change': price_change
            })
        
        self.last_price = data['Close']
        return signals

class MomentumStrategy(PandasStrategy):
    """Momentum Strategy - Based on price momentum and volume"""
    
    def __init__(self, symbol: str = 'AAPL'):
        super().__init__("Momentum Strategy")
        self.symbol = symbol
        self.last_signal = None
    
    def generate_signals(self, data: pd.Series) -> List[Dict]:
        signals = []
        
        # Calculate momentum indicators
        if 'Volume' in data and not pd.isna(data['Volume']):
            # Simple momentum based on price and volume
            price_momentum = (data['Close'] - data['Open']) / data['Open']
            
            # For volume ratio, we need to handle the rolling calculation differently
            # Since we're processing one row at a time, we'll use a simpler approach
            volume_ratio = 1.0  # Default value
            
            if price_momentum > 0.02:  # Strong upward momentum
                signals.append({
                    'symbol': self.symbol,
                    'action': 'BUY',
                    'price': data['Close'],
                    'momentum': price_momentum,
                    'volume_ratio': volume_ratio
                })
            elif price_momentum < -0.02:  # Strong downward momentum
                signals.append({
                    'symbol': self.symbol,
                    'action': 'SELL',
                    'price': data['Close'],
                    'momentum': price_momentum,
                    'volume_ratio': volume_ratio
                })
        
        return signals

class MeanReversionStrategy(PandasStrategy):
    """Mean Reversion Strategy - Trade against extreme movements"""
    
    def __init__(self, symbol: str = 'AAPL'):
        super().__init__("Mean Reversion Strategy")
        self.symbol = symbol
        self.last_signal = None
    
    def generate_signals(self, data: pd.Series) -> List[Dict]:
        signals = []
        
        # Calculate mean reversion indicators
        if not pd.isna(data['SMA_30']):
            deviation = (data['Close'] - data['SMA_30']) / data['SMA_30']
            
            # Buy when price is significantly below mean (oversold)
            if deviation < -0.05:  # 5% below mean
                signals.append({
                    'symbol': self.symbol,
                    'action': 'BUY',
                    'price': data['Close'],
                    'deviation': deviation
                })
            # Sell when price is significantly above mean (overbought)
            elif deviation > 0.05:  # 5% above mean
                signals.append({
                    'symbol': self.symbol,
                    'action': 'SELL',
                    'price': data['Close'],
                    'deviation': deviation
                })
        
        return signals

class BollingerBandsStrategy(PandasStrategy):
    """Bollinger Bands Mean Reversion Strategy"""
    
    def __init__(self, window: int = 10, std_dev: float = 1.5, symbol: str = 'AAPL'):
        super().__init__("Bollinger Bands")
        self.window = window
        self.std_dev = std_dev
        self.symbol = symbol
        self.last_signal = None
    
    def generate_signals(self, data: pd.Series) -> List[Dict]:
        signals = []
        
        if (pd.isna(data['BB_Upper']) or pd.isna(data['BB_Lower']) or 
            pd.isna(data['BB_Middle'])):
            return signals
        
        # More aggressive Bollinger Bands with tighter bands
        bb_position = (data['Close'] - data['BB_Lower']) / (data['BB_Upper'] - data['BB_Lower'])
        
        # Generate signals more frequently
        if bb_position <= 0.1:  # Near lower band
            signals.append({
                'symbol': self.symbol,
                'action': 'BUY',
                'price': data['Close'],
                'upper_band': data['BB_Upper'],
                'lower_band': data['BB_Lower'],
                'middle_band': data['BB_Middle'],
                'bb_position': bb_position
            })
        elif bb_position >= 0.9:  # Near upper band
            signals.append({
                'symbol': self.symbol,
                'action': 'SELL',
                'price': data['Close'],
                'upper_band': data['BB_Upper'],
                'lower_band': data['BB_Lower'],
                'middle_band': data['BB_Middle'],
                'bb_position': bb_position
            })
        
        return signals

class RSIStrategy(PandasStrategy):
    """RSI Strategy - More aggressive with frequent signals"""
    
    def __init__(self, oversold: int = 40, overbought: int = 60, symbol: str = 'AAPL'):
        super().__init__("RSI Strategy")
        self.oversold = oversold
        self.overbought = overbought
        self.symbol = symbol
        self.last_signal = None
    
    def generate_signals(self, data: pd.Series) -> List[Dict]:
        signals = []
        
        if pd.isna(data['RSI']):
            return signals
        
        # More aggressive RSI levels for frequent trading
        if data['RSI'] <= self.oversold:
            signals.append({
                'symbol': self.symbol,
                'action': 'BUY',
                'price': data['Close'],
                'rsi': data['RSI']
            })
        elif data['RSI'] >= self.overbought:
            signals.append({
                'symbol': self.symbol,
                'action': 'SELL',
                'price': data['Close'],
                'rsi': data['RSI']
            })
        
        return signals

class BreakoutStrategy(PandasStrategy):
    """Breakout Strategy - Trade on price breakouts from ranges"""
    
    def __init__(self, symbol: str = 'AAPL'):
        super().__init__("Breakout Strategy")
        self.symbol = symbol
    
    def generate_signals(self, data: pd.Series) -> List[Dict]:
        signals = []
        
        # For breakout strategy, we need to track highs and lows differently
        # Since we're processing one row at a time, we'll use a simpler approach
        # based on recent price action
        
        # Simple breakout based on current price vs recent range
        if hasattr(self, 'recent_high') and hasattr(self, 'recent_low'):
            # Breakout above recent high
            if data['Close'] > self.recent_high * 1.01:  # 1% above recent high
                signals.append({
                    'symbol': self.symbol,
                    'action': 'BUY',
                    'price': data['Close'],
                    'breakout_level': self.recent_high
                })
            # Breakdown below recent low
            elif data['Close'] < self.recent_low * 0.99:  # 1% below recent low
                signals.append({
                    'symbol': self.symbol,
                    'action': 'SELL',
                    'price': data['Close'],
                    'breakdown_level': self.recent_low
                })
        
        # Update recent high and low
        if not hasattr(self, 'recent_high') or data['High'] > self.recent_high:
            self.recent_high = data['High']
        if not hasattr(self, 'recent_low') or data['Low'] < self.recent_low:
            self.recent_low = data['Low']
        
        return signals
