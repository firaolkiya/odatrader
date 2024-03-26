# backtester.py
"""
Run backtest on historical market_data using your strategies.
Outputs:
- PnL & trade log to backtest_results.csv
- Summary metrics: Sharpe, drawdown
"""
#NHHH
import pandas as pd
import numpy as np
from datetime import datetime
# import matplotlib.pyplot as plt
import os
import sys
from sqlalchemy import create_engine, text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.strategies.rsi_strategy import RSIStrategy
from backend.strategies.ema_crossover import EMACrossoverStrategy
from backend.strategies.macd_strategy import MACDStrategy
from backend.strategies.bb_strategy import BollingerStrategy
from config.config import DATABASE_URL, DB_PARAMS
# === DB CONFIG ===
DB_PARAMS = DB_PARAMS
DB_URI = f"{DATABASE_URL}"
engine = create_engine(DB_URI)

STRATEGIES = {
    'rsi': RSIStrategy,
    'ema': EMACrossoverStrategy,
    'macd': MACDStrategy,
    'bb': BollingerStrategy
}

USE_STRATEGY = 'rsi'  # options: 'rsi', 'ema', 'macd', 'bb', 'all'
TRADE_SIZE = 1
STARTING_BALANCE = 1000

# === Load historical market data ===
def load_data():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM market_data ORDER BY timestamp", conn)
    df.set_index('timestamp', inplace=True)
    return df

# === Feature Engineering ===
def add_indicators(df):
    import ta

    # Ensure correct column format
    df['close'] = df['close'].astype(float)

    # RSI
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()

    # EMA Fast and Slow
    df['ema_fast'] = ta.trend.EMAIndicator(close=df['close'], window=9).ema_indicator()
    df['ema_slow'] = ta.trend.EMAIndicator(close=df['close'], window=21).ema_indicator()

    # MACD
    macd = ta.trend.MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close=df['close'], window=20)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()

    return df.dropna()


# === Backtest Logic ===
def run_backtest(df):
    position = None
    trades = []
    equity = []
    balance = STARTING_BALANCE

    for i in range(1, len(df)):
        row = df.iloc[i]

        # Select strategy
        if USE_STRATEGY == 'all':
            signal = None
            for func in STRATEGIES.values():
                signal = func(row)
                if signal:
                    break
        else:
            signal = STRATEGIES[USE_STRATEGY](row)

        price = row['close']

        if signal:
            action = signal['action']
            if action == 'BUY' and position is None:
                position = {
                    'entry_price': price,
                    'entry_time': row.name
                }
            elif action == 'SELL' and position:
                pnl = price - position['entry_price']
                trades.append({
                    'entry_time': position['entry_time'],
                    'exit_time': row.name,
                    'entry_price': position['entry_price'],
                    'exit_price': price,
                    'pnl': pnl * TRADE_SIZE
                })
                balance += pnl * TRADE_SIZE
                position = None

        # Add equity (mark-to-market if in position)
        if position:
            unrealized = (price - position['entry_price']) * TRADE_SIZE
            equity.append(balance + unrealized)
        else:
            equity.append(balance)

    return trades, equity

# === Metrics ===
def summarize(trades, equity):
    pnl = [t['pnl'] for t in trades]
    equity = np.array(equity)
    returns = np.diff(equity) / equity[:-1]

    sharpe = np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252 * 24 * 60)  # annualized for minute data
    drawdown = np.max(np.maximum.accumulate(equity) - equity)

    print(f"\nBacktest Summary:")
    print(f"Trades: {len(trades)}")
    print(f"Total PnL: {sum(pnl):.2f} USDT")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {drawdown:.2f}")

    return pd.DataFrame(trades), equity

# === Save Results ===
# def save_results(trade_df, equity):
#     trade_df.to_csv("backtest_results.csv", index=False)
#     plt.figure(figsize=(10, 5))
#     plt.plot(equity)
#     plt.title("Equity Curve")
#     plt.xlabel("Steps")
#     plt.ylabel("Balance")
#     plt.grid(True)
#     plt.tight_layout()
#     plt.savefig("backtest_equity.png")
#     plt.show()

# === Main ===
if __name__ == '__main__':
    df = load_data()
    df = add_indicators(df)
    print(f"Loaded {len(df)} rows of historical data.")

    trades, equity = run_backtest(df)
    trade_df, eq_curve = summarize(trades, equity)
    # save_results(trade_df, eq_curve)
