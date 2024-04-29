import pytest
from odatrade.core.event_bus_async import Event, EventType
from backend.events.idempotency import EventDeduplicator


class TestEventDeduplicator:
    def test_first_not_duplicate(self):
        d = EventDeduplicator()
        e = Event(EventType.RISK_APPROVED, "b1", {"symbol": "btc"}, correlation_id="c1")
        assert not d.is_duplicate(e)

    def test_second_is_duplicate(self):
        d = EventDeduplicator()
        e = Event(EventType.RISK_APPROVED, "b1", {"symbol": "btc"}, correlation_id="c1")
        d.mark(e)
        assert d.is_duplicate(e)

    def test_different_correlation_not_duplicate(self):
        d = EventDeduplicator()
        d.mark(Event(EventType.RISK_APPROVED, "b1", {}, correlation_id="c1"))
        e2 = Event(EventType.RISK_APPROVED, "b1", {}, correlation_id="c2")
        assert not d.is_duplicate(e2)

    def test_ignores_types_without_correlation(self):
        d = EventDeduplicator()
        e = Event(EventType.MARKET_DATA, "b1", {"price": 1})
        assert d.make_key(e) is None
