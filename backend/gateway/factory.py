"""Gateway factory for multi-venue connectors."""
from backend.gateway.binance_gateway import BinanceGateway
from backend.gateway.alpaca_gateway import AlpacaGateway
from backend.gateway.oanda_gateway import OANDAGateway
from backend.core.instruments import Instrument, AssetClass
import os


GATEWAYS = {
    "binance": BinanceGateway,
    "alpaca": AlpacaGateway,
    "oanda": OANDAGateway,
    "bybit": BinanceGateway,
    "deribit": BinanceGateway,
}


def get_gateway(instrument: Instrument):
    venue = instrument.venue.lower()
    cls = GATEWAYS.get(venue, BinanceGateway)
    if venue == "binance":
        return cls(api_key=os.getenv("BINANCE_API_KEY", ""), secret=os.getenv("BINANCE_SECRET_KEY", ""))
    if venue == "alpaca":
        return cls(api_key=os.getenv("ALPACA_API_KEY", ""), secret=os.getenv("ALPACA_SECRET_KEY", ""))
    if venue == "oanda":
        return cls(api_key=os.getenv("OANDA_API_KEY", ""), account_id=os.getenv("OANDA_ACCOUNT_ID", ""))
    return cls()
