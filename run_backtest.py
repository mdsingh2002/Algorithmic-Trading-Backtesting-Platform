#!/usr/bin/env python3
"""
Simple backtesting script using pandas and yfinance
No Interactive Brokers required!
"""

from backtester import BacktestEngine, MovingAverageCrossoverStrategy, BollingerBandsStrategy, RSIStrategy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("=== Pandas Backtesting Engine ===")
    print("No Interactive Brokers required!")
    print()
    
    # Initialize backtest engine
    engine = BacktestEngine(initial_capital=100000)
    
    # Define test parameters
    symbol = "AAPL"
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    
    print(f"Running backtest for {symbol} from {start_date} to {end_date}")
    print(f"Initial capital: $100,000")
    print()
    
    # Test different strategies
    strategies = {
        "Moving Average Crossover": MovingAverageCrossoverStrategy(10, 30),
        "Bollinger Bands": BollingerBandsStrategy(20, 2.0),
        "RSI Strategy": RSIStrategy(30, 70)
    }
    
    for strategy_name, strategy in strategies.items():
        print(f"\n{'='*50}")
        print(f"Testing: {strategy_name}")
        print(f"{'='*50}")
        
        try:
            # Run backtest
            results = engine.run_backtest(
                strategy=strategy,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                initial_capital=100000
            )
            
            if 'error' in results:
                print(f"Error: {results['error']}")
                continue
            
            # Print results
            print(f"Initial Capital: ${results['initial_capital']:,.2f}")
            print(f"Final Portfolio Value: ${results['final_portfolio_value']:,.2f}")
            print(f"Total Return: {results['total_return']:.2%}")
            print(f"Annualized Return: {results['annualized_return']:.2%}")
            print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            print(f"Maximum Drawdown: {results['max_drawdown']:.2%}")
            print(f"Total Trades: {results['total_trades']}")
            
            # Plot results
            print("\nGenerating plot...")
            engine.plot_results(results, symbol)
            
        except Exception as e:
            print(f"Error running {strategy_name}: {e}")
    
    print(f"\n{'='*50}")
    print("Backtesting complete!")
    print("Check the interactive plots above for detailed results.")

if __name__ == "__main__":
    main()
