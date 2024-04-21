# OdaTrade Architecture

## Overview

OdaTrade is a modular crypto trading platform.

## Modules

- **odatrade/** — Core package (settings, logging, cache, events)
- **backend/api/** — FastAPI REST + WebSocket endpoints
- **backend/strategies/** — Technical, ML, and AI strategies
- **backend/backtesting/** — Historical simulation engine
- **backend/portfolio/** — Position tracking and analytics
- **backend/risk/** — Risk limits, VaR, position sizing
- **backend/notifications/** — Webhook, email, Telegram alerts
- **backend/scanner/** — Multi-symbol market scanner
- **frontend/** — Streamlit multi-page dashboard

## Data Flow

```
Binance WS → market_data → feature_engineering → StrategyVoter → ExecutionEngine → trades
                                                      ↓
                                              Streamlit Dashboard
```
