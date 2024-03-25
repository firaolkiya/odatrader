import datetime
import httpx
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db.market_data import get_latest_price
from backend.sentiments.reddit_scraper import get_reddit_sentiment_sync_safe
from config.config import GROQ_API_KEY

def generate_prompt(symbol: str, price: float, sentiment: float, timestamp: str) -> str:
    return f"""
You are a crypto trading assistant.
Given the following data:

- Symbol: {symbol}
- Price: {price}
- Sentiment Score: {sentiment}
- Timestamp: {timestamp}

Make a trading decision: BUY, SELL, or HOLD. Keep it in one word only.
"""

def evaluate(symbol: str):
    try:
        price_data = get_latest_price(symbol)
        if not price_data:
            return {"symbol": symbol, "decision": "HOLD", "reason": "No market data."}

        price = price_data['price']
        timestamp = price_data['timestamp']

        sentiment = get_reddit_sentiment_sync_safe(symbol)
        if hasattr(sentiment, "__await__"):  # Awaitable check (FastAPI etc.)
            import asyncio
            sentiment = asyncio.run(sentiment)

        prompt = generate_prompt(symbol, price, sentiment, timestamp)

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You're a crypto trading expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        with httpx.Client(timeout=20.0) as client:
            res = client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
            res.raise_for_status()
            decision = res.json()["choices"][0]["message"]["content"].strip().upper()
            if decision not in ["BUY", "SELL", "HOLD"]:
                decision = "HOLD"

        return {
            "symbol": symbol,
            "decision": decision,
            "price": price,
            "sentiment": sentiment,
            "timestamp": timestamp
        }

    except Exception as e:
        return {"symbol": symbol, "decision": "HOLD", "error": str(e)}

if __name__ == "__main__":
    print(evaluate("BTCUSDT"))
