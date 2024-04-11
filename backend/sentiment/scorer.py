"""Composite sentiment scorer."""

def composite_score(sources: dict) -> dict:
    scores = {k: v for k, v in sources.items() if v is not None}
    avg = sum(scores.values()) / len(scores) if scores else 0
    signal = "BUY" if avg > 0.3 else "SELL" if avg < -0.3 else "HOLD"
    return {"score": avg, "signal": signal, "sources": scores}
