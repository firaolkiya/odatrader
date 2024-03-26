import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# === EXCHANGE API KEYS ===
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")


# === RISK & SAFETY SETTINGS ===
MAX_TRADES_PER_DAY = int(os.getenv("MAX_TRADES_PER_DAY", 30))
MAX_DRAWDOWN = float(os.getenv("MAX_DRAWDOWN", 15))
TRAIL_STOP_PCT = float(os.getenv("TRAIL_STOP_PCT", 0.02))
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 0.05))
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", 0.04))
FIXED_RISK_PCT = float(os.getenv("FIXED_RISK_PCT", 0.01))
DAILY_LOSS_LIMIT = float(os.getenv("DAILY_LOSS_LIMIT", 30))
TRAILING_STOP_PCT = float(os.getenv("STOP_LOSS_PCT", 0.02))
TRAILING_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", 0.04))
MIN_PROFIT_PCT = 0.0040          # 0.40% profit threshold
MIN_PROFIT_RETRACE_PCT = 0.0010  # 0.10% allowed retracement

# === SYMBOLS LIST ===
SYMBOLS = ["btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt"]  # Optional: os.getenv("SYMBOLS").split(",")

# === DATABASE CONNECTION STRING ===
DATABASE_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
GROQ_API_KEY = os.getenv("groq_api_key")
REDDIT_CLIENT_ID = os.getenv("reddit_client_id")
REDDIT_SECRET_KEY = os.getenv("reddit_secret_key")
# === Optional: Parsed DB Params (if using psycopg2 or similar) ===
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}
