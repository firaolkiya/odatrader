"""Signal models: votes, snapshots, trade intents."""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional
import json


@dataclass
class SignalVote:
    name: str
    value: int  # -1 bearish, 0 neutral, +1 bullish
    weight: float = 1.0
    details: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SignalSnapshot:
    ts: str
    instrument: str
    votes: List[SignalVote]
    bull_share: float
    bear_share: float
    score: float
    regime: float
    entry_threshold: float
    exit_threshold: float
    action: str = "HOLD"
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "ts": self.ts, "instrument": self.instrument,
            "votes": [v.to_dict() for v in self.votes],
            "bull_share": self.bull_share, "bear_share": self.bear_share,
            "score": self.score, "regime": self.regime,
            "entry_threshold": self.entry_threshold, "exit_threshold": self.exit_threshold,
            "action": self.action, "reason": self.reason,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


@dataclass
class TradeIntent:
    ts: str
    instrument: str
    side: str
    size: float
    order_type: str = "limit"
    px_hint: Optional[float] = None
    stop_px: Optional[float] = None
    tif: str = "GTC"
    post_only: bool = False
    reduce_only: bool = False
    reason: str = ""
    bot_id: str = "default"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Quote:
    ts: float
    bid: float
    ask: float
    bidsz: float = 0.0
    asksz: float = 0.0
    instrument: str = ""


@dataclass
class Bar:
    ts: float
    o: float
    h: float
    l: float
    c: float
    v: float
    timeframe: str = "1m"
    instrument: str = ""
