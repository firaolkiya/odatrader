import pytest
from backend.bots.config import BotConfig, apply_risk_profile, RISK_PROFILES
from backend.bots.registry import BotRegistry

class TestBotConfig:
    def test_create(self):
        c = BotConfig(name="Test Bot", symbols=["btcusdt"])
        assert c.name == "Test Bot"

    def test_to_dict(self):
        c = BotConfig(name="B", symbols=["ethusdt"])
        assert "name" in c.to_dict()

    def test_from_dict(self):
        c = BotConfig.from_dict({"name": "X", "symbols": ["btcusdt"], "bot_id": "abc"})
        assert c.bot_id == "abc"

    def test_has_bot_id(self):
        c = BotConfig(name="B")
        assert c.bot_id is not None

class TestRiskProfiles:
    @pytest.mark.parametrize("profile", ["conservative","moderate","aggressive"])
    def test_apply(self, profile):
        c = BotConfig(name="T", risk_profile=profile)
        c = apply_risk_profile(c)
        assert c.max_drawdown == RISK_PROFILES[profile]["max_drawdown"]

class TestBotRegistry:
    @pytest.fixture
    def registry(self):
        return BotRegistry()

    def test_register(self, registry):
        c = BotConfig(name="Bot1", symbols=["btcusdt"])
        registry.register(c)
        assert registry.get(c.bot_id) is not None

    def test_unregister(self, registry):
        c = BotConfig(name="Bot2")
        registry.register(c)
        assert registry.unregister(c.bot_id)

    def test_list_all(self, registry):
        registry.register(BotConfig(name="A"))
        registry.register(BotConfig(name="B"))
        assert len(registry.list_all()) == 2
