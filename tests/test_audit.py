import pytest
from backend.audit.decision_logger import DecisionLogger
from backend.core.signals import SignalSnapshot, SignalVote

class TestDecisionLogger:
    @pytest.fixture
    def logger(self, tmp_path):
        return DecisionLogger(log_dir=str(tmp_path))

    def test_log_signal(self, logger):
        snap = SignalSnapshot("2025", "btc", [], 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
        logger.log_signal(snap)
        assert len(logger._buffer) == 1

    def test_log_reject(self, logger):
        from backend.core.signals import TradeIntent
        intent = TradeIntent("2025", "btc", "BUY", 0.1)
        logger.log_reject(intent, "risk limit")
        assert logger._buffer[0]["type"] == "reject"

    def test_flush(self, logger, tmp_path):
        logger.log_reject(__import__("backend.core.signals", fromlist=["TradeIntent"]).TradeIntent("t","b","BUY",1), "test")
        logger.flush()
        assert len(logger._buffer) == 0
