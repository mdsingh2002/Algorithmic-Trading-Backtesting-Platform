import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Interactive Brokers TWS/Gateway settings
    IB_HOST = os.getenv('IB_HOST', '127.0.0.1')
    IB_PORT = int(os.getenv('IB_PORT', 7497))  # 7497 for TWS, 4001 for Gateway
    IB_CLIENT_ID = int(os.getenv('IB_CLIENT_ID', 1))
    
    # Paper trading settings
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'True').lower() == 'true'
    
    # Trading parameters
    DEFAULT_QUANTITY = int(os.getenv('DEFAULT_QUANTITY', 100))
    MAX_POSITION_SIZE = int(os.getenv('MAX_POSITION_SIZE', 1000))
    
    # Risk management
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', 2.0))
    TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', 5.0))
    
    # API settings
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'algo_trading.log')
