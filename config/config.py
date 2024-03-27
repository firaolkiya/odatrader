import os


# Load variables from .env
# === EXCHANGE API KEYS (Binance Example) ===
BINANCE_API_KEY= "REDACTED"
BINANCE_SECRET_KEY= "REDACTED"

# === RISK & SAFETY SETTINGS ===
MAX_TRADES_PER_DAY=30
MAX_DRAWDOWN=0.15            # Daily drawdown limit (15%)
TRAIL_STOP_PCT=0.002          # Trailing Stop % (2%)
STOP_LOSS_PCT=0.020           # Static Stop Loss (5%)
TAKE_PROFIT_PCT=0.02         # Static Take Profit (4%)
FIXED_RISK_PCT=0.01          # Risk per trade (1%)
DAILY_LOSS_LIMIT=0.30         # Max 30% capital loss/day
PROFIT_TRIGGER_PCT = 0.0045
TRAILING_STOP_PCT = 0.0002
# === DATABASE ===
DATABASE_URL="postgresql+psycopg2://postgres.fehlivkemqncamxkfjwo:odatrade@aws-1-eu-west-2.pooler.supabase.com:6543/postgres"

SYMBOLS = ["btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt"]

# === DATABASE CONFIG ===
DB_NAME="postgres"
DB_USER="postgres.fehlivkemqncamxkfjwo"
DB_PASSWORD="odatrade"
DB_HOST="aws-1-eu-west-2.pooler.supabase.com"
DB_PORT=6543
REDDIT_CLIENT_ID = "rDIOU95RnhKtzRLswXoP1g"
REDDIT_SECRET_KEY = "REDACTED"

GROQ_API_KEY = "REDACTED"
MIN_PROFIT_PCT = 0.0040          # 0.40% profit threshold
MIN_PROFIT_RETRACE_PCT = 0.0010  # 0.10% allowed retracement

# === SYMBOLS LIST ===
SYMBOLS = ["btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt"]  # Optional: os.getenv("SYMBOLS").split(",")


REDDIT_SECRET_KEY = os.getenv("reddit_secret_key")
# === Optional: Parsed DB Params (if using psycopg2 or similar) ===
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}
