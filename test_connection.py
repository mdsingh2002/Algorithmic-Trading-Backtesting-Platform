#!/usr/bin/env python3
"""
Test script for Interactive Brokers API connection
Run this script to verify your setup before using the main application
"""

import sys
import time
from ib_client import IBConnection
from config import Config

def test_connection():
    """Test the connection to Interactive Brokers"""
    print("Testing Interactive Brokers API Connection")
    print("=" * 50)
    
    # Create connection
    ib_conn = IBConnection()
    
    print(f"Attempting to connect to {Config.IB_HOST}:{Config.IB_PORT}")
    print(f"Client ID: {Config.IB_CLIENT_ID}")
    print()
    
    try:
        # Attempt connection
        success = ib_conn.connect()
        
        if success:
            print("Successfully connected to Interactive Brokers!")
            print()
            
            # Test account information
            print("Requesting account information...")
            ib_conn.request_account_summary()
            time.sleep(2)  # Wait for data
            
            account_info = ib_conn.get_account_info()
            if account_info:
                print("Account information received:")
                for key, value in account_info.items():
                    print(f"   {key}: ${float(value):,.2f}")
            else:
                print("No account information received")
            
            print()
            
            # Test market data (AAPL as example)
            print("Testing market data for AAPL...")
            req_id = ib_conn.request_market_data("AAPL")
            if req_id:
                print(f"Market data request sent (ReqID: {req_id})")
                time.sleep(3)  # Wait for data
                
                market_data = ib_conn.get_market_data(req_id)
                if market_data and 'price' in market_data:
                    print(f"Market data received: ${market_data['price']:.2f}")
                else:
                    print("No market data received (may be outside market hours)")
            else:
                print("Failed to request market data")
            
            print()
            
            # Disconnect
            print("Disconnecting...")
            ib_conn.disconnect()
            print("Disconnected successfully")
            
        else:
            print("Failed to connect to Interactive Brokers")
            print()
            print("Troubleshooting tips:")
            print("1. Make sure TWS or IB Gateway is running and logged in")
            print("2. Check that API connections are enabled in TWS/Gateway")
            print("3. Verify the port number matches your TWS/Gateway settings")
            print("4. Ensure your IP is in the trusted IPs list")
            print("5. Check that the client ID is unique")
            
    except Exception as e:
        print(f"Error during connection test: {e}")
        print()
        print("Make sure you have:")
        print("1. Interactive Brokers account")
        print("2. TWS or IB Gateway installed and running")
        print("3. API connections enabled")
        print("4. Correct port configuration")

def main():
    """Main test function"""
    print("Interactive Brokers API Connection Test")
    print("This script will test your connection to TWS or IB Gateway")
    print()
    
    # Check configuration
    print("Configuration:")
    print(f"  Host: {Config.IB_HOST}")
    print(f"  Port: {Config.IB_PORT}")
    print(f"  Client ID: {Config.IB_CLIENT_ID}")
    print(f"  Paper Trading: {Config.PAPER_TRADING}")
    print()
    
    # Ask for confirmation
    response = input("Do you want to proceed with the connection test? (y/n): ")
    if response.lower() != 'y':
        print("Test cancelled.")
        return
    
    print()
    test_connection()

if __name__ == "__main__":
    main()

