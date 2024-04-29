# OdaTrade

Professional algorithmic trading platform with adaptive multi-strategy voting, ML predictions,
backtesting, and real-time dashboards.

## Features

- Adaptive confidence voting with regime-aware entry/exit thresholds
- 15+ technical strategies (RSI, MACD, Supertrend, Donchian, grid, market maker, etc.)
- Multi-asset instruments (crypto spot/perp, equities, forex) via gateway adapters
- LightGBM ML predictions, walk-forward backtesting, Monte Carlo simulation
- Paper and live trading with risk management, kill switch, and VaR
- FastAPI REST + WebSocket API with JWT auth and Prometheus metrics
- Streamlit dashboard (14 pages) and React SPA (`ui/`)
- Multi-bot orchestration with Redis-backed event bus

## Quick Start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp config/.env.example .env

# API (port 8000)
uvicorn backend.api.main:app --reload

# Streamlit dashboard (port 8501)
streamlit run frontend/app.py

# React SPA (port 3000)
cd ui && npm install && npm run dev
```

Login: `admin` / `odatrade-admin`

## Testing

```bash
pip install -r requirements-core.txt
pytest tests/ -q

# Docker test profile (offline, SQLite + Redis)
docker compose -f docker-compose.test.yml run --rm odatrade-test

# Regression check at a specific commit
./validate-at-base.sh HEAD
```

## Architecture

See `docs/ARCHITECTURE.md`.

## Deployment

See `docs/DEPLOYMENT.md` for Docker Compose, Kubernetes, AWS, GCP, and DigitalOcean.
