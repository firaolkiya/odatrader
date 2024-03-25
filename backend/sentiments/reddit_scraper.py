import os
import sys
import nltk
import praw  # Changed from asyncpraw to praw
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Add config path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config.config import REDDIT_CLIENT_ID, REDDIT_SECRET_KEY

# Download vader lexicon (only the first time)
nltk.download('vader_lexicon', quiet=True)

# Initialize VADER once globally
vader_analyzer = SentimentIntensityAnalyzer()

def fetch_reddit_sentiment(keyword: str, limit: int = 3) -> float:
    """Synchronous version of Reddit sentiment analysis"""
    try:
        if not REDDIT_CLIENT_ID or not REDDIT_SECRET_KEY:
            print("[Reddit] API credentials not configured")
            return 0.0

        # Initialize synchronous Reddit instance
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_SECRET_KEY,
            user_agent="Crypto_Project"
        )

        sentiments = []
        subreddit = reddit.subreddit("CryptoCurrency")
        
        # Synchronous search
        for submission in subreddit.search(keyword, limit=limit):
            content = f"{submission.title} {submission.selftext}"
            score = vader_analyzer.polarity_scores(content)["compound"]
            sentiments.append(score)

        return sum(sentiments) / len(sentiments) if sentiments else 0.0

    except Exception as e:
        print(f"[Reddit] Sentiment fetch error: {e}")
        return 0.0

# Keep the same interface for compatibility
get_reddit_sentiment_sync_safe = fetch_reddit_sentiment

# Test
if __name__ == "__main__":
    print("Testing Reddit Sentiment Fetch...")
    score = fetch_reddit_sentiment("btcusdt")
    print(f"Sentiment Score: {score:.4f}")