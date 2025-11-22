from flask import Flask, render_template, request, jsonify
from backtester import BacktestEngine, MovingAverageCrossoverStrategy, BollingerBandsStrategy, RSIStrategy, ScalpingStrategy, MomentumStrategy, MeanReversionStrategy, BreakoutStrategy
import logging
import json
import os
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize backtest engine
engine = BacktestEngine()

@app.route('/')
def index():
    return render_template('backtest.html')

@app.route('/api/run_backtest', methods=['POST'])
def run_backtest():
    try:
        data = request.json
        symbol = data.get('symbol', 'AAPL')
        start_date = data.get('start_date', '2023-01-01')
        end_date = data.get('end_date', '2024-01-01')
        strategy_name = data.get('strategy', 'Moving Average Crossover')
        initial_capital = float(data.get('initial_capital', 100000))
        
        # Select strategy
        if strategy_name == 'Moving Average Crossover':
            strategy = MovingAverageCrossoverStrategy(5, 20, symbol)
        elif strategy_name == 'Bollinger Bands':
            strategy = BollingerBandsStrategy(10, 1.5, symbol)
        elif strategy_name == 'RSI Strategy':
            strategy = RSIStrategy(40, 60, symbol)
        elif strategy_name == 'Scalping Strategy':
            strategy = ScalpingStrategy(symbol)
        elif strategy_name == 'Momentum Strategy':
            strategy = MomentumStrategy(symbol)
        elif strategy_name == 'Mean Reversion Strategy':
            strategy = MeanReversionStrategy(symbol)
        elif strategy_name == 'Breakout Strategy':
            strategy = BreakoutStrategy(symbol)
        else:
            return jsonify({'error': 'Invalid strategy'})
        
        # Run backtest
        results = engine.run_backtest(
            strategy=strategy,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        
        if 'error' in results:
            return jsonify({'error': results['error']})
        
        # Prepare response data
        response_data = {
            'symbol': symbol,
            'strategy': strategy_name,
            'initial_capital': float(results['initial_capital']),
            'final_portfolio_value': float(results['final_portfolio_value']),
            'total_return': float(results['total_return']),
            'annualized_return': float(results['annualized_return']),
            'sharpe_ratio': float(results['sharpe_ratio']),
            'max_drawdown': float(results['max_drawdown']),
            'total_trades': int(results['total_trades']),
            'portfolio_values': _serialize_portfolio_values(results['portfolio_values']),
            'trade_history': _serialize_trade_history(results['trade_history'])
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)})

def _serialize_portfolio_values(portfolio_values):
    """Serialize portfolio values DataFrame to JSON-safe format"""
    try:
        # Reset index to make date a column if it's currently the index
        if isinstance(portfolio_values.index, pd.DatetimeIndex):
            df = portfolio_values.reset_index()
            # Rename the index column to 'date' if it exists
            if df.columns[0] not in ['date', 'Date']:
                df.rename(columns={df.columns[0]: 'date'}, inplace=True)
        else:
            df = portfolio_values.copy()
        
        # Ensure we have the date column
        if 'date' not in df.columns and 'Date' in df.columns:
            df.rename(columns={'Date': 'date'}, inplace=True)
        
        serialized = []
        for idx, row in df.iterrows():
            # Get date from index or column
            if 'date' in df.columns:
                date_val = row['date']
            elif isinstance(portfolio_values.index, pd.DatetimeIndex):
                date_val = portfolio_values.index[idx]
            else:
                date_val = idx
            
            # Format date
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%Y-%m-%d')
            elif isinstance(date_val, str):
                date_str = date_val
            else:
                date_str = str(date_val)
            
            serialized_record = {
                'date': date_str,
                'portfolio_value': float(row['portfolio_value']) if 'portfolio_value' in row and not pd.isna(row['portfolio_value']) else 0.0,
                'price': float(row['price']) if 'price' in row and not pd.isna(row['price']) else 0.0
            }
            serialized.append(serialized_record)
        return serialized
    except Exception as e:
        logging.error(f"Error serializing portfolio values: {e}", exc_info=True)
        return []

def _serialize_trade_history(trade_history):
    """Serialize trade history to JSON-safe format"""
    try:
        serialized = []
        for trade in trade_history:
            serialized_trade = {
                'date': trade['date'].strftime('%Y-%m-%d') if hasattr(trade['date'], 'strftime') else str(trade['date']),
                'symbol': str(trade['symbol']),
                'action': str(trade['action']),
                'quantity': int(trade['quantity']),
                'price': float(trade['price']) if not pd.isna(trade['price']) else 0.0,
                'cost': float(trade.get('cost', 0)) if not pd.isna(trade.get('cost', 0)) else 0.0,
                'revenue': float(trade.get('revenue', 0)) if not pd.isna(trade.get('revenue', 0)) else 0.0,
                'portfolio_value': float(trade.get('portfolio_value', 0)) if not pd.isna(trade.get('portfolio_value', 0)) else 0.0
            }
            serialized.append(serialized_trade)
        return serialized
    except Exception as e:
        logging.error(f"Error serializing trade history: {e}")
        return []

@app.route('/api/get_symbols')
def get_symbols():
    """Get list of popular symbols"""
    symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
        'SPY', 'QQQ', 'IWM', 'GLD', 'TLT', 'VTI', 'VOO'
    ]
    return jsonify(symbols)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print("=== Pandas Backtesting Web App ===")
    print("No Interactive Brokers required!")
    print(f"Open your browser to: http://localhost:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
