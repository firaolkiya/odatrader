"""Exchange factory."""
from backend.exchange.binance import BinanceExchange
from backend.exchange.coinbase import CoinbaseExchange
from backend.exchange.kraken import KrakenExchange

EXCHANGES = {"binance": BinanceExchange, "coinbase": CoinbaseExchange, "kraken": KrakenExchange}

def get_exchange(name: str, **kwargs):
    cls = EXCHANGES.get(name.lower())
    if not cls:
        raise ValueError(f"Unknown exchange: {name}")
    return cls(**kwargs)
