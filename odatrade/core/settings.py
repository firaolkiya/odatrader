"""Settings loader with validation."""
import os
from dataclasses import dataclass, field
from typing import List
from odatrade.core.exceptions import ConfigError

@dataclass
class OdaTradeSettings:
    app_name: str = "OdaTrade"
    database_url: str = "sqlite:///odatrade.db"
    symbols: List[str] = field(default_factory=lambda: ["btcusdt", "ethusdt"])
    starting_balance: float = 5000.0
    jwt_secret: str = "change-me"
    groq_api_key: str = ""
    binance_api_key: str = ""
    binance_secret_key: str = ""

    @classmethod
    def from_env(cls) -> "OdaTradeSettings":
        symbols = os.getenv("SYMBOLS", "btcusdt,ethusdt").split(",")
        if not symbols:
            raise ConfigError("SYMBOLS must not be empty")
        return cls(
            database_url=os.getenv("DATABASE_URL", "sqlite:///odatrade.db"),
            symbols=[s.strip().lower() for s in symbols],
            starting_balance=float(os.getenv("STARTING_BALANCE", "5000")),
            jwt_secret=os.getenv("JWT_SECRET", "change-me"),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            binance_api_key=os.getenv("BINANCE_API_KEY", ""),
            binance_secret_key=os.getenv("BINANCE_SECRET_KEY", ""),
        )
