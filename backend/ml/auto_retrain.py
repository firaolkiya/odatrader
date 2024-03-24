# auto_retrain.py
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from lgbm_model_trainer import train_lightgbm
from lstm_model_trainer import train_lstm

def auto_retrain():
    print("🚀 [Auto Retrainer] Starting full retraining process...\n")

    try:
        train_lightgbm()
    except Exception as e:
        print(f"❌ [Auto Retrainer] LightGBM training failed: {e}")

    print("\n" + "-"*60 + "\n")

    try:
        train_lstm()
    except Exception as e:
        print(f"❌ [Auto Retrainer] LSTM training failed: {e}")

    print("\n✅ [Auto Retrainer] Finished retraining pipeline.\n")

if __name__ == "__main__":
    auto_retrain()
