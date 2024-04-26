"""Bot registry for multi-bot management."""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.bots.config import BotConfig
from odatrade.core.redis_state import RedisStateStore

logger = logging.getLogger("odatrade.bot_registry")

PREFIX = "odatrade:registry:"


class BotRegistry:
    """Central registry tracking all bot instances across the platform."""

    def __init__(self, state_store: RedisStateStore = None):
        self.state = state_store or RedisStateStore()
        self._local: Dict[str, BotConfig] = {}

    def register(self, config: BotConfig) -> BotConfig:
        self._local[config.bot_id] = config
        key = f"{PREFIX}{config.bot_id}"
        data = {
            "config": config.to_dict(),
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "status": "registered",
        }
        if self.state.redis.is_connected:
            self.state.redis.json_set(key, data)
        logger.info("Bot registered: %s (%s)", config.bot_id, config.name)
        return config

    def unregister(self, bot_id: str) -> bool:
        if bot_id not in self._local:
            return False
        del self._local[bot_id]
        key = f"{PREFIX}{bot_id}"
        if self.state.redis.is_connected:
            self.state.redis.delete(key)
        return True

    def get(self, bot_id: str) -> Optional[BotConfig]:
        if bot_id in self._local:
            return self._local[bot_id]
        key = f"{PREFIX}{bot_id}"
        if self.state.redis.is_connected:
            data = self.state.redis.json_get(key)
            if data and "config" in data:
                return BotConfig.from_dict(data["config"])
        return None

    def list_all(self) -> List[dict]:
        bots = []
        for bot_id, config in self._local.items():
            status = self.state.get_bot_status(bot_id) or {"status": "unknown"}
            bots.append({
                "bot_id": bot_id,
                "name": config.name,
                "symbols": config.symbols,
                "strategy": config.strategy,
                "risk_profile": config.risk_profile,
                "status": status.get("status", "unknown"),
            })
        return bots

    def update_status(self, bot_id: str, status: str, metadata: dict = None):
        self.state.set_bot_status(bot_id, status, metadata)
