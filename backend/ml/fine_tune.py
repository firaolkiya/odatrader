"""ML model fine-tuning pipeline with regime features."""
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger("odatrade.ml.finetune")


class ModelFineTuner:
    def __init__(self, model_dir: str = "backend/ml/models"):
        self.model_dir = model_dir
        self._history: list = []

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        from backend.core.feature_engineering import compute_features
        from backend.engine.regime_classifier import RegimeClassifier
        featured = compute_features(df.copy())
        rc = RegimeClassifier()
        regimes = []
        for i in range(len(featured)):
            window = featured.iloc[max(0, i - 50):i + 1]
            regimes.append(rc.classify(window)["regime"] if len(window) > 10 else 0)
        featured["regime"] = regimes
        from backend.ml.feature_pipeline import add_lag_features, add_rolling_stats
        featured = add_lag_features(featured, ["close", "rsi"], lags=[1, 3, 5])
        featured = add_rolling_stats(featured, "close", windows=[5, 10, 20])
        return featured.dropna()

    def fine_tune_lightgbm(self, df: pd.DataFrame, symbol: str, params: dict = None) -> Dict:
        try:
            import lightgbm as lgb
            from sklearn.model_selection import train_test_split
            featured = self.prepare_features(df)
            if len(featured) < 100:
                return {"error": "insufficient data", "rows": len(featured)}
            featured["target"] = featured["close"].shift(-3) / featured["close"] - 1
            featured = featured.dropna()
            feature_cols = [c for c in featured.columns if c not in ("target", "timestamp", "symbol")]
            X = featured[feature_cols]
            y = featured["target"]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
            default_params = {"objective": "regression", "metric": "rmse", "num_leaves": 31,
                              "learning_rate": 0.05, "feature_fraction": 0.8, "verbose": -1}
            default_params.update(params or {})
            train_data = lgb.Dataset(X_train, label=y_train)
            model = lgb.train(default_params, train_data, num_boost_round=200)
            preds = model.predict(X_test)
            rmse = float(np.sqrt(np.mean((preds - y_test) ** 2)))
            path = os.path.join(self.model_dir, f"{symbol}_finetuned.pkl")
            import joblib
            joblib.dump(model, path)
            result = {"symbol": symbol, "rmse": rmse, "features": len(feature_cols),
                      "train_rows": len(X_train), "path": path,
                      "finetuned_at": datetime.now(timezone.utc).isoformat()}
            self._history.append(result)
            from backend.ml.model_registry import ModelRegistry
            ModelRegistry.register(f"{symbol}_finetuned", path, "v2", {"rmse": rmse})
            logger.info("Fine-tuned %s: RMSE=%.6f", symbol, rmse)
            return result
        except Exception as e:
            logger.error("Fine-tune failed: %s", e)
            return {"error": str(e)}

    def train_regime_classifier(self, df: pd.DataFrame) -> Dict:
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            featured = self.prepare_features(df)
            featured["regime_label"] = (featured["regime"] > 0.5).astype(int)
            feature_cols = [c for c in featured.columns if c not in ("regime_label", "timestamp", "symbol", "regime", "target")]
            if not feature_cols:
                return {"error": "no features"}
            X = featured[feature_cols].fillna(0)
            y = featured["regime_label"]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
            clf = RandomForestClassifier(n_estimators=100, max_depth=5)
            clf.fit(X_train, y_train)
            accuracy = float(clf.score(X_test, y_test))
            path = os.path.join(self.model_dir, "regime_classifier.pkl")
            import joblib
            joblib.dump(clf, path)
            return {"accuracy": accuracy, "path": path, "features": len(feature_cols)}
        except Exception as e:
            return {"error": str(e)}
