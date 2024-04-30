"""Canonical instrument model for multi-asset trading."""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional
import json


class AssetClass(str, Enum):
    CRYPTO_SPOT = "CRYPTO_SPOT"
    CRYPTO_PERP = "CRYPTO_PERP"
    EQUITY = "EQUITY"
    FX = "FX"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    PERP = "PERP"


@dataclass
class Instrument:
    symbol: str
    venue: str
    asset_class: AssetClass
    tick_size: float = 0.01
    lot_size: float = 0.001
    quote_ccy: str = "USDT"
    leverage_allowed: bool = False
    max_leverage: float = 1.0
    margin_type: str = "cross"
    contract_size: float = 1.0
    tick_value: float = 1.0
    funding_rate: float = 0.0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["asset_class"] = self.asset_class.value
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Instrument":
        ac = data.get("asset_class", "CRYPTO_SPOT")
        if isinstance(ac, str):
            ac = AssetClass(ac)
        return cls(
            symbol=data["symbol"], venue=data["venue"], asset_class=ac,
            tick_size=data.get("tick_size", 0.01), lot_size=data.get("lot_size", 0.001),
            quote_ccy=data.get("quote_ccy", "USDT"),
            leverage_allowed=data.get("leverage_allowed", False),
            max_leverage=data.get("max_leverage", 1.0),
            margin_type=data.get("margin_type", "cross"),
            contract_size=data.get("contract_size", 1.0),
            tick_value=data.get("tick_value", 1.0),
            funding_rate=data.get("funding_rate", 0.0),
            metadata=data.get("metadata", {}),
        )


# Default instrument universe
DEFAULT_INSTRUMENTS: List[Instrument] = [
    Instrument("BTCUSDT", "binance", AssetClass.CRYPTO_SPOT, 0.01, 0.001, "USDT"),
    Instrument("ETHUSDT", "binance", AssetClass.CRYPTO_SPOT, 0.01, 0.01, "USDT"),
    Instrument("BTCUSDT-PERP", "binance", AssetClass.PERP, 0.01, 0.001, "USDT", True, 20.0, "isolated"),
    Instrument("ETHUSDT-PERP", "binance", AssetClass.PERP, 0.01, 0.01, "USDT", True, 20.0, "isolated"),
    Instrument("AAPL", "alpaca", AssetClass.EQUITY, 0.01, 1.0, "USD"),
    Instrument("TSLA", "alpaca", AssetClass.EQUITY, 0.01, 1.0, "USD"),
    Instrument("EURUSD", "oanda", AssetClass.FX, 0.00001, 1000.0, "USD"),
    Instrument("USDJPY", "oanda", AssetClass.FX, 0.001, 1000.0, "JPY"),
    Instrument("GBPUSD", "oanda", AssetClass.FX, 0.00001, 1000.0, "USD"),
]


class InstrumentService:
    def __init__(self):
        self._instruments: Dict[str, Instrument] = {i.symbol: i for i in DEFAULT_INSTRUMENTS}

    def register(self, instrument: Instrument):
        self._instruments[instrument.symbol] = instrument

    def get(self, symbol: str) -> Optional[Instrument]:
        return self._instruments.get(symbol)

    def list_all(self) -> List[Instrument]:
        return list(self._instruments.values())

    def list_by_class(self, asset_class: AssetClass) -> List[Instrument]:
        return [i for i in self._instruments.values() if i.asset_class == asset_class]

    def load_from_yaml(self, path: str = "config/instruments.yaml"):
        try:
            import yaml
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            for item in data.get("instruments", []):
                self.register(Instrument.from_dict(item))
        except FileNotFoundError:
            pass


instrument_service = InstrumentService()
