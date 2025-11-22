Algorithmic Trading Backtesting Platform

A Python-based algorithmic trading platform designed for strategy development, historical data analysis, and performance evaluation through a flexible backtesting engine.
This project allows you to quickly prototype trading strategies, run simulations over historical price data, and analyze results with customizable logic.

Backtesting Engine

- Runs simulations on historical OHLCV data.

- Supports portfolio tracking (cash, positions, PnL).

- Trade execution simulator (fills, order handling, slippage).

- Customizable position sizing and risk rules.

Strategy Framework

- Includes prebuilt strategies such as:

- Moving Average Crossover, Mean Reversion (Bollinger Bands), Momentum Strategy

Each strategy:

- Generates buy/sell signals

- Uses customizable parameters

- Follows an object-oriented interface for easy extension

Performance Tracking

- Track daily returns

- Equity curve

- Open/closed positions

- Trade history

- Win/loss rate, max drawdown, and more (depending on strategy implementation)

  Future Features:

  - Using an Interactive Brokers account to do both paper trade and live trade
