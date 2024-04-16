"""Cross-asset correlation monitor."""
import pandas as pd

def correlation_matrix(price_data: dict) -> pd.DataFrame:
    df = pd.DataFrame({sym: s["close"] for sym, s in price_data.items() if not s.empty})
    return df.pct_change().corr()

def high_correlation_pairs(corr: pd.DataFrame, threshold: float = 0.8) -> list:
    pairs = []
    for i, c1 in enumerate(corr.columns):
        for c2 in corr.columns[i+1:]:
            if abs(corr.loc[c1, c2]) > threshold:
                pairs.append((c1, c2, corr.loc[c1, c2]))
    return pairs
