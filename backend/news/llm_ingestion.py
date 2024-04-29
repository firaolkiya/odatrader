"""LLM-based news ingestion for real-time sentiment analysis."""
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger("odatrade.news")


class NewsArticle:
    def __init__(self, title: str, source: str, url: str = "", summary: str = "", published_at: str = ""):
        self.title = title
        self.source = source
        self.url = url
        self.summary = summary
        self.published_at = published_at or datetime.now(timezone.utc).isoformat()
        self.sentiment: Optional[float] = None
        self.signal: str = "HOLD"

    def to_dict(self) -> dict:
        return {
            "title": self.title, "source": self.source, "url": self.url,
            "summary": self.summary, "published_at": self.published_at,
            "sentiment": self.sentiment, "signal": self.signal,
        }


class LLMNewsIngestor:
    """
    Fetches crypto news and analyzes sentiment using Groq LLM.
    Feeds results into the trading event pipeline.
    """

    CRYPTO_NEWS_FEEDS = [
        "https://cryptopanic.com/api/v1/posts/?auth_token=free&currencies=BTC,ETH&filter=hot",
    ]

    def __init__(self, groq_api_key: str = "", model: str = "llama-3.1-8b-instant"):
        self.groq_api_key = groq_api_key
        self.model = model
        self._cache: List[NewsArticle] = []
        self._last_fetch = 0
        self._fetch_interval = 300

    def fetch_news(self, symbols: List[str] = None) -> List[NewsArticle]:
        articles = []
        for symbol in (symbols or ["BTC", "ETH"]):
            articles.extend(self._fetch_cryptopanic(symbol))
        self._cache = articles[:50]
        self._last_fetch = time.time()
        return articles

    def _fetch_cryptopanic(self, symbol: str) -> List[NewsArticle]:
        articles = []
        try:
            url = f"https://cryptopanic.com/api/v1/posts/?currencies={symbol}&filter=hot"
            resp = httpx.get(url, timeout=10)
            if resp.status_code != 200:
                return articles
            data = resp.json()
            for post in data.get("results", [])[:10]:
                articles.append(NewsArticle(
                    title=post.get("title", ""),
                    source=post.get("source", {}).get("title", "unknown"),
                    url=post.get("url", ""),
                    published_at=post.get("published_at", ""),
                ))
        except Exception as e:
            logger.warning("News fetch failed for %s: %s", symbol, e)
        return articles

    def analyze_sentiment(self, article: NewsArticle) -> NewsArticle:
        if not self.groq_api_key:
            article.sentiment = self._rule_based_sentiment(article.title)
            article.signal = self._sentiment_to_signal(article.sentiment)
            return article

        try:
            prompt = (
                f"Analyze this crypto news headline for trading sentiment. "
                f"Respond with ONLY one word: BULLISH, BEARISH, or NEUTRAL.\n\n"
                f"Headline: {article.title}"
            )
            resp = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.groq_api_key}"},
                json={"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 10},
                timeout=15,
            )
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"].strip().upper()
                if "BULLISH" in text:
                    article.sentiment = 0.8
                    article.signal = "BUY"
                elif "BEARISH" in text:
                    article.sentiment = -0.8
                    article.signal = "SELL"
                else:
                    article.sentiment = 0.0
                    article.signal = "HOLD"
            else:
                article.sentiment = self._rule_based_sentiment(article.title)
                article.signal = self._sentiment_to_signal(article.sentiment)
        except Exception as e:
            logger.warning("LLM sentiment failed: %s", e)
            article.sentiment = self._rule_based_sentiment(article.title)
            article.signal = self._sentiment_to_signal(article.sentiment)
        return article

    def _rule_based_sentiment(self, text: str) -> float:
        bullish = ["surge", "rally", "bull", "moon", "breakout", "ath", "adoption", "upgrade"]
        bearish = ["crash", "dump", "bear", "hack", "ban", "lawsuit", "sec", "fraud"]
        text_lower = text.lower()
        score = sum(1 for w in bullish if w in text_lower) - sum(1 for w in bearish if w in text_lower)
        return max(-1.0, min(1.0, score * 0.3))

    def _sentiment_to_signal(self, sentiment: float) -> str:
        if sentiment > 0.3:
            return "BUY"
        if sentiment < -0.3:
            return "SELL"
        return "HOLD"

    def ingest_and_analyze(self, symbols: List[str] = None) -> Dict:
        articles = self.fetch_news(symbols)
        analyzed = [self.analyze_sentiment(a) for a in articles]
        sentiments = [a.sentiment for a in analyzed if a.sentiment is not None]
        avg = sum(sentiments) / len(sentiments) if sentiments else 0
        return {
            "articles": [a.to_dict() for a in analyzed],
            "count": len(analyzed),
            "avg_sentiment": avg,
            "aggregate_signal": self._sentiment_to_signal(avg),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_cached(self) -> List[dict]:
        return [a.to_dict() for a in self._cache]
