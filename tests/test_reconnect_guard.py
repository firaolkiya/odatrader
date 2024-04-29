import pytest
from backend.gateway.reconnect_guard import StaleQuoteGuard


class TestStaleQuoteGuard:
    def test_accepts_fresh_quote(self):
        g = StaleQuoteGuard(max_age_sec=5.0)
        assert g.accept_quote(100.0, now_ts=102.0)

    def test_rejects_stale_quote(self):
        g = StaleQuoteGuard(max_age_sec=5.0)
        assert not g.accept_quote(90.0, now_ts=100.0)
        assert g.dropped_count == 1

    def test_grace_period_after_reconnect(self):
        g = StaleQuoteGuard(grace_after_reconnect_sec=10.0)
        g.on_disconnect(100.0)
        g.on_reconnect(105.0)
        assert not g.accept_quote(104.0, now_ts=106.0)

    def test_rejects_pre_disconnect_quotes(self):
        g = StaleQuoteGuard()
        g.on_disconnect(200.0)
        g.on_reconnect(210.0)
        assert g.accept_quote(199.0, now_ts=220.0) is False
