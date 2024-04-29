import pytest
from backend.engine.pair_scorer import PairScorer, PairMetadata, pair_score, normalize

class TestNormalize:
    @pytest.mark.parametrize("x,xmax,expected", [(5,10,0.5),(0,10,0.0),(10,10,1.0),(15,10,1.0),(-1,10,0.0)])
    def test_normalize(self, x, xmax, expected):
        assert normalize(x, xmax) == pytest.approx(expected, abs=0.01)

class TestPairScore:
    def test_high_liquidity_scores_high(self):
        meta = PairMetadata("BTC", volume=1e9, spread=0.0001, vol=0.02, depth=50000)
        s = pair_score(meta, {"volume":1e9,"spread":0.01,"vol":2,"depth":100000,"funding_rate":0.001},
                       {"liq":0.3,"spread":0.25,"vol":0.2,"depth":0.15,"corr":0.1})
        assert s > 0.5

    def test_wide_spread_scores_lower(self):
        good = PairMetadata("A", volume=1e8, spread=0.0001, vol=0.02, depth=10000)
        bad = PairMetadata("B", volume=1e8, spread=0.05, vol=0.02, depth=10000)
        maxima = {"volume":1e9,"spread":0.01,"vol":2,"depth":100000,"funding_rate":0.001}
        weights = {"liq":0.3,"spread":0.25,"vol":0.2,"depth":0.15,"corr":0.1}
        assert pair_score(good, maxima, weights) > pair_score(bad, maxima, weights)

    def test_score_bounded(self):
        meta = PairMetadata("X", volume=1, spread=1, vol=10, depth=1)
        s = pair_score(meta, {"volume":1e9,"spread":0.01,"vol":2,"depth":100000,"funding_rate":0.001},
                       {"liq":0.3,"spread":0.25,"vol":0.2,"depth":0.15,"corr":0.1})
        assert 0 <= s <= 1

    def test_negative_funding_penalty(self):
        meta = PairMetadata("P", volume=1e8, spread=0.001, vol=0.02, depth=10000, funding_rate=-0.01)
        meta2 = PairMetadata("P", volume=1e8, spread=0.001, vol=0.02, depth=10000, funding_rate=0)
        maxima = {"volume":1e9,"spread":0.01,"vol":2,"depth":100000,"funding_rate":0.001}
        weights = {"liq":0.3,"spread":0.25,"vol":0.2,"depth":0.15,"corr":0.1}
        assert pair_score(meta, maxima, weights) >= pair_score(meta2, maxima, weights)

class TestPairScorer:
    @pytest.fixture
    def scorer(self):
        return PairScorer()

    def test_update_metadata(self, scorer):
        scorer.update_metadata("BTC", volume=1e9)
        assert "BTC" in scorer._metadata

    def test_score_all_empty(self, scorer):
        assert scorer.score_all() == []

    def test_score_all_with_data(self, scorer):
        scorer.update_metadata("BTC", volume=1e9, spread=0.0005)
        scorer.update_metadata("ETH", volume=5e8, spread=0.001)
        results = scorer.score_all()
        assert len(results) == 2

    def test_get_top_k(self, scorer):
        for sym, vol in [("A",1e9),("B",5e8),("C",1e7)]:
            scorer.update_metadata(sym, volume=vol, spread=0.0005, vol=0.02, depth=10000)
        top = scorer.get_top_k()
        assert len(top) <= 3

    def test_selected_flag(self, scorer):
        scorer.update_metadata("BTC", volume=1e9, spread=0.0001, vol=0.02, depth=50000)
        results = scorer.score_all()
        assert any(r["selected"] for r in results)

    @pytest.mark.parametrize("symbol", ["BTCUSDT","ETHUSDT","EURUSD","AAPL"])
    def test_multiple_symbols(self, scorer, symbol):
        scorer.update_metadata(symbol, volume=1e8, spread=0.001, vol=0.02, depth=5000)
        assert scorer.score_all()[0]["symbol"] == symbol
