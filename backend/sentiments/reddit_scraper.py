import os
import sys
import asyncio
from textblob import TextBlob
import asyncpraw

# Add config path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config.config import REDDIT_CLIENT_ID, REDDIT_SECRET_KEY

# Async function
async def fetch_reddit_sentiment(keyword: str, limit: int = 50) -> float:
    try:
        reddit = asyncpraw.Reddit(
            client_id=f"{REDDIT_CLIENT_ID}",
            client_secret=f"{REDDIT_SECRET_KEY}",
            user_agent="Crypto_Project"
        )

        sentiments = []
        subreddit = await reddit.subreddit("CryptoCurrency")

        async for submission in subreddit.search(keyword, limit=limit):
            content = submission.title + " " + submission.selftext
            polarity = TextBlob(content).sentiment.polarity
            sentiments.append(polarity)

        await reddit.close()

        return sum(sentiments) / len(sentiments) if sentiments else 0.0

    except Exception as e:
        print(f"[Reddit] Sentiment fetch error: {e}")
        return 0.0

# Safe wrapper for synchronous use
def get_reddit_sentiment_sync_safe(keyword: str, limit: int = 50) -> float:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.ensure_future(fetch_reddit_sentiment(keyword, limit))
        else:
            return loop.run_until_complete(fetch_reddit_sentiment(keyword, limit))
    except RuntimeError:
        return asyncio.run(fetch_reddit_sentiment(keyword, limit))

# Test
if __name__ == "__main__":
    print("Testing Reddit Sentiment Fetch...")
    score = asyncio.run(fetch_reddit_sentiment("BTCUSDT"))
    print(f"Sentiment Score: {score:.4f}")
