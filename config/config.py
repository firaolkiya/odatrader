import os
from dotenv import load_dotenv

load_dotenv()

# OdaTrade Configuration
APP_NAME = "OdaTrade"
APP_VERSION = "1.0.0"

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")

MAX_TRADES_PER_DAY = int(os.getenv("MAX_TRADES_PER_DAY", "30"))
MAX_DRAWDOWN = float(os.getenv("MAX_DRAWDOWN", "0.15"))
TRAIL_STOP_PCT = float(os.getenv("TRAIL_STOP_PCT", "0.002"))
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "0.020"))
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "0.02"))
FIXED_RISK_PCT = float(os.getenv("FIXED_RISK_PCT", "0.01"))
DAILY_LOSS_LIMIT = float(os.getenv("DAILY_LOSS_LIMIT", "0.30"))
PROFIT_TRIGGER_PCT = float(os.getenv("PROFIT_TRIGGER_PCT", "0.0045"))
TRAILING_STOP_PCT = float(os.getenv("TRAILING_STOP_PCT", "0.0002"))
MIN_PROFIT_PCT = float(os.getenv("MIN_PROFIT_PCT", "0.0040"))
MIN_PROFIT_RETRACE_PCT = float(os.getenv("MIN_PROFIT_RETRACE_PCT", "0.0010"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///odatrade.db")
DB_NAME = os.getenv("DB_NAME", "odatrade")
DB_USER = os.getenv("DB_USER", "odatrade")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

SYMBOLS = os.getenv("SYMBOLS", "btcusdt,ethusdt,bnbusdt,solusdt,xrpusdt").split(",")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_SECRET_KEY = os.getenv("REDDIT_SECRET_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "odatrade-dev-secret-change-me")

DB_PARAMS = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
}
