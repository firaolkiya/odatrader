# backend/exchange/binance.py

import ccxt
from backend.exchange.base import BaseExchange

class BinanceExchange(BaseExchange):
    def __init__(self, api_key, secret):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True
        })

    def get_ohlcv(self, symbol, timeframe, limit=100):
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def create_order(self, symbol, side, amount, order_type="market"):
        return self.exchange.create_order(symbol, order_type, side, amount)

    def get_balance(self, asset):
        balance = self.exchange.fetch_balance()
        return balance['total'].get(asset, 0)

    def get_open_orders(self, symbol):
        return self.exchange.fetch_open_orders(symbol)

    def cancel_order(self, order_id, symbol):
        return self.exchange.cancel_order(order_id, symbol)
