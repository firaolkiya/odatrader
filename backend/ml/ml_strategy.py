import pandas as pd
import joblib
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from backend.strategies.base_strategy import BaseStrategy

class MLStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="ML")
        self.model = joblib.load("models/lightgbm_model.pkl")
        self.scaler = joblib.load("models/scaler.pkl")

    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.sort_values('timestamp', inplace=True)

        df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
        df['ema_fast'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
        df['ema_slow'] = EMAIndicator(close=df['close'], window=21).ema_indicator()

        macd = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        return df

    def generate_signal(self, df: pd.DataFrame, symbol: str = None) -> str:
        """
        Generates a signal using the most recent row from the dataframe.
        """
        try:
            if df.empty or len(df) < 30:
                print(f"[MLStrategy:{symbol}] ⚠️ Not enough data for prediction.")
                return "hold"

            df = self.generate_features(df)
            latest = df.iloc[-1]
            features = latest[['rsi', 'ema_fast', 'ema_slow', 'macd', 'macd_signal', 'volume']].to_frame().T

            X = self.scaler.transform(features)
            predicted_return = self.model.predict(X)[0]

            print(f"[MLStrategy:{symbol}] Predicted return: {predicted_return:.2f}%")

            if predicted_return >= 0.5:
                return "buy"
            elif predicted_return <= -0.5:
                return "sell"
            else:
                return "hold"

        except Exception as e:
            print(f"[MLStrategy:{symbol}] ❌ Error: {e}")
            return "hold"

    def evaluate(self, row=None, prev_row=None, df: pd.DataFrame = None, symbol: str = None):
        """
        Evaluate using recent DataFrame or row.
        If df is provided, it uses ML prediction. Otherwise, it returns None.
        """
        if df is None:
            return None

        signal = self.generate_signal(df, symbol)
        if signal == "buy":
            return {'action': 'BUY', 'reason': 'ML model predicted strong upward movement', 'strategy': self.name}
        elif signal == "sell":
            return {'action': 'SELL', 'reason': 'ML model predicted strong downward movement', 'strategy': self.name}
        else:
            return None
