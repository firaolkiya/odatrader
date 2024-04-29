import pytest
from backend.sentiment.reddit_analyzer import analyze_posts
from backend.sentiment.scorer import composite_score

class TestRedditAnalyzer:
    def test_bullish_posts(self):
        posts = ["BTC to the moon!", "bullish on ETH", "buy the dip"]
        score = analyze_posts(posts)
        assert score > 0

    def test_bearish_posts(self):
        posts = ["bear market incoming", "sell everything", "crash imminent"]
        score = analyze_posts(posts)
        assert score < 0

    def test_empty(self):
        assert analyze_posts([]) == 0

    def test_mixed(self):
        posts = ["bull run", "bear dump"]
        score = analyze_posts(posts)
        assert -1 <= score <= 1

class TestCompositeScorer:
    def test_bullish(self):
        r = composite_score({"reddit": 0.5, "news": 0.3})
        assert r["signal"] == "BUY"

    def test_bearish(self):
        r = composite_score({"reddit": -0.5, "news": -0.4})
        assert r["signal"] == "SELL"

    def test_neutral(self):
        r = composite_score({"reddit": 0.1})
        assert r["signal"] == "HOLD"
