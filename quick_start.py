#!/usr/bin/env python3
"""
Quick Start Script for Algo Trading Platform
This script helps you get started quickly with minimal configuration
"""

import os
import sys
import subprocess
import time

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'ibapi', 'flask', 'flask-cors', 'pandas', 'numpy', 
        'matplotlib', 'plotly', 'python-dotenv', 'schedule'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"{package}")
        except ImportError:
            print(f"{package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install dependencies")
            return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists('.env'):
        print(".env file already exists")
        return True
    
    print("Creating .env file...")
    try:
        with open('env_example.txt', 'r') as f:
            env_content = f.read()
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(".env file created from template")
        print("Please review and edit .env file with your settings")
        return True
    except Exception as e:
        print(f" Failed to create .env file: {e}")
        return False

def check_ib_software():
    """Check if Interactive Brokers software is likely running"""
    print("\nChecking Interactive Brokers software...")
    print("Make sure TWS or IB Gateway is running and configured:")
    print("   1. TWS/Gateway should be logged in")
    print("   2. API connections should be enabled")
    print("   3. Port should be set to 7497 (TWS) or 4001 (Gateway)")
    print("   4. Your IP should be in trusted IPs list")
    
    response = input("\nIs TWS or IB Gateway running and configured? (y/n): ")
    return response.lower() == 'y'

def test_connection():
    """Test the connection to Interactive Brokers"""
    print("\nTesting connection to Interactive Brokers...")
    try:
        from test_connection import test_connection as run_test
        run_test()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

def start_application():
    """Start the main application"""
    print("\nStarting Algo Trading Platform...")
    print("The web interface will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the application")
    print()
    
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Failed to start application: {e}")

def main():
    """Main quick start function"""
    print("Algo Trading Platform - Quick Start")
    print("=" * 50)
    
    # Step 1: Check Python version
    print("Step 1: Checking Python version...")
    if not check_python_version():
        return
    
    # Step 2: Check dependencies
    print("\nStep 2: Checking dependencies...")
    if not check_dependencies():
        print("Failed to install dependencies. Please run: pip install -r requirements.txt")
        return
    
    # Step 3: Create environment file
    print("\nStep 3: Setting up configuration...")
    if not create_env_file():
        return
    
    # Step 4: Check IB software
    print("\nStep 4: Interactive Brokers software check...")
    if not check_ib_software():
        print("Please start TWS or IB Gateway and configure API settings")
        print("   Then run this script again")
        return
    
    # Step 5: Test connection
    print("\nStep 5: Testing connection...")
    if not test_connection():
        print("Connection test failed. Please check your TWS/Gateway configuration")
        return
    
    # Step 6: Start application
    print("\nStep 6: Starting application...")
    start_application()

if __name__ == "__main__":
    main()

