"""SQLite offline storage for OdaTrade development."""
from sqlalchemy import create_engine
from backend.db.migrations import run_migrations

def get_sqlite_engine(path: str = "odatrade.db"):
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    run_migrations(engine)
    return engine
