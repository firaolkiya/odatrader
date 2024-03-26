import os, sys, time
from datetime import datetime, timezone
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine, text
from binance import ThreadedWebsocketManager

# === Path Fixes ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# === Local Imports ===
from backend.core.feature_engineering import compute_features as engineer_features
from backend.ml.ml_strategy import MLStrategy
from backend.ml.lgbm_model_trainer import train_lightgbm
from backend.execution.execution_engine import ExecutionEngine
from backend.strategies.strategy_voter import StrategyVoter
from config.config import DB_PARAMS, SYMBOLS

# === CONFIG ===
DB_PARAMS = DB_PARAMS
SYMBOLS = SYMBOLS
INTERVAL = "1m"
STARTING_BALANCE = 5000

# === DB Setup ===
DB_URI = f"postgresql+psycopg2://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['dbname']}"
engine = create_engine(DB_URI)

# === Engine + Voter ===
execution_engine = ExecutionEngine(starting_balance=STARTING_BALANCE, engine=engine)
voter = {symbol: StrategyVoter(symbol) for symbol in SYMBOLS}

# === Store OHLCV to DB ===
def store_to_db(symbol, candle):
    with engine.begin() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS market_data (
                symbol TEXT NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                open FLOAT, high FLOAT, low FLOAT, close FLOAT, volume FLOAT,
                PRIMARY KEY (symbol, timestamp)
            )
        '''))
        conn.execute(text('''
            INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume)
            VALUES (:symbol, :timestamp, :open, :high, :low, :close, :volume)
            ON CONFLICT (symbol, timestamp) DO NOTHING
        '''), {
            'symbol': symbol,
            'timestamp': datetime.fromtimestamp(candle['t'] / 1000, tz=timezone.utc),
            'open': float(candle['o']),
            'high': float(candle['h']),
            'low': float(candle['l']),
            'close': float(candle['c']),
            'volume': float(candle['v'])
        })

# === Load & Engineer Features ===
def load_and_engineer_features(symbol: str) -> pd.DataFrame:
    try:
        query = '''
            SELECT * FROM market_data
            WHERE symbol = %s
            ORDER BY timestamp DESC
            LIMIT 100
        '''
        df = pd.read_sql(query, engine, params=(symbol,))
        if df.empty or len(df) < 30:
            print(f"[{symbol.upper()}] ⚠️ Not enough data")                                      
            return pd.DataFrame()

        df.sort_values('timestamp', inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = engineer_features(df)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"[{symbol.upper()}] ❌ Feature engineering error: {e}")
        return pd.DataFrame()

# === Log Signal to DB ===
def log_signal_to_db(signal, price, symbol, executed=True):
    try:
        with engine.begin() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS strategy_signals (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ,
                    symbol TEXT,
                    strategy TEXT,
                    action TEXT,
                    price FLOAT,
                    reason TEXT,
                    executed BOOLEAN DEFAULT TRUE
                )
            '''))
            conn.execute(text('''
                INSERT INTO strategy_signals (timestamp, symbol, strategy, action, price, reason, executed)
                VALUES (:timestamp, :symbol, :strategy, :action, :price, :reason, :executed)
            '''), {
                'timestamp': datetime.now(timezone.utc),
                'symbol': symbol,
                'strategy': signal['strategy'],
                'action': signal['action'],
                'price': float(price),
                'reason': signal['reason'],
                'executed': executed
            })
    except Exception as e:
        print(f"[DB Error] ❌ Failed to log signal for {symbol}: {e}")

# === Strategy Evaluation ===
def evaluate_with_voter(df, symbol):
    message = f"evaluating stratagies for **{symbol}**"
    print(message.upper())
    try:
        final_signal = voter[symbol].get_final_signal(df)
        if final_signal == "BUY":
            return {
                "action": "BUY",
                "strategy": "strategy_voter",
                "reason": "Consensus voted BUY"
            }
        elif final_signal == "SELL":
            return {
                "action": "SELL",
                "strategy": "strategy_voter",
                "reason": "Consensus voted SELL"
            }
    except Exception as e:
        print(f"[{symbol.upper()} Evaluation Error] {e}")
    return None

# === WebSocket Message Handler ===
def handle_socket_message(symbol):
    def inner(msg):
        try:
            if msg['e'] != 'kline' or not msg['k']['x']:
                return

            kline = msg['k']
            candle = {
                't': int(kline['t']),
                'o': float(kline['o']),
                'h': float(kline['h']),
                'l': float(kline['l']),
                'c': float(kline['c']),
                'v': float(kline['v']),
            }

            store_to_db(symbol, candle)
            df = load_and_engineer_features(symbol)
            if df.empty:
                return

            signal = evaluate_with_voter(df, symbol)
            if signal:
                price = df.iloc[-1]['close']

                # 🛡 Kill Switch Check
                if execution_engine.check_kill_switch():
                    print(f"[{symbol.upper()}] 🛑 Kill switch active. Trade blocked.")
                    log_signal_to_db(signal, price, symbol, executed=False)
                    return

                executed = execution_engine.execute_paper_trade(signal, price, symbol)
                if executed:
                    log_signal_to_db(signal, price, symbol)
        except Exception as e:
            print(f"[{symbol.upper()} Stream Error] {e}")
    return inner

# === PnL Logger ===
def log_pnl():
    pnl_log = execution_engine.get_pnl_log()
    if pnl_log:
        print("\n--- PnL Summary ---")
        for trade in pnl_log:
            print(f"Symbol: {trade['symbol']} | Entry: {trade['entry_time']} | Exit: {trade['exit_time']} | PnL: {trade['pnl']:.2f}")
        print(f"[Balance] ${execution_engine.get_balance():.2f}\n")

# === ML Retrain Scheduler ===
def activate_lightgbm():
    for symbol in SYMBOLS:
        train_lightgbm(symbol)

# === Entry Point ===
if __name__ == '__main__':
    twm = ThreadedWebsocketManager()
    twm.start()

    for symbol in SYMBOLS:
        print(f"[WebSocket] 🔄 Starting stream for {symbol.upper()}...")
        twm.start_kline_socket(callback=handle_socket_message(symbol), symbol=symbol, interval=INTERVAL)

    scheduler = BackgroundScheduler()
    scheduler.add_job(log_pnl, 'interval', minutes=1)
    scheduler.add_job(activate_lightgbm, 'interval', hours=2)
    scheduler.start()

    if execution_engine.check_kill_switch():
        print("[Startup] ⚠️ Kill switch is ACTIVE.")
    else:
        print("[Startup] Kill switch is OFF.")

    print("[Bot] ✅ Multi-symbol scalping bot active")
    while True:
        time.sleep(1)
