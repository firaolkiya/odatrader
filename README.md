# OdaTrade

Professional crypto trading platform with multi-strategy voting, ML predictions, backtesting, and real-time dashboard.

## Features

- Live market data ingestion (Binance WebSocket)
- 10+ technical strategies with weighted voting
- LightGBM ML predictions and Groq AI signals
- Paper trading with risk management and kill switch
- Backtesting engine with performance reports
- Multi-page Streamlit dashboard
- REST API with JWT auth, WebSocket streams, and Prometheus metrics
- Alert system (webhook, email, Telegram)
- Portfolio analytics and trade journal

## Quick Start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp config/.env.example .env
uvicorn backend.api.main:app --reload
streamlit run frontend/app.py
```

## Architecture

See `docs/ARCHITECTURE.md` for module overview.

## Author

OdaTrade — Personal Algorithmic Trading Platform
