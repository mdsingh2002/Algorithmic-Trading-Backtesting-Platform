# Algo Trading Platform with Interactive Brokers API

A comprehensive algorithmic trading platform that integrates with Interactive Brokers TWS (Trader Workstation) or IB Gateway for automated trading strategies.

## Features

- **Real-time Market Data**: Live price feeds from Interactive Brokers
- **Multiple Trading Strategies**: 
  - Moving Average Crossover
  - Mean Reversion (Bollinger Bands)
  - Momentum Strategy
- **Automated Trading**: Fully automated strategy execution
- **Manual Trading**: Manual order placement interface
- **Risk Management**: Configurable stop-loss and position sizing
- **Modern Web Interface**: Beautiful, responsive dashboard
- **Paper Trading Support**: Safe testing environment
- **Real-time Monitoring**: Live updates on positions, orders, and performance

## Prerequisites

### 1. Interactive Brokers Account
- Active Interactive Brokers account (paper or live)
- TWS (Trader Workstation) or IB Gateway installed and running

### 2. Python Environment
- Python 3.8 or higher
- pip package manager

### 3. Interactive Brokers Software Setup

#### Option A: TWS (Trader Workstation)
1. Download and install TWS from [Interactive Brokers](https://www.interactivebrokers.com/en/trading/tws.php)
2. Launch TWS and log in
3. Go to **Edit** → **Global Configuration** → **API** → **Settings**
4. Enable **Enable ActiveX and Socket Clients**
5. Set **Socket port** to `7497` (or your preferred port)
6. Add your local IP to **Trusted IPs** if needed

#### Option B: IB Gateway
1. Download IB Gateway from [Interactive Brokers](https://www.interactivebrokers.com/en/trading/ib-api.php)
2. Launch IB Gateway and log in
3. Configure API settings similar to TWS
4. Set port to `4001` (default for Gateway)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AlgoTrading
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy the example environment file
   cp env_example.txt .env
   
   # Edit .env with your settings
   # Make sure IB_HOST and IB_PORT match your TWS/Gateway settings
   ```

4. **Start Interactive Brokers software**
   - Launch TWS or IB Gateway
   - Ensure API connections are enabled
   - Note the port number (7497 for TWS, 4001 for Gateway)

## Configuration

### Environment Variables

Create a `.env` file based on `env_example.txt`:

```env
# Interactive Brokers Connection
IB_HOST=127.0.0.1          # TWS/Gateway host
IB_PORT=7497               # TWS port (7497) or Gateway port (4001)
IB_CLIENT_ID=1             # Unique client ID

# Trading Settings
PAPER_TRADING=True         # Set to False for live trading
DEFAULT_QUANTITY=100       # Default shares per trade
MAX_POSITION_SIZE=1000     # Maximum position size

# Risk Management
STOP_LOSS_PERCENTAGE=2.0   # Stop loss percentage
TAKE_PROFIT_PERCENTAGE=5.0 # Take profit percentage

# Web Interface
FLASK_HOST=0.0.0.0         # Web server host
FLASK_PORT=5000            # Web server port
DEBUG=True                 # Debug mode

# Logging
LOG_LEVEL=INFO             # Logging level
LOG_FILE=algo_trading.log  # Log file name
```

## Usage

### 1. Start the Application

```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

### 2. Connect to Interactive Brokers

1. Open your web browser and navigate to `http://localhost:5000`
2. Click the **Connect** button to establish connection with TWS/Gateway
3. Verify connection status shows "Connected"

### 3. Add Symbols to Watchlist

1. In the **Watchlist** section, enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
2. Click the **+** button to add it to your watchlist
3. The system will start receiving real-time market data for that symbol

### 4. Select Trading Strategy

1. In the **Trading Controls** section, click on a strategy card:
   - **Moving Average Crossover**: Uses short and long moving averages
   - **Mean Reversion**: Uses Bollinger Bands for entry/exit signals
   - **Momentum Strategy**: Trades based on price momentum

### 5. Start Automated Trading

1. Click **Start Trading** to begin automated strategy execution
2. The system will automatically place buy/sell orders based on strategy signals
3. Monitor positions and performance in real-time

### 6. Manual Trading

1. Enter a symbol and quantity in the **Manual Trade** section
2. Click **Buy** or **Sell** to place manual orders
3. Orders are executed as market orders by default

## Trading Strategies

### Moving Average Crossover
- **Logic**: Buy when short MA crosses above long MA, sell when it crosses below
- **Parameters**: 
  - Short window: 10 periods
  - Long window: 30 periods
- **Best for**: Trending markets

### Mean Reversion (Bollinger Bands)
- **Logic**: Buy when price touches lower band, sell when it touches upper band
- **Parameters**:
  - Window: 20 periods
  - Standard deviation: 2.0
- **Best for**: Range-bound markets

### Momentum Strategy
- **Logic**: Buy on positive momentum, sell on negative momentum
- **Parameters**:
  - Lookback period: 10 periods
  - Momentum threshold: 2%
- **Best for**: Volatile markets with clear trends

## Risk Management

### Position Sizing
- Each strategy has built-in position sizing rules
- Positions are sized as a percentage of account value
- Maximum position size is configurable

### Stop Loss and Take Profit
- Configurable stop-loss and take-profit percentages
- Helps limit downside risk and lock in profits

### Paper Trading
- **Always test with paper trading first**
- Set `PAPER_TRADING=True` in your `.env` file
- Paper trading uses simulated money and orders

## Monitoring and Analysis

### Real-time Dashboard
- **Market Data**: Live price feeds for all watchlist symbols
- **Positions**: Current holdings and average costs
- **Performance**: Trade statistics and completion rates
- **Trade History**: Complete order history with timestamps

### Logging
- All trading activities are logged to `algo_trading.log`
- Log level can be configured in `.env`
- Monitor logs for debugging and analysis

## Safety Guidelines

### Before Live Trading
1. **Test thoroughly** with paper trading
2. **Start small** with minimal position sizes
3. **Monitor closely** during initial live trading
4. **Have stop-losses** in place
5. **Understand the strategies** you're using

### Risk Warnings
- **Past performance does not guarantee future results**
- **Algorithmic trading involves significant risk**
- **Always use proper risk management**
- **Never risk more than you can afford to lose**

## Troubleshooting

### Connection Issues
1. **Check TWS/Gateway is running** and logged in
2. **Verify API settings** are enabled in TWS/Gateway
3. **Check port numbers** match your configuration
4. **Ensure firewall** allows connections on the API port

### No Market Data
1. **Verify symbols** are valid and actively traded
2. **Check market hours** - data may not be available outside trading hours
3. **Ensure account** has market data subscriptions

### Order Issues
1. **Check account permissions** for trading
2. **Verify sufficient funds** for orders
3. **Check symbol availability** for trading

## Development

### Project Structure
```
AlgoTrading/
├── app.py                 # Flask web application
├── algo_trader.py         # Main trading engine
├── ib_client.py          # Interactive Brokers API client
├── trading_strategies.py  # Trading strategy implementations
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── templates/            # Web templates
│   └── index.html       # Main dashboard
├── .env                 # Environment configuration
└── README.md           # This file
```

### Adding New Strategies
1. Create a new class inheriting from `TradingStrategy`
2. Implement required methods: `calculate_signals`, `should_buy`, `should_sell`
3. Add the strategy to `StrategyManager` in `trading_strategies.py`

### Customizing Risk Management
- Modify position sizing logic in strategy classes
- Adjust stop-loss and take-profit parameters
- Add additional risk checks in `algo_trader.py`

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in `algo_trading.log`
3. Ensure Interactive Brokers software is properly configured
4. Verify all dependencies are installed correctly

## Disclaimer

This software is for educational and research purposes. Trading involves substantial risk of loss and is not suitable for all investors. The authors are not responsible for any financial losses incurred through the use of this software. Always consult with a qualified financial advisor before making investment decisions.

## License

This project is provided as-is for educational purposes. Use at your own risk.
