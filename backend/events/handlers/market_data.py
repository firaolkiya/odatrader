"""Market data handler: ingest candles, compute features, emit FEATURES_READY."""
import logging
from typing import Any

import pandas as pd

from odatrade.core.event_bus_async import AsyncEventBus, Event, EventType
from odatrade.core.redis_state import RedisStateStore

logger = logging.getLogger("odatrade.handler.market_data")


class MarketDataHandler:
    def __init__(self, bot_id: str, config: dict, bus: AsyncEventBus, state: RedisStateStore):
        self.bot_id = bot_id
        self.config = config
        self.bus = bus
        self.state = state
        self._buffers: dict = {}

    async def handle(self, event: Event):
        symbol = event.payload.get("symbol")
        candle = event.payload.get("candle")
        if not symbol or not candle:
            return

        self._buffers.setdefault(symbol, []).append(candle)
        buf = self._buffers[symbol]
        if len(buf) > 200:
            buf.pop(0)

        if len(buf) < 30:
            return

        try:
            df = pd.DataFrame(buf)
            if "close" not in df.columns and "c" in df.columns:
                df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True)

            from backend.core.feature_engineering import compute_features
            featured = compute_features(df)
            featured = featured.dropna()

            if featured.empty:
                return

            latest = featured.iloc[-1].to_dict()
            self.state.increment_metric(self.bot_id, "candles_processed")

            await self.bus.emit(Event(
                type=EventType.FEATURES_READY,
                bot_id=self.bot_id,
                payload={
                    "symbol": symbol,
                    "features": latest,
                    "rows": len(featured),
                    "dataframe_tail": featured.tail(5).to_dict(orient="records"),
                },
                correlation_id=event.correlation_id,
            ))
        except Exception as e:
            logger.error("[%s] Feature engineering failed for %s: %s", self.bot_id, symbol, e)
            self.state.increment_metric(self.bot_id, "feature_errors")
