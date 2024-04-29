"""Cross-asset portfolio exposure with correlation-adjusted netting."""
from typing import Dict, List, Tuple


def _normalize_weights(correlations: Dict[str, Dict[str, float]], symbols: List[str]) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    for a in symbols:
        out[a] = {}
        for b in symbols:
            if a == b:
                out[a][b] = 1.0
            else:
                out[a][b] = correlations.get(a, {}).get(b, correlations.get(b, {}).get(a, 0.0))
    return out


def correlated_exposure(
    notionals: Dict[str, float],
    correlations: Dict[str, Dict[str, float]],
) -> float:
    """
    Effective portfolio exposure accounting for pairwise correlations.
    Uses sqrt of sum of (w_i * w_j * rho_ij) over all pairs.
    """
    symbols = list(notionals.keys())
    if not symbols:
        return 0.0
    weights = _normalize_weights(correlations, symbols)
    total = 0.0
    for i, a in enumerate(symbols):
        for j, b in enumerate(symbols):
            total += notionals[a] * notionals[b] * weights[a][b]
    return max(0.0, total) ** 0.5


def check_portfolio_limits(
    notionals: Dict[str, float],
    correlations: Dict[str, Dict[str, float]],
    max_per_symbol: float,
    max_correlated_total: float,
) -> dict:
    violations: List[str] = []
    for sym, exp in notionals.items():
        if abs(exp) > max_per_symbol:
            violations.append(f"{sym} notional {exp:.4f} exceeds per-symbol cap {max_per_symbol}")
    corr_total = correlated_exposure(notionals, correlations)
    if corr_total > max_correlated_total:
        violations.append(
            f"correlated exposure {corr_total:.4f} exceeds cap {max_correlated_total}"
        )
    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "correlated_exposure": corr_total,
        "per_symbol": dict(notionals),
    }


def net_positions(
    positions: Dict[str, Tuple[float, float]],
) -> Dict[str, float]:
    """Convert (qty, price) positions to signed notional map."""
    return {sym: qty * price for sym, (qty, price) in positions.items()}
