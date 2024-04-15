"""Scheduled job definitions."""

JOBS = [
    {"id": "retrain_ml", "interval_minutes": 60, "description": "Retrain LightGBM models"},
    {"id": "portfolio_snapshot", "interval_minutes": 15, "description": "Save portfolio snapshot"},
    {"id": "risk_check", "interval_minutes": 5, "description": "Run risk limit checks"},
    {"id": "cleanup_logs", "interval_minutes": 1440, "description": "Rotate old log files"},
]
