from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import json
import logging
from datetime import datetime
from algo_trader import AlgoTrader
from config import Config

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize the algo trader
algo_trader = AlgoTrader()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        status = algo_trader.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/connect', methods=['POST'])
def connect():
    """Connect to Interactive Brokers"""
    try:
        success = algo_trader.connect_to_ib()
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error connecting: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    """Disconnect from Interactive Brokers"""
    try:
        algo_trader.disconnect_from_ib()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error disconnecting: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
def manage_watchlist():
    """Manage watchlist"""
    try:
        if request.method == 'GET':
            return jsonify({'watchlist': algo_trader.watchlist})
        
        elif request.method == 'POST':
            data = request.get_json()
            symbol = data.get('symbol', '').upper()
            if symbol:
                success = algo_trader.add_to_watchlist(symbol)
                return jsonify({'success': success})
            else:
                return jsonify({'error': 'Symbol is required'}), 400
        
        elif request.method == 'DELETE':
            data = request.get_json()
            symbol = data.get('symbol', '').upper()
            if symbol:
                success = algo_trader.remove_from_watchlist(symbol)
                return jsonify({'success': success})
            else:
                return jsonify({'error': 'Symbol is required'}), 400
                
    except Exception as e:
        logger.error(f"Error managing watchlist: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-data')
def get_market_data():
    """Get current market data"""
    try:
        market_data = algo_trader.get_market_data()
        return jsonify(market_data)
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/positions')
def get_positions():
    """Get current positions"""
    try:
        positions = algo_trader.get_positions()
        return jsonify(positions)
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/account')
def get_account_info():
    """Get account information"""
    try:
        account_info = algo_trader.get_account_info()
        return jsonify(account_info)
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trade-history')
def get_trade_history():
    """Get trade history"""
    try:
        trade_history = algo_trader.get_trade_history()
        # Convert datetime objects to strings for JSON serialization
        for trade in trade_history:
            if 'timestamp' in trade:
                trade['timestamp'] = trade['timestamp'].isoformat()
        return jsonify(trade_history)
    except Exception as e:
        logger.error(f"Error getting trade history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    try:
        performance = algo_trader.get_performance_metrics()
        return jsonify(performance)
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies')
def get_strategies():
    """Get available strategies"""
    try:
        strategies = algo_trader.strategy_manager.get_all_strategies()
        strategy_info = {}
        for name, strategy in strategies.items():
            strategy_info[name] = {
                'name': strategy.name,
                'active': name == algo_trader.strategy_manager.active_strategy
            }
        return jsonify(strategy_info)
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy', methods=['POST'])
def set_strategy():
    """Set active strategy"""
    try:
        data = request.get_json()
        strategy_name = data.get('strategy')
        if strategy_name:
            algo_trader.set_strategy(strategy_name)
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Strategy name is required'}), 400
    except Exception as e:
        logger.error(f"Error setting strategy: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/start', methods=['POST'])
def start_trading():
    """Start automated trading"""
    try:
        success = algo_trader.start_trading()
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error starting trading: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/stop', methods=['POST'])
def stop_trading():
    """Stop automated trading"""
    try:
        algo_trader.stop_trading()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error stopping trading: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    """Execute a manual trade"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        action = data.get('action', '').upper()
        quantity = int(data.get('quantity', 0))
        order_type = data.get('order_type', 'MKT')
        
        if not all([symbol, action, quantity]):
            return jsonify({'error': 'Symbol, action, and quantity are required'}), 400
            
        if action not in ['BUY', 'SELL']:
            return jsonify({'error': 'Action must be BUY or SELL'}), 400
            
        order_id = algo_trader.execute_trade(symbol, action, quantity, order_type)
        if order_id:
            return jsonify({'success': True, 'order_id': order_id})
        else:
            return jsonify({'error': 'Failed to execute trade'}), 500
            
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )
