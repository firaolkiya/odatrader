import pytest
from backend.core.signals import SignalVote, SignalSnapshot, TradeIntent, Quote, Bar

class TestSignalVote:
    def test_bullish(self):
        v = SignalVote("rsi", 1, 0.15, "oversold")
        assert v.value == 1

    def test_to_dict(self):
        v = SignalVote("macd", -1, 0.2)
        d = v.to_dict()
        assert d["name"] == "macd"

class TestSignalSnapshot:
    def test_create(self):
        s = SignalSnapshot("2025-01-01", "btcusdt", [], 0.6, 0.2, 0.6, 0.5, 0.55, 0.45)
        assert s.instrument == "btcusdt"

    def test_to_dict(self):
        s = SignalSnapshot("2025-01-01", "btcusdt", [SignalVote("rsi",1,0.15)], 0.7, 0.1, 0.7, 0.5, 0.6, 0.5, action="BUY")
        d = s.to_dict()
        assert d["action"] == "BUY"

    def test_to_json(self):
        s = SignalSnapshot("2025-01-01", "btcusdt", [], 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
        assert "btcusdt" in s.to_json()

class TestTradeIntent:
    def test_create(self):
        t = TradeIntent("2025-01-01", "btcusdt", "BUY", 0.1, px_hint=50000)
        assert t.side == "BUY"

    def test_post_only(self):
        t = TradeIntent("2025-01-01", "btcusdt", "BUY", 0.1, post_only=True)
        assert t.post_only

class TestQuote:
    def test_create(self):
        q = Quote(1.0, 100.0, 100.1, 10, 10, "btcusdt")
        assert q.bid == 100.0

class TestBar:
    def test_create(self):
        b = Bar(1.0, 100, 101, 99, 100.5, 500, "1m", "btcusdt")
        assert b.c == 100.5
