"""News and sentiment API routes."""
from fastapi import APIRouter, Depends
from typing import List, Optional

from backend.auth.middleware import require_auth
from config.config import GROQ_API_KEY

router = APIRouter(prefix="/news", tags=["news"])

_ingestor = None


def get_ingestor():
    global _ingestor
    if _ingestor is None:
        from backend.news.llm_ingestion import LLMNewsIngestor
        _ingestor = LLMNewsIngestor(groq_api_key=GROQ_API_KEY)
    return _ingestor


@router.get("/feed")
def get_news_feed(symbols: Optional[str] = "BTC,ETH"):
    ingestor = get_ingestor()
    sym_list = [s.strip() for s in symbols.split(",")]
    return ingestor.ingest_and_analyze(sym_list)


@router.get("/cached")
def get_cached_news():
    ingestor = get_ingestor()
    return {"articles": ingestor.get_cached()}


@router.get("/sentiment")
def get_aggregate_sentiment(symbols: Optional[str] = "BTC,ETH"):
    ingestor = get_ingestor()
    sym_list = [s.strip() for s in symbols.split(",")]
    result = ingestor.ingest_and_analyze(sym_list)
    return {
        "avg_sentiment": result["avg_sentiment"],
        "signal": result["aggregate_signal"],
        "article_count": result["count"],
    }
