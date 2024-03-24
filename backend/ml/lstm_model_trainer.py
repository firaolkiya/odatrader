import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping
from sqlalchemy import create_engine

DB_URI = "postgresql+psycopg2://odatrade:odatrade@localhost:5432/postgres"
engine = create_engine(DB_URI)

def train_lstm_for_symbol(symbol='BTCUSDT'):
    print(f"[ML Trainer] 📊 Starting LSTM training for symbol: {symbol}...")

    # Load data
    df = pd.read_sql("SELECT * FROM market_data WHERE symbol = %s ORDER BY timestamp DESC", engine, params=(symbol,))
    df = df.sort_values('timestamp')

    if df.empty or len(df) < 100:
        print("[ML Trainer] ❌ Not enough data to train.")
        return

    # Feature engineering
    import talib
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['ema_fast'] = talib.EMA(df['close'], timeperiod=9)
    df['ema_slow'] = talib.EMA(df['close'], timeperiod=21)
    macd, signal, _ = talib.MACD(df['close'])
    df['macd'] = macd
    df['macd_signal'] = signal
    df['volume'] = df['volume'].astype(float)
    df.dropna(inplace=True)

    # Create target
    df['target'] = df['close'].pct_change().shift(-1) * 100
    df.dropna(inplace=True)

    # Features
    features = ['rsi', 'ema_fast', 'open', 'close', 'high', 'low', 'volume',
                'ema_slow', 'macd', 'macd_signal']
    X = df[features]
    y = df['target']

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Sequences
    def create_sequences(X, y, seq_len=20):
        Xs, ys = [], []
        for i in range(seq_len, len(X)):
            Xs.append(X[i-seq_len:i])
            ys.append(y.iloc[i])
        return np.array(Xs), np.array(ys)

    X_seq, y_seq = create_sequences(X_scaled, y)

    # Train/test split
    split_idx = int(len(X_seq) * 0.8)
    X_train, X_test = X_seq[:split_idx], X_seq[split_idx:]
    y_train, y_test = y_seq[:split_idx], y_seq[split_idx:]

    # LSTM model
    model = Sequential()
    model.add(LSTM(64, return_sequences=False, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    # Training
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1, callbacks=[early_stop])

    # Evaluation
    y_pred = model.predict(X_test).flatten()
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    print(f"[ML Trainer] 📈 Evaluation Results for {symbol} — R² Score: {r2:.4f}, MSE: {mse:.4f}")

    # Save
    os.makedirs(f"models/{symbol}", exist_ok=True)
    model.save(f"models/{symbol}/lstm_model.h5")
    joblib.dump(scaler, f"models/{symbol}/scaler.pkl")
    print(f"[ML Trainer] ✅ LSTM model and scaler saved for {symbol}.")

if __name__ == "__main__":
    train_lstm_for_symbol(symbol='btcusdt')
