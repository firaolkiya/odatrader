import pytest

class TestSymbolManager:
    def test_add_remove(self):
        from backend.core.symbol_manager import SymbolManager
        sm = SymbolManager(["btcusdt"])
        sm.add("ethusdt")
        assert sm.is_watched("ethusdt")
        sm.remove("btcusdt")
        assert not sm.is_watched("btcusdt")

    def test_list(self):
        from backend.core.symbol_manager import SymbolManager
        sm = SymbolManager(["btcusdt", "ethusdt"])
        assert len(sm.list_all()) == 2

class TestHealthMonitor:
    def test_heartbeat(self):
        from backend.monitoring.health_monitor import HealthMonitor
        hm = HealthMonitor()
        hm.heartbeat()
        assert hm.is_healthy()

    def test_errors(self):
        from backend.monitoring.health_monitor import HealthMonitor
        hm = HealthMonitor()
        for i in range(15):
            hm.record_error(f"err{i}")
        assert not hm.is_healthy()

class TestStrategyPerformance:
    def test_record(self):
        from backend.analytics.strategy_performance import StrategyPerformanceTracker
        t = StrategyPerformanceTracker()
        t.record("rsi", 10)
        t.record("rsi", -5)
        s = t.get_stats("rsi")
        assert s["wins"] == 1 and s["losses"] == 1

class TestTradeJournal:
    def test_add_search(self):
        from backend.journal.trade_journal import TradeJournal
        j = TradeJournal()
        j.add("t1", "btcusdt", "good trade", ["scalp"])
        assert len(j.search("btcusdt")) == 1

class TestAlertRules:
    def test_drawdown_alert(self):
        from backend.alerts.rules import drawdown_alert
        rule = drawdown_alert(0.1)
        assert rule({"drawdown": 0.15})
        assert not rule({"drawdown": 0.05})

    def test_price_alert(self):
        from backend.alerts.rules import price_alert
        rule = price_alert("btcusdt", 50000, "above")
        assert rule({"symbol": "btcusdt", "price": 51000})

class TestConfigLoader:
    def test_load_missing(self):
        from odatrade.core.config_loader import load_strategy_config
        assert load_strategy_config("/nonexistent/path.yaml") == {}

class TestPrometheusExporter:
    def test_render(self):
        from backend.monitoring.prometheus_exporter import render_metrics, increment
        increment("trades_total", 5)
        output = render_metrics()
        assert "odatrade_trades_total" in output
