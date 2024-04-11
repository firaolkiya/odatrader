"""Reddit sentiment analyzer stub."""
from typing import List

def analyze_posts(posts: List[str]) -> float:
    positive = sum(1 for p in posts if any(w in p.lower() for w in ["bull", "moon", "buy", "long"]))
    negative = sum(1 for p in posts if any(w in p.lower() for w in ["bear", "dump", "sell", "short"]))
    total = len(posts) or 1
    return (positive - negative) / total
