"""Schema migration runner for OdaTrade."""
from sqlalchemy import text
from backend.db.models import Base

MIGRATIONS = [
    ("001_initial", "CREATE TABLE IF NOT EXISTS migrations (id TEXT PRIMARY KEY, applied_at TIMESTAMP)"),
    ("002_alert_logs", None),
]

def run_migrations(engine):
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS migrations (id TEXT PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"))
        applied = {r[0] for r in conn.execute(text("SELECT id FROM migrations")).fetchall()}
        Base.metadata.create_all(engine)
        for mid, _ in MIGRATIONS:
            if mid not in applied:
                conn.execute(text("INSERT INTO migrations (id) VALUES (:id)"), {"id": mid})
