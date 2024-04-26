"""Per-bot configuration model."""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json
import uuid


@dataclass
class BotConfig:
    """Configuration for a single OdaTrade bot instance."""
    name: str
    symbols: List[str] = field(default_factory=lambda: ["btcusdt"])
    strategy: str = "strategy_voter"
    risk_profile: str = "moderate"
    starting_balance: float = 5000.0
    max_trades_per_day: int = 30
    max_drawdown: float = 0.15
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.02
    fixed_risk_pct: float = 0.01
    max_per_symbol_exposure: float = 0.3
    max_total_exposure: float = 1.0
    interval: str = "1m"
    enabled_strategies: List[str] = field(default_factory=lambda: [
        "rsi", "macd", "ema_crossover", "bollinger", "ml", "gpt"
    ])
    bot_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    container_id: Optional[str] = None
    cloud_region: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> "BotConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, raw: str) -> "BotConfig":
        return cls.from_dict(json.loads(raw))


RISK_PROFILES = {
    "conservative": {"max_drawdown": 0.05, "fixed_risk_pct": 0.005, "max_trades_per_day": 10},
    "moderate": {"max_drawdown": 0.15, "fixed_risk_pct": 0.01, "max_trades_per_day": 30},
    "aggressive": {"max_drawdown": 0.25, "fixed_risk_pct": 0.02, "max_trades_per_day": 60},
}


def apply_risk_profile(config: BotConfig) -> BotConfig:
    profile = RISK_PROFILES.get(config.risk_profile, RISK_PROFILES["moderate"])
    for key, val in profile.items():
        setattr(config, key, val)
    return config
