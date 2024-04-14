"""Predefined alert rules."""

def drawdown_alert(threshold: float = 0.1):
    return lambda ctx: ctx.get("drawdown", 0) > threshold

def price_alert(symbol: str, target: float, direction: str = "above"):
    return lambda ctx: (
        ctx.get("symbol") == symbol and
        (ctx.get("price", 0) > target if direction == "above" else ctx.get("price", 0) < target)
    )
