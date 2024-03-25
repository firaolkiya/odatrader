import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Union
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
  # using ta instead of talib


class MLStrategy:
    """
    Machine Learning Trading Strategy using LightGBM models trained by train_lightgbm.py

    Features:
    - RSI, EMAs, MACD indicators
    - Lagged price/volume features
    - StandardScaler normalization
    - Predicts 3-candle future price change
    """

    def __init__(self, symbol: str = "btcusdt"):
        self.symbol = symbol.lower()
        self.name = "MLStrategy"
        self.model: LGBMRegressor = None
        self.feature_list: list = None
        self.scaler: StandardScaler = None
        self._load_model_and_features()

    def _load_model_and_features(self) -> None:
        """Load trained model, features, and scaler from disk"""
        base_path = "backend/ml/models"
        model_path = os.path.join(base_path, f"lightgbm_price_model_{self.symbol}.pkl")
        features_path = os.path.join(base_path, f"lightgbm_features_{self.symbol}.pkl")
        scaler_path = os.path.join(base_path, f"lightgbm_scaler_{self.symbol}.pkl")

        if not all(os.path.exists(p) for p in [model_path, features_path, scaler_path]):
            raise FileNotFoundError(f"Model files missing for {self.symbol}")

        self.model = joblib.load(model_path)
        self.feature_list = joblib.load(features_path)
        self.scaler = joblib.load(scaler_path)

    def _generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate technical indicators matching training features using `ta`"""
        df = df.copy()
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)

        # Technical Indicators using ta
        df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
        df['ema_fast'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
        df['ema_slow'] = EMAIndicator(close=df['close'], window=21).ema_indicator()

        macd =MACD(close=df['close'], window_fast=12, window_slow=26, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()

        # Lag Features (matches training)
        for lag in [1, 2, 3, 5, 10]:
            df[f'close_lag_{lag}'] = df['close'].shift(lag)
            df[f'volume_lag_{lag}'] = df['volume'].shift(lag)

        df.bfill(inplace=True)  # Replaces deprecated fillna(method='bfill')
        return df

    def evaluate(self, market_data: Union[pd.DataFrame, pd.Series]) -> Dict[str, str]:
        """
        Evaluate market data and return trading decision

        Args:
            market_data: Latest market data (DataFrame or Series)
                         Must contain: ['open', 'high', 'low', 'close', 'volume']

        Returns:
            Dictionary with trading decision:
            {
                "action": "buy|sell|hold",
                "strategy": "MLStrategy",
                "reason": str
            }
        """
        try:
            # Convert input to DataFrame format
            if isinstance(market_data, pd.Series):
                df = market_data.to_frame().T
            else:
                df = market_data.copy()

            df = self._generate_features(df)

            input_df = df[self.feature_list].tail(1)

            if input_df.empty or input_df.isnull().any().any():
                return {
                    "action": "hold",
                    "strategy": self.name,
                    "reason": "Missing/invalid features"
                }

            input_scaled = self.scaler.transform(input_df)
            predicted_change = self.model.predict(input_scaled)[0]

            threshold = 0.002  # 0.2% change threshold

            if predicted_change > threshold:
                return {
                    "action": "buy",
                    "strategy": self.name,
                    "reason": f"Predicted +{predicted_change:.2%} gain"
                }
            elif predicted_change < -threshold:
                return {
                    "action": "sell",
                    "strategy": self.name,
                    "reason": f"Predicted {predicted_change:.2%} loss"
                }
            else:
                return {
                    "action": "hold",
                    "strategy": self.name,
                    "reason": f"Neutral ({predicted_change:.4%})"
                }

        except Exception as e:
            return {
                "action": "hold",
                "strategy": self.name,
                "reason": f"Error: {str(e)}"
            }
