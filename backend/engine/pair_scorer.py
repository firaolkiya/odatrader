"""Pair scoring algorithm for instrument selection."""
import math
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger("odatrade.pair_scorer")


@dataclass
class PairMetadata:
    symbol: str
    volume: float = 1e6
    spread: float = 0.0005
    vol: float = 0.02
    depth: float = 10000.0
    funding_rate: float = 0.0
    correlation: float = 0.0


def normalize(x: float, xmax: float, xmin: float = 0.0) -> float:
    return max(0.0, min(1.0, (x - xmin) / (xmax - xmin + 1e-12)))


def pair_score(meta: PairMetadata, maxima: dict, weights: dict, funding_weight: float = 0.15) -> float:
    liq = normalize(math.log(max(1, meta.volume)), math.log(max(1, maxima.get("volume", 1e9))))
    spread_s = 1 - normalize(meta.spread, maxima.get("spread", 0.01))
    vol_s = normalize(meta.vol, maxima.get("vol", 2.0))
    depth_s = normalize(meta.depth, maxima.get("depth", 100000))
    funding_pen = max(-1, min(1, meta.funding_rate / maxima.get("funding_rate", 0.0001)))

    score = (
        weights.get("liq", 0.30) * liq
        + weights.get("spread", 0.25) * spread_s
        + weights.get("vol", 0.20) * vol_s
        + weights.get("depth", 0.15) * depth_s
        + weights.get("corr", 0.10) * (1 - abs(meta.correlation))
    )
    score -= funding_weight * funding_pen
    return max(0.0, min(1.0, score))


class PairScorer:
    DEFAULT_WEIGHTS = {"liq": 0.30, "spread": 0.25, "vol": 0.20, "depth": 0.15, "corr": 0.10}
    DEFAULT_MAXIMA = {"volume": 1e9, "spread": 0.01, "vol": 2.0, "depth": 100000, "funding_rate": 0.001}

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.weights = self.config.get("weights", self.DEFAULT_WEIGHTS)
        self.maxima = self.config.get("maxima", self.DEFAULT_MAXIMA)
        self.select_threshold = self.config.get("select_threshold", 0.65)
        self.top_k = self.config.get("top_k", 3)
        self._metadata: Dict[str, PairMetadata] = {}

    def update_metadata(self, symbol: str, **kwargs):
        if symbol not in self._metadata:
            self._metadata[symbol] = PairMetadata(symbol=symbol)
        for k, v in kwargs.items():
            if hasattr(self._metadata[symbol], k):
                setattr(self._metadata[symbol], k, v)

    def score_all(self) -> List[dict]:
        results = []
        for sym, meta in self._metadata.items():
            s = pair_score(meta, self.maxima, self.weights)
            results.append({
                "symbol": sym, "score": s,
                "selected": s >= self.select_threshold,
                "metadata": {
                    "volume": meta.volume, "spread": meta.spread,
                    "vol": meta.vol, "depth": meta.depth, "funding_rate": meta.funding_rate,
                },
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def get_top_k(self) -> List[str]:
        scored = self.score_all()
        return [r["symbol"] for r in scored[:self.top_k] if r["selected"]]

    def get_active_pairs(self) -> List[str]:
        return [r["symbol"] for r in self.score_all() if r["selected"]]
