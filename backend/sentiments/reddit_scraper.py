import praw
from textblob import TextBlob
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config.config import REDDIT_CLIENT_ID, REDDIT_SECRET_KEY
reddit = praw.Reddit(
    client_id=f"{REDDIT_CLIENT_ID}",
    client_secret=f"{REDDIT_SECRET_KEY}",
    user_agent="Crypto Project"
)

def fetch_reddit_sentiment(keyword, limit=50):
    sentiments = []
    for submission in reddit.subreddit("CryptoCurrency").search(keyword, limit=limit):
        content = submission.title + " " + submission.selftext
        polarity = TextBlob(content).sentiment.polarity
        sentiments.append(polarity)

    if not sentiments:
        return 0.0
    return sum(sentiments) / len(sentiments)
if __name__ == "__main__":
    
    result = fetch_reddit_sentiment("BTCUSDT")
    print(result)