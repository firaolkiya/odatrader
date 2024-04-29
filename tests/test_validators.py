import pytest
from odatrade.core.validators import (
    validate_symbol, validate_symbols, validate_interval,
    validate_risk_profile, validate_event_backend,
    validate_database_url, validate_redis_url,
)
from odatrade.core.exceptions import ConfigError

class TestValidators:
    def test_valid_symbol(self):
        assert validate_symbol("btcusdt") == "btcusdt"

    def test_invalid_symbol(self):
        with pytest.raises(ConfigError):
            validate_symbol("INVALID")

    def test_validate_symbols(self):
        assert len(validate_symbols(["btcusdt", "ethusdt"])) == 2

    def test_empty_symbols(self):
        with pytest.raises(ConfigError):
            validate_symbols([])

    @pytest.mark.parametrize("interval", ["1m","5m","15m","1h","4h","1d"])
    def test_valid_intervals(self, interval):
        assert validate_interval(interval) == interval

    def test_invalid_interval(self):
        with pytest.raises(ConfigError):
            validate_interval("2m")

    @pytest.mark.parametrize("profile", ["conservative","moderate","aggressive"])
    def test_risk_profiles(self, profile):
        assert validate_risk_profile(profile) == profile

    @pytest.mark.parametrize("backend", ["redis","kafka","nats","memory"])
    def test_event_backends(self, backend):
        assert validate_event_backend(backend) == backend

    def test_postgres_url(self):
        ok, _ = validate_database_url("postgresql://user:pass@host/db")
        assert ok

    def test_sqlite_url(self):
        ok, _ = validate_database_url("sqlite:///test.db")
        assert ok

    def test_redis_url(self):
        ok, _ = validate_redis_url("redis://localhost:6379/0")
        assert ok
