"""Redis-backed state persistence replacing file-based state."""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from odatrade.core.redis_client import RedisClient

logger = logging.getLogger("odatrade.redis_state")

# Key prefixes
PREFIX_BOT = "odatrade:bot:"
PREFIX_PNL = "odatrade:pnl:"
PREFIX_POSITION = "odatrade:position:"
PREFIX_SIGNAL = "odatrade:signal:"
PREFIX_KILL = "odatrade:kill:"
PREFIX_TRAILING = "odatrade:trailing:"
PREFIX_METRICS = "odatrade:metrics:"


class RedisStateStore:
    """Centralized Redis state store for all bot runtime data."""

    def __init__(self, redis_client: RedisClient = None):
        self.redis = redis_client or RedisClient.get_instance()
        self._fallback: Dict[str, Any] = {}

    def _key(self, prefix: str, bot_id: str, suffix: str = "") -> str:
        return f"{prefix}{bot_id}:{suffix}" if suffix else f"{prefix}{bot_id}"

    # --- Bot state ---
    def set_bot_status(self, bot_id: str, status: str, metadata: dict = None):
        data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        key = self._key(PREFIX_BOT, bot_id, "status")
        if self.redis.is_connected:
            self.redis.json_set(key, data, ex=86400)
        else:
            self._fallback[key] = data

    def get_bot_status(self, bot_id: str) -> Optional[dict]:
        key = self._key(PREFIX_BOT, bot_id, "status")
        if self.redis.is_connected:
            return self.redis.json_get(key)
        return self._fallback.get(key)

    def list_active_bots(self) -> List[str]:
        if not self.redis.is_connected:
            return [k.split(":")[2] for k in self._fallback if k.startswith(PREFIX_BOT)]
        keys = self.redis.client.keys(f"{PREFIX_BOT}*:status") if self.redis.client else []
        return [k.split(":")[2] for k in keys]

    # --- PnL tracking ---
    def update_pnl(self, bot_id: str, symbol: str, pnl: float, cumulative: float):
        key = self._key(PREFIX_PNL, bot_id, symbol)
        data = {
            "symbol": symbol,
            "pnl": pnl,
            "cumulative": cumulative,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        if self.redis.is_connected:
            self.redis.json_set(key, data, ex=3600)
            self.redis.publish(f"odatrade:events:pnl:{bot_id}", json.dumps(data))
        else:
            self._fallback[key] = data

    def get_pnl(self, bot_id: str, symbol: str = None) -> Any:
        if symbol:
            key = self._key(PREFIX_PNL, bot_id, symbol)
            if self.redis.is_connected:
                return self.redis.json_get(key)
            return self._fallback.get(key)
        prefix = self._key(PREFIX_PNL, bot_id)
        if self.redis.is_connected and self.redis.client:
            keys = self.redis.client.keys(f"{prefix}:*")
            return {k: self.redis.json_get(k) for k in keys}
        return {k: v for k, v in self._fallback.items() if k.startswith(prefix)}

    # --- Positions ---
    def set_position(self, bot_id: str, symbol: str, position: dict):
        key = self._key(PREFIX_POSITION, bot_id, symbol)
        position["updated_at"] = datetime.now(timezone.utc).isoformat()
        if self.redis.is_connected:
            self.redis.json_set(key, position, ex=86400)
        else:
            self._fallback[key] = position

    def get_positions(self, bot_id: str) -> Dict[str, dict]:
        prefix = self._key(PREFIX_POSITION, bot_id)
        if self.redis.is_connected and self.redis.client:
            keys = self.redis.client.keys(f"{prefix}:*")
            return {k.split(":")[-1]: self.redis.json_get(k) for k in keys}
        return {k.split(":")[-1]: v for k, v in self._fallback.items() if k.startswith(prefix)}

    # --- Signals ---
    def publish_signal(self, bot_id: str, signal: dict):
        signal["ts"] = datetime.now(timezone.utc).isoformat()
        signal["bot_id"] = bot_id
        channel = f"odatrade:events:signal:{bot_id}"
        payload = json.dumps(signal, default=str)
        if self.redis.is_connected:
            self.redis.publish(channel, payload)
            key = f"{PREFIX_SIGNAL}{bot_id}:{signal.get('symbol', 'unknown')}:{signal['ts']}"
            self.redis.set(key, payload, ex=3600)
        else:
            self._fallback[channel] = signal

    # --- Kill switch ---
    def activate_kill_switch(self, bot_id: str, reason: str = ""):
        key = self._key(PREFIX_KILL, bot_id)
        data = {"active": True, "reason": reason, "ts": datetime.now(timezone.utc).isoformat()}
        if self.redis.is_connected:
            self.redis.json_set(key, data)
            self.redis.publish(f"odatrade:events:kill:{bot_id}", json.dumps(data))
        else:
            self._fallback[key] = data

    def deactivate_kill_switch(self, bot_id: str):
        key = self._key(PREFIX_KILL, bot_id)
        if self.redis.is_connected:
            self.redis.delete(key)
        else:
            self._fallback.pop(key, None)

    def is_kill_switch_active(self, bot_id: str) -> bool:
        key = self._key(PREFIX_KILL, bot_id)
        if self.redis.is_connected:
            data = self.redis.json_get(key)
            return data is not None and data.get("active", False)
        return key in self._fallback

    # --- Trailing stops ---
    def set_trailing_high(self, bot_id: str, symbol: str, high: float):
        key = self._key(PREFIX_TRAILING, bot_id, symbol)
        if self.redis.is_connected:
            self.redis.set(key, str(high), ex=86400)
        else:
            self._fallback[key] = high

    def get_trailing_high(self, bot_id: str, symbol: str) -> Optional[float]:
        key = self._key(PREFIX_TRAILING, bot_id, symbol)
        if self.redis.is_connected:
            val = self.redis.get(key)
            return float(val) if val else None
        return self._fallback.get(key)

    # --- Metrics ---
    def increment_metric(self, bot_id: str, metric: str, amount: int = 1):
        key = self._key(PREFIX_METRICS, bot_id, metric)
        if self.redis.is_connected and self.redis.client:
            self.redis.client.incrby(key, amount)
        else:
            self._fallback[key] = self._fallback.get(key, 0) + amount

    def get_metrics(self, bot_id: str) -> dict:
        prefix = self._key(PREFIX_METRICS, bot_id)
        if self.redis.is_connected and self.redis.client:
            keys = self.redis.client.keys(f"{prefix}:*")
            result = {}
            for k in keys:
                metric_name = k.split(":")[-1]
                val = self.redis.client.get(k)
                result[metric_name] = int(val) if val else 0
            return result
        return {k.split(":")[-1]: v for k, v in self._fallback.items() if k.startswith(prefix)}
