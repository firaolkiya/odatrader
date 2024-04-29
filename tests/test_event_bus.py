import pytest
import asyncio
from odatrade.core.event_bus_async import (
    Event, EventType, InMemoryBackend, AsyncEventBus,
)

class TestEvent:
    def test_create(self):
        e = Event(EventType.MARKET_DATA, "bot1", {"symbol": "btc"})
        assert e.bot_id == "bot1"

    def test_to_dict(self):
        e = Event(EventType.PNL_UPDATE, "b1", {"pnl": 10})
        d = e.to_dict()
        assert d["type"] == "pnl_update"

    def test_roundtrip_json(self):
        e = Event(EventType.STRATEGY_SIGNAL, "b1", {"signal": "BUY"})
        e2 = Event.from_json(e.to_json())
        assert e2.type == EventType.STRATEGY_SIGNAL

class TestInMemoryBackend:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        backend = InMemoryBackend()
        received = []
        await backend.subscribe(EventType.MARKET_DATA, lambda e: received.append(e))
        await backend.start()
        e = Event(EventType.MARKET_DATA, "b1", {"price": 100})
        await backend.publish(e)
        assert len(received) == 1

class TestAsyncEventBus:
    @pytest.mark.asyncio
    async def test_emit(self):
        bus = AsyncEventBus()
        received = []
        bus.on(EventType.PNL_UPDATE, lambda e: received.append(e))
        await bus.start()
        await bus.emit(Event(EventType.PNL_UPDATE, "b1", {"pnl": 5}))
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_emit_market_data(self):
        bus = AsyncEventBus()
        await bus.start()
        result = await bus.emit_market_data("b1", "btc", {"c": 100})
        assert result
