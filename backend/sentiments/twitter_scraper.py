import snscrape.modules.twitter as sntwitter
from textblob import TextBlob

def fetch_twitter_sentiment(keyword, limit=50):
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{keyword} lang:en').get_items()):
        if i >= limit:
            break
        sentiment = TextBlob(tweet.content).sentiment.polarity
        tweets.append(sentiment)

    if not tweets:
        return 0.0
    return sum(tweets) / len(tweets)

