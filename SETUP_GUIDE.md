# Interactive Brokers API Setup Guide

## ✅ What's Working
- Python environment is set up correctly
- All required packages are installed
- The algo trading platform is ready to use

## 🔧 Next Steps: Set Up Interactive Brokers

### Option 1: TWS (Trader Workstation) - Recommended for Testing

1. **Download TWS**
   - Go to: https://www.interactivebrokers.com/en/trading/tws.php
   - Download and install TWS

2. **Launch TWS and Log In**
   - Start TWS
   - Log in with your Interactive Brokers credentials
   - **Important**: Use PAPER TRADING account for testing

3. **Configure API Settings**
   - In TWS, go to **Edit** → **Global Configuration** → **API** → **Settings**
   - ✅ **Enable ActiveX and Socket Clients**
   - Set **Socket Port** to `7497` (for paper trading)
   - Add your local IP (`127.0.0.1`) to **Trusted IPs**

4. **Test Connection**
   ```bash
   py test_connection.py
   ```

### Option 2: IB Gateway (Lightweight Alternative)

1. **Download IB Gateway**
   - Go to: https://www.interactivebrokers.com/en/trading/ib-api.php
   - Download IB Gateway

2. **Launch IB Gateway**
   - Start IB Gateway
   - Log in with your credentials
   - Use PAPER TRADING account

3. **Configure API Settings**
   - Similar to TWS, enable API connections
   - Set port to `4002` (for paper trading)

4. **Update Configuration**
   - Edit `.env` file and change `IB_PORT=4002`

## 🚀 Quick Start

Once TWS or IB Gateway is running:

1. **Test the connection:**
   ```bash
   py test_connection.py
   ```

2. **Start the web interface:**
   ```bash
   py app.py
   ```

3. **Open your browser:**
   - Go to: http://localhost:5000
   - Click "Connect" to establish connection
   - Add symbols to watchlist (e.g., AAPL, MSFT)
   - Select a trading strategy
   - Start automated trading

## 📋 Important Notes

- **Always use PAPER TRADING first** - it's safe and uses simulated money
- **Market hours**: Most data is only available during market hours (9:30 AM - 4:00 PM ET)
- **Account requirements**: You need an Interactive Brokers account (paper trading is free)

## 🔍 Troubleshooting

### Connection Issues
- Make sure TWS/Gateway is running and logged in
- Verify API settings are enabled
- Check that the port numbers match
- Ensure your IP is in the trusted IPs list

### No Market Data
- Check if markets are open
- Verify you have market data subscriptions
- Try popular symbols like AAPL, MSFT, GOOGL

## 🎯 Ready to Trade?

Once you have TWS or IB Gateway running and connected, you can:

1. **Test with paper trading** (recommended)
2. **Add symbols to your watchlist**
3. **Choose from 3 trading strategies:**
   - Moving Average Crossover
   - Mean Reversion (Bollinger Bands)
   - Momentum Strategy
4. **Start automated trading**
5. **Monitor performance in real-time**

## ⚠️ Safety First

- **Never risk more than you can afford to lose**
- **Always test with paper trading first**
- **Start with small position sizes**
- **Monitor your strategies closely**

---

**Need help?** The error messages in the test script will guide you through any issues!
