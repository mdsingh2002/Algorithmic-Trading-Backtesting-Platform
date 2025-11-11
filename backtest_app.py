from flask import Flask, render_template, request, jsonify
from backtester import BacktestEngine, MovingAverageCrossoverStrategy, BollingerBandsStrategy, RSIStrategy, ScalpingStrategy, MomentumStrategy, MeanReversionStrategy, BreakoutStrategy
import logging
import json
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
        # Convert to records and handle datetime serialization
        records = portfolio_values.to_dict('records')
        serialized = []
        for record in records:
            serialized_record = {
                'date': record['date'].strftime('%Y-%m-%d') if hasattr(record['date'], 'strftime') else str(record['date']),
                'portfolio_value': float(record['portfolio_value']) if not pd.isna(record['portfolio_value']) else 0.0,
                'price': float(record['price']) if not pd.isna(record['price']) else 0.0
            }
            serialized.append(serialized_record)
        return serialized
    except Exception as e:
        logging.error(f"Error serializing portfolio values: {e}")
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
    print("=== Pandas Backtesting Web App ===")
    print("No Interactive Brokers required!")
    print("Open your browser to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
