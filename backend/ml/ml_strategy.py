import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Union
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler
import talib

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
        """Generate technical indicators matching training features"""
        # Technical Indicators
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        df['ema_fast'] = talib.EMA(df['close'], timeperiod=9)
        df['ema_slow'] = talib.EMA(df['close'], timeperiod=21)
        macd, signal, _ = talib.MACD(df['close'])
        df['macd'] = macd
        df['macd_signal'] = signal
        
        # Lag Features (matches training)
        for lag in [1, 2, 3, 5, 10]:
            df[f'close_lag_{lag}'] = df['close'].shift(lag)
            df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
            
        df.fillna(method='bfill', inplace=True)
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
            # Convert input to proper DataFrame format
            if isinstance(market_data, pd.Series):
                df = market_data.to_frame().T
            else:
                df = market_data.copy()
                
            # Generate all required features
            df = self._generate_features(df)
            
            # Select only the features used in training
            input_df = df[self.feature_list].tail(1)
            
            if input_df.empty or input_df.isnull().any().any():
                return {
                    "action": "hold",
                    "strategy": self.name,
                    "reason": "Missing/invalid features"
                }
            
            # Scale features and make prediction
            input_scaled = self.scaler.transform(input_df)
            predicted_change = self.model.predict(input_scaled)[0]
            
            # Trading logic
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

