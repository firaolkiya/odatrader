"""Portfolio exposure limits."""

def check_exposure(positions: dict, max_per_symbol: float = 0.3, max_total: float = 1.0) -> dict:
    total = sum(abs(v) for v in positions.values())
    violations = []
    for sym, exp in positions.items():
        if exp > max_per_symbol:
            violations.append(f"{sym} exceeds per-symbol limit")
    if total > max_total:
        violations.append("Total exposure exceeds limit")
    return {"ok": len(violations) == 0, "violations": violations, "total_exposure": total}
