import pytest
from backend.engine.adaptive_voter import AdaptiveVoter

@pytest.fixture
def voter():
    return AdaptiveVoter("btcusdt")

class TestAdaptiveVoter:
    def test_init(self, voter):
        assert voter.symbol == "btcusdt"

    def test_default_config(self, voter):
        assert voter.config["base_entry"] == 0.70

    def test_evaluate_returns_snapshot(self, voter, sample_ohlcv_df):
        snap = voter.evaluate(sample_ohlcv_df)
        assert snap.instrument == "btcusdt"
        assert snap.action in ("BUY","SELL","HOLD")

    def test_bull_share_bounded(self, voter, sample_ohlcv_df):
        snap = voter.evaluate(sample_ohlcv_df)
        assert 0 <= snap.bull_share <= 1

    def test_bear_share_bounded(self, voter, sample_ohlcv_df):
        snap = voter.evaluate(sample_ohlcv_df)
        assert 0 <= snap.bear_share <= 1

    def test_regime_in_snapshot(self, voter, sample_ohlcv_df):
        snap = voter.evaluate(sample_ohlcv_df)
        assert 0 <= snap.regime <= 1

    def test_thresholds_present(self, voter, sample_ohlcv_df):
        snap = voter.evaluate(sample_ohlcv_df)
        assert snap.entry_threshold > 0
        assert snap.exit_threshold > 0

    def test_votes_list(self, voter, sample_ohlcv_df):
        snap = voter.evaluate(sample_ohlcv_df)
        assert isinstance(snap.votes, list)

    def test_to_dict(self, voter, sample_ohlcv_df):
        d = voter.evaluate(sample_ohlcv_df).to_dict()
        assert "votes" in d and "action" in d

    def test_calm_higher_entry_threshold(self, voter):
        cfg = voter.config.copy()
        voter.config = cfg
        entry_calm = cfg["base_entry"] - cfg["entry_slope"] * 0
        entry_vol = cfg["base_entry"] - cfg["entry_slope"] * 1
        assert entry_calm > entry_vol

    def test_vote_from_result_buy(self, voter):
        assert voter._vote_from_result({"action": "BUY"}) == 1

    def test_vote_from_result_sell(self, voter):
        assert voter._vote_from_result({"action": "SELL"}) == -1

    def test_vote_from_result_hold(self, voter):
        assert voter._vote_from_result({"action": "HOLD"}) == 0

    def test_vote_from_none(self, voter):
        assert voter._vote_from_result(None) == 0

    def test_custom_config(self):
        v = AdaptiveVoter("ethusdt", {"base_entry": 0.8, "base_exit": 0.4, "entry_slope": 0.1, "exit_slope": 0.05, "weights": {}})
        snap = v.evaluate(__import__("pandas").DataFrame({"close": range(50), "high": range(50), "low": range(50), "volume": range(50)}))
        expected = 0.8 - 0.1 * snap.regime
        assert snap.entry_threshold == pytest.approx(expected, abs=0.01)

    @pytest.mark.parametrize("symbol", ["btcusdt","ethusdt","AAPL","EURUSD"])
    def test_multi_symbol(self, symbol, sample_ohlcv_df):
        v = AdaptiveVoter(symbol)
        snap = v.evaluate(sample_ohlcv_df)
        assert snap.instrument == symbol

    def test_reason_not_empty(self, voter, sample_ohlcv_df):
        snap = voter.evaluate(sample_ohlcv_df)
        assert len(snap.reason) > 0

    def test_ts_present(self, voter, sample_ohlcv_df):
        snap = voter.evaluate(sample_ohlcv_df)
        assert snap.ts is not None
