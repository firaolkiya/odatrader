import os, sys
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
import lightgbm as lgb
from sqlalchemy import create_engine
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import DATABASE_URL, SYMBOLS

# === CONFIG ===
DB_URI = f"{DATABASE_URL}"
engine = create_engine(DB_URI)
SYMBOLS = SYMBOLS

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
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
    df['ema_fast'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
    df['ema_slow'] = EMAIndicator(close=df['close'], window=21).ema_indicator()

    macd_indicator = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['macd'] = macd_indicator.macd()
    df['macd_signal'] = macd_indicator.macd_signal()

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

    
    

if __name__ == "__main__":
    for symbol in SYMBOLS:
        train_lightgbm(symbol)
