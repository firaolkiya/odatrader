# 📈 Crypto Scalping Bot Framework with ML Dashboard

This project is a complete crypto scalping framework that:
- Collects live market data using Binance API
- Runs rule-based and machine learning strategies
- Logs signals and trades to PostgreSQL
- Allows you to train an ML model (LightGBM) on historical data
- Provides a **dashboard** to visualize market data, predictions, and performance

---

## 🛠 Requirements

**Python Version:** Python 3.8–3.11 recommended

### 🔧 Installation

1. Clone the repository or download the source code:
```bash

cd to to the folder of the project
Create and activate a virtual environment (recommended):

bash
Copy
Edit
python -m venv venv
source venv/bin/activate    # on Linux/macOS
venv\Scripts\activate       # on Windows
Install all dependencies:

bash
Copy
Edit
pip install -r requirements.txt
📦 Required Python Packages
If requirements.txt is missing, here are the main packages used:

txt
Copy
Edit
pandas
numpy
scikit-learn
joblib
sqlalchemy
psycopg2-binary
requests
ta-lib
binance
streamlit
apscheduler
Install them manually:

bash
Copy
Edit
pip install pandas numpy scikit-learn joblib sqlalchemy psycopg2-binary requests ta-lib binance streamlit apscheduler
✅ Note: TA-Lib may require compilation. If you face issues on Windows, try:

bash
Copy
Edit
pip install TA-Lib‑0.4.0‑cp311‑cp311‑win_amd64.whl
🧠 How to Run the Project
if you have vscode installed after installing all nessecarry files just run the poject starting withe the Scalping Framework.py  and then the ml trainer the the dashboard sequentilly if you dont have vs code 
then:
1. ✅ Run the Scalping Framework (Real-time Data Collector + Strategy Engine)
This collects data from Binance and evaluates strategies:

bash
Copy
Edit
python scalping_bot_framework.py
Make sure your .env or config section has the correct database credentials and Binance symbol (e.g., BTCUSDT, ETHUSDT).

2. 🧪 Train the LightGBM Model
After some data is collected, run the trainer:

bash
Copy
Edit
python backend/ml/trainer_lightgbm.py
This fetches recent market data from the DB and trains a regression model to predict price direction.

It saves the model at:

models/lightgbm_model.pkl

3. 📊 Launch the Dashboard
Use Streamlit to visualize market trends and predictions:

bash
Copy
Edit
cd dashboard
streamlit run dashboard.py
The dashboard displays:

Live price chart

RSI, MACD, EMA indicators

Model predictions

Strategy signal logs

PnL over time

🧠 Strategy Modules
Your strategies are modular and located in:

bash
Copy
Edit
backend/strategies/
├── rsi_strategy.py
├── macd_strategy.py
├── ema_crossover.py
├── bb_strategy.py
├── evaluate_lightgbm.py  # ML-based strategy
You can add custom strategies by creating new Python functions that accept row and return a signal dict.

✅ Summary of Steps
Step	Script	Description
1	scalping_bot_framework.py	Starts data collection & runs strategy logic
2	backend/ml/trainer_lightgbm.py	Trains and saves LightGBM model
3	dashboard/dashboard.py	Launches the dashboard via Streamlit

⚠️ Notes
Make sure your PostgreSQL database is running and credentials are valid.

Binance API can disconnect sometimes — the bot will auto-reconnect.

Always run the scalping bot first before training the model or viewing the dashboard.

Keep your models/ directory in place to avoid missing file errors.

🧠 Tips
To test fast, reduce the interval to "1m" in Binance settings.

Keep Streamlit and the bot running in separate terminals.

You can extend the ML model to use sentiment data or multi-timeframe inputs.

🤖 Author
Made by [Your Name] – Freelance Data Scientist / Algo Dev
📧 Reach me on Upwork or GitHub if you have questions or want upgrades!

yaml
Copy
Edit

---

LEach day builds progressively, reuses your folders, and targets specific features from your milestone.
________________________________________
🔹 Day 1 – Docker + MVP Deployment Test
📍 Goal: Get your existing codebase Dockerized, connected, and visible in the browser for basic MVP flow.
Tasks:
•	✅ Finalize Dockerfile, docker-compose.yml
•	✅ Add volumes for logs/models
•	✅ Run your dashboard.py and scalping_bot_framework.py inside container
•	✅ Print bot status to UI from backend using simple REST (FastAPI or Flask)
•	✅ Fix WebSocket reconnect logic (if applicable)
Related Files/Folders:
•	Dockerfile, docker-compose.yml
•	dashboard.py, scalping_bot_framework.py
•	Backend REST (consider adding backend/api/ later if needed)
________________________________________
🔹 Day 2 – Strategy Evaluation Voting System
📍 Goal: Run multiple strategies and vote using weighted results.
Tasks:
•	✅ Refactor bb_strategy.py, rsi_strategy.py, etc. into a Strategy class interface
•	✅ Build a vote_strategies() function (as per spec)
•	✅ Integrate into scalping_bot_framework.py
Related Files/Folders:
•	strategies/
•	backend/execution/execution_engine.py
•	scalping_bot_framework.py
________________________________________
🔹 Day 3 – Secure API Key Encryption + Toggle Control
📍 Goal: Encrypt and store API keys securely and allow UI control of bot (start/stop).
Tasks:
•	✅ Create encrypt_key(), decrypt_key() in key/ or utils/
•	✅ Read/write encrypted keys using .env or config
•	✅ Add REST endpoint /toggle_bot to start/stop trading logic
Related Files/Folders:
•	key/key.pub
•	backend/config.py (if needed)
•	scalping_bot_framework.py
•	Add FastAPI Flask server to handle toggling
________________________________________
🔹 Day 4 – AI: LGBM Enhancement + Retrain Trigger
📍 Goal: Enhance your LightGBM model with volatility/volume features and allow retrain from UI.
Tasks:
•	✅ Add new features in lgbm_model_trainer.py
•	✅ Connect model output to strategy engine
•	✅ Add retrain function with flag retrain=True
•	✅ Expose trigger endpoint in dashboard or UI
Related Files/Folders:
•	backend/ml/lgbm_model_trainer.py
•	models/lightgbm_model.pkl
•	scalping_bot_framework.py
________________________________________
🔹 Day 5 – Add LSTM Model Integration
📍 Goal: Use lstm_price_model.h5 to enhance prediction logic alongside LightGBM.
Tasks:
•	✅ Create lstm_predictor.py under ml/
•	✅ Load model & make predictions based on recent OHLCV
•	✅ Fuse output with strategy vote (e.g., override or influence)
Related Files/Folders:
•	backend/ml/lstm_predictor.py (new)
•	models/lstm_price_model.h5
•	scalping_bot_framework.py
________________________________________
🔹 Day 6 – Risk Management & Kill Switch Logic
📍 Goal: Add max drawdown, kill switch endpoint, and order cleanup logic.
Tasks:
•	✅ Add logic to risk_manager.py to track PnL, loss % etc.
•	✅ Create /kill endpoint in REST API
•	✅ Add logic to fetch open orders and cancel them
•	✅ Log kills in a CSV or DB file (future: SQLite or MongoDB)
Related Files/Folders:
•	backend/risk/risk_manager.py
•	scalping_bot_framework.py
•	Add logs/kill_log.csv or backend/db.py
so it enters trade aafter the voting and stays in buy position till at least a profit of 0.45% is reached then adds a trailing stoploss of 0.1%
