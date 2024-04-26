"""Bridge between legacy scalping_bot_framework and new event-driven pipeline."""
import logging
import threading
from typing import Dict, Optional

logger = logging.getLogger("odatrade.legacy_bridge")


class LegacyBridge:
    """
    Connects the original scalping_bot_framework to the new OdaTrade
    event-driven architecture without breaking existing functionality.
    """

    def __init__(self, bot_manager=None):
        self.bot_manager = bot_manager
        self._legacy_running = False
        self._legacy_thread: Optional[threading.Thread] = None
        self._bot_id = "legacy-default"

    def start_legacy_bot(self, config: dict = None) -> dict:
        if self._legacy_running:
            return {"status": "already_running", "bot_id": self._bot_id}

        if self.bot_manager:
            from backend.bots.config import BotConfig
            bot_config = BotConfig(
                name="Legacy Bot",
                bot_id=self._bot_id,
                symbols=config.get("symbols", ["btcusdt", "ethusdt"]) if config else ["btcusdt"],
            )
            self.bot_manager.create_bot(bot_config)
            result = self.bot_manager.start_bot(self._bot_id)
            self._legacy_running = True
            return result

        self._legacy_thread = threading.Thread(target=self._run_legacy, daemon=True)
        self._legacy_thread.start()
        self._legacy_running = True
        return {"status": "started", "mode": "legacy_direct", "bot_id": self._bot_id}

    def _run_legacy(self):
        try:
            from scalping_bot_framework import run_bot
            run_bot()
        except Exception as e:
            logger.error("Legacy bot error: %s", e)
            self._legacy_running = False

    def stop_legacy_bot(self) -> dict:
        if self.bot_manager and self._legacy_running:
            self.bot_manager.stop_bot(self._bot_id)
        else:
            try:
                from scalping_bot_framework import stop_bot
                stop_bot()
            except Exception as e:
                logger.warning("Legacy stop error: %s", e)
        self._legacy_running = False
        return {"status": "stopped", "bot_id": self._bot_id}

    def get_status(self) -> dict:
        status = {"legacy_running": self._legacy_running, "bot_id": self._bot_id}
        if self.bot_manager:
            try:
                status.update(self.bot_manager.get_bot_status(self._bot_id))
            except Exception:
                pass
        return status

    def migrate_to_pipeline(self, bot_id: str) -> dict:
        """Migrate a legacy bot to the new event pipeline."""
        if not self.bot_manager:
            return {"error": "Bot manager not available"}
        config = self.bot_manager.registry.get(bot_id)
        if not config:
            return {"error": f"Bot {bot_id} not found"}
        self.stop_legacy_bot()
        self.bot_manager.start_bot(bot_id)
        return {"status": "migrated", "bot_id": bot_id, "pipeline": "event-driven"}


_bridge: Optional[LegacyBridge] = None


def get_legacy_bridge() -> LegacyBridge:
    global _bridge
    if _bridge is None:
        try:
            from backend.api.routes.bots_api import get_bot_manager
            _bridge = LegacyBridge(get_bot_manager())
        except Exception:
            _bridge = LegacyBridge()
    return _bridge
