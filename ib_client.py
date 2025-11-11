import time
import threading
import logging
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.common import TickerId, OrderId
from ibapi.ticktype import TickType
# from ibapi.utils import decimalMaxString  # Not available in newer versions
from config import Config

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class IBClient(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}
        self.positions = {}
        self.orders = {}
        self.account_info = {}
        self.connected = False
        self.next_order_id = None
        
    def error(self, reqId, errorCode, errorString):
        logger.error(f"Error {errorCode}: {errorString}")
        
    def nextValidId(self, orderId: int):
        self.next_order_id = orderId
        logger.info(f"Next valid order ID: {orderId}")
        
    def connectAck(self):
        self.connected = True
        logger.info("Connected to Interactive Brokers")
        
    def connectionClosed(self):
        self.connected = False
        logger.info("Connection to Interactive Brokers closed")
        
    def tickPrice(self, reqId, tickType, price, attrib):
        if reqId not in self.data:
            self.data[reqId] = {}
        self.data[reqId]['price'] = price
        self.data[reqId]['tickType'] = tickType
        
    def tickSize(self, reqId, tickType, size):
        if reqId not in self.data:
            self.data[reqId] = {}
        self.data[reqId]['size'] = size
        
    def position(self, account, contract, pos, avgCost):
        symbol = contract.symbol
        self.positions[symbol] = {
            'position': pos,
            'avgCost': avgCost,
            'contract': contract
        }
        
    def positionEnd(self):
        logger.info("Position data received")
        
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        if orderId not in self.orders:
            self.orders[orderId] = {}
        self.orders[orderId].update({
            'status': status,
            'filled': filled,
            'remaining': remaining,
            'avgFillPrice': avgFillPrice,
            'lastFillPrice': lastFillPrice
        })
        logger.info(f"Order {orderId} status: {status}")
        
    def openOrder(self, orderId, contract, order, orderState):
        if orderId not in self.orders:
            self.orders[orderId] = {}
        self.orders[orderId].update({
            'contract': contract,
            'order': order,
            'orderState': orderState
        })
        
    def accountSummary(self, reqId, account, tag, value, currency):
        if account not in self.account_info:
            self.account_info[account] = {}
        self.account_info[account][tag] = value
        
    def accountSummaryEnd(self, reqId):
        logger.info("Account summary received")

class IBConnection:
    def __init__(self):
        self.client = IBClient()
        self.connection_thread = None
        
    def connect(self):
        """Connect to Interactive Brokers TWS/Gateway"""
        try:
            self.client.connect(Config.IB_HOST, Config.IB_PORT, Config.IB_CLIENT_ID)
            self.connection_thread = threading.Thread(target=self.client.run)
            self.connection_thread.daemon = True
            self.connection_thread.start()
            
            # Wait for connection
            timeout = 10
            while timeout > 0 and not self.client.connected:
                time.sleep(0.1)
                timeout -= 0.1
                
            if self.client.connected:
                logger.info("Successfully connected to Interactive Brokers")
                return True
            else:
                logger.error("Failed to connect to Interactive Brokers")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from Interactive Brokers"""
        if self.client.connected:
            self.client.disconnect()
            logger.info("Disconnected from Interactive Brokers")
            
    def request_market_data(self, symbol, secType="STK", exchange="SMART", currency="USD"):
        """Request real-time market data for a symbol"""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.exchange = exchange
        contract.currency = currency
        
        reqId = len(self.client.data) + 1
        self.client.reqMktData(reqId, contract, "", False, False, [])
        logger.info(f"Requested market data for {symbol}")
        return reqId
        
    def place_order(self, symbol, action, quantity, orderType="MKT", lmtPrice=None, stopPrice=None):
        """Place an order"""
        if not self.client.next_order_id:
            logger.error("No valid order ID available")
            return None
            
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        
        order = Order()
        order.action = action  # "BUY" or "SELL"
        order.totalQuantity = quantity
        order.orderType = orderType
        
        if lmtPrice:
            order.lmtPrice = lmtPrice
        if stopPrice:
            order.auxPrice = stopPrice
            
        orderId = self.client.next_order_id
        self.client.placeOrder(orderId, contract, order)
        self.client.next_order_id += 1
        
        logger.info(f"Placed {action} order for {quantity} {symbol}")
        return orderId
        
    def request_positions(self):
        """Request current positions"""
        self.client.reqPositions()
        
    def request_account_summary(self, account="All"):
        """Request account summary"""
        self.client.reqAccountSummary(1, account, "NetLiquidation,BuyingPower,TotalCashValue")
        
    def get_market_data(self, reqId):
        """Get market data for a specific request ID"""
        return self.client.data.get(reqId, {})
        
    def get_positions(self):
        """Get current positions"""
        return self.client.positions
        
    def get_orders(self):
        """Get current orders"""
        return self.client.orders
        
    def get_account_info(self):
        """Get account information"""
        return self.client.account_info
