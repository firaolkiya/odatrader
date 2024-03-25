import os
import sys
import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import create_engine
from typing import Dict, Any
from groq import Groq

# === Add root to path for imports ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import DATABASE_URL, GROQ_API_KEY
from backend.sentiments.reddit_scraper import fetch_reddit_sentiment


class GPTSentimentStrategy:
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.db_url = f"{DATABASE_URL}"
        self.client = Groq(api_key=GROQ_API_KEY)

    def get_latest_price(self) -> tuple[float | None, datetime | None]:
        try:
            engine = create_engine(self.db_url)
            query = f"""
                SELECT close, timestamp 
                FROM market_data 
                WHERE symbol = '{self.symbol.lower()}' 
                ORDER BY timestamp DESC 
                LIMIT 1
            """
            df = pd.read_sql(query, engine)
            if df.empty:
                return None, None
            return df['close'].iloc[0], df['timestamp'].iloc[0]
        except Exception as e:
            print(f"[GPT-STRATEGY] DB Error: {e}")
            return None, None

    def fetch_sentiments(self) -> str:
        try:
            reddit_sentiment = fetch_reddit_sentiment(self.symbol)
        except Exception as e:
            reddit_sentiment = "unknown"
            print(f"[GPT-STRATEGY] Reddit sentiment error: {e}")
        return reddit_sentiment

    def generate_prompt(
        self,
        price: float,
        timestamp: datetime,
        reddit_sentiment: str
    ) -> str:
        return f"""
You are a crypto trading assistant.

Symbol: {self.symbol}
Current Price: {price}
Timestamp: {timestamp}

Reddit Sentiment: {reddit_sentiment}

Based on the price and social sentiment, should we BUY, SELL, or HOLD {self.symbol}?
Respond with only one word: BUY, SELL, or HOLD.
"""

    def generate_signal(self) -> str | None:
        price, timestamp = self.get_latest_price()
        if price is None:
            print(f"[GPT-STRATEGY] No price found for {self.symbol}")
            return None

        reddit_sentiment = self.fetch_sentiments()
        prompt = self.generate_prompt(price, timestamp, reddit_sentiment)

        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            decision = response.choices[0].message.content.strip().upper()
            print(f"[GPT-STRATEGY] Decision for {self.symbol}: {decision}")
            return decision
        except Exception as e:
            print(f"[GPT-STRATEGY] Groq API error: {e}")
            return None

    def evaluate(self, market_data: pd.DataFrame | Any) -> Dict[str, str]:
        """
        Evaluate method to align with other strategies
        :param market_data: DataFrame passed for compatibility, not used here
        :return: signal decision
        """
        signal = self.generate_signal()
        return {"symbol": self.symbol, "signal": signal or "UNKNOWN"}
if __name__ == "__main__":
    strategy = GPTSentimentStrategy("BTCUSDT")
    result = strategy.evaluate(None)
    print(result)
