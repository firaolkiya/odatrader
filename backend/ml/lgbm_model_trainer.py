import os
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
import lightgbm as lgb
from sqlalchemy import create_engine
import talib
import matplotlib.pyplot as plt

# === CONFIG ===
DB_URI = "postgresql+psycopg2://odatrade:odatrade@localhost:5432/postgres"
engine = create_engine(DB_URI)
SYMBOLS = ["btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt"]

def train_lightgbm(symbol: str):
    symbol = symbol.lower()
    print(f"[ML Trainer] 📊 Training LightGBM for {symbol}")

    query = f"""
        SELECT * FROM market_data 
        WHERE symbol = '{symbol}' 
        ORDER BY timestamp ASC
    """
    df = pd.read_sql(query, engine)

    if df.empty or len(df) < 100:
        print(f"[ML Trainer] ❌ Not enough data to train for {symbol}")
        return

    # === Feature Engineering ===
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['ema_fast'] = talib.EMA(df['close'], timeperiod=9)
    df['ema_slow'] = talib.EMA(df['close'], timeperiod=21)
    macd, signal, _ = talib.MACD(df['close'])
    df['macd'] = macd
    df['macd_signal'] = signal

    for lag in [1, 2, 3, 5, 10]:
        df[f'close_lag_{lag}'] = df['close'].shift(lag)
        df[f'volume_lag_{lag}'] = df['volume'].shift(lag)

    # === Target: % change over next 3 candles ===
    df['future_close'] = df['close'].shift(-3)
    df['target'] = (df['future_close'] - df['close']) / df['close']  # % change
    df.dropna(inplace=True)

    features = ['rsi', 'ema_fast', 'ema_slow', 'macd', 'macd_signal', 'volume'] + \
               [col for col in df.columns if 'lag_' in col]

    X = df[features]
    y = df['target']

    # === Scale Features ===
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # === Train/Test Split ===
    split_idx = int(len(X_scaled) * 0.8)
    X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # === Train LightGBM Model ===
    model = lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05, max_depth=7)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    print(f"[ML Trainer] ✅ {symbol.upper()} R²: {r2:.4f}, MSE: {mse:.6f}")

    # === Save Model, Features, Scaler ===
    os.makedirs("backend/ml/models", exist_ok=True)
    joblib.dump(model, f"backend/ml/models/lightgbm_price_model_{symbol}.pkl")
    joblib.dump(features, f"backend/ml/models/lightgbm_features_{symbol}.pkl")
    joblib.dump(scaler, f"backend/ml/models/lightgbm_scaler_{symbol}.pkl")

    # === Plot Prediction ===
    # plt.figure(figsize=(14, 6))
    # plt.plot(y_test.values, label='Actual % Change')
    # plt.plot(y_pred, label='Predicted % Change')
    # plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
    # plt.title(f'{symbol.upper()} Model\nR²: {r2:.3f}, MSE: {mse:.6f}')
    # plt.legend()
    # plt.savefig(f'backend/ml/models/{symbol}_prediction_plot.png')
    # plt.close()

if __name__ == "__main__":
    for symbol in SYMBOLS:
        train_lightgbm(symbol)
