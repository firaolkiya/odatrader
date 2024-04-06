"""HTML backtest report generator."""

def generate_report(metrics: dict, title: str = "OdaTrade Backtest Report") -> str:
    rows = "".join(f"<tr><td>{k}</td><td>{v:.4f if isinstance(v, float) else v}</td></tr>" for k, v in metrics.items())
    return f"""<!DOCTYPE html><html><head><title>{title}</title></head>
    <body><h1>{title}</h1><table border="1">{rows}</table></body></html>"""
