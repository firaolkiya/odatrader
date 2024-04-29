# OdaTrade Architecture

## Overview

OdaTrade is a modular, event-driven trading platform supporting multi-bot deployment,
adaptive strategy voting, and multi-asset execution.

## Modules

| Package | Purpose |
|---------|---------|
| `backend/engine/` | Adaptive voter, regime classifier, pair scorer |
| `backend/strategies/` | Technical, ML, and AI signal generators |
| `backend/gateway/` | Exchange connectors (Binance, Alpaca, OANDA) |
| `backend/exec/` | Order routing, fee model, slippage |
| `backend/derivatives/` | Leverage, funding rates, Greeks |
| `backend/backtesting/` | Engine, walk-forward, Monte Carlo, replay |
| `backend/events/` | Async event pipeline (market → strategy → risk → orders) |
| `backend/bots/` | Multi-bot manager, worker, registry |
| `backend/api/` | FastAPI REST + WebSocket endpoints |
| `backend/portfolio/` | Position tracking and analytics |
| `backend/risk/` | VaR, exposure limits, kill switch |
| `odatrade/core/` | Event bus, Redis client, validators, settings |
| `frontend/` | Streamlit multi-page dashboard |
| `ui/` | React SPA (Vite + Tailwind) |
| `tests/` | Pytest suite (300+ tests) |

## Data Flow

```
Market Gateway → market_data event → Feature Engineering
                                          ↓
                                   AdaptiveVoter (regime-aware)
                                          ↓
                              strategy_signal → Risk Check → Orders → PnL
                                          ↓
                              Streamlit / React Dashboard / Prometheus
```

## Configuration

- `config/adaptive.yaml` — voting weights and threshold slopes
- `config/instruments.yaml` — tradeable instrument definitions
- `config/strategies.yaml` — per-strategy parameters
- `config/.env.example` — environment variable template

## Testing

- `requirements-core.txt` — slim dependency set for CI
- `validate-at-base.sh` — run tests at a specific git revision
- `.github/workflows/ci.yml` — GitHub Actions pipeline
