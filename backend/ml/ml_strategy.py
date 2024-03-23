import pandas as pd
import joblib
import ta
from sqlalchemy import create_engine
from datetime import timezone, datetime

import ta.momentum
import ta.trend

# Load model and scaler once
model = joblib.load("models/lightgbm_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# Your DB settings
DB_URI = "postgresql+psycopg2://odatrade:odatrade@localhost:5432/postgres"
engine = create_engine(DB_URI)

def evaluate_ml_strategy():
    try:
        # 1. Load last 100 candles
        df = pd.read_sql("SELECT * FROM market_data ORDER BY timestamp DESC LIMIT 100", engine)
        if df.empty or len(df) < 30:
            print("[ML Strategy] ⚠️ Not enough data for prediction.")
            return None

        df.sort_values('timestamp', inplace=True)

        # 2. Computindicators
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        df['ema_fast'] = ta.trend.EMAIndicator(close=df['close'], window=9).ema_indicator()
        df['ema_slow'] = ta.trend.EMAIndicator(close=df['close'], window=21).ema_indicator()

        macd_ind = ta.trend.MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd_ind.macd()
        df['macd_signal'] = macd_ind.macd_signal()

        # 3. Latest row for prediction
        latest = df.iloc[-1]
        features = latest[['rsi', 'ema_fast', 'ema_slow', 'macd', 'macd_signal', 'volume']].to_frame().T
        X = scaler.transform(features)

        predicted_return = model.predict(X)[0]  # in %

        print(f"[ML Strategy] Predicted return: {predicted_return:.2f}%")

        if predicted_return >= 0.5:
            return {
                "action": "BUY",
                "strategy": "evaluate_ml_strategy",
                "price": float(latest['close']),
                "reason": f"ML expects +{predicted_return:.2f}%",
            }

        return None

    except Exception as e:
        print(f"[ML Strategy Error] {e}")
        return None
