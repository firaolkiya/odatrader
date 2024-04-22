"""OdaTrade FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.api.router import api_router
from backend.api.routes.health import router as health_router
from backend.api.routes.portfolio import router as portfolio_router
from backend.api.routes.trades import router as trades_router
from backend.api.routes.strategies_api import router as strategies_router
from backend.api.routes.backtest_api import router as backtest_router
from backend.api.routes.alerts_api import router as alerts_router
from backend.api.routes.metrics import router as metrics_router
from backend.api.routes.ws_prices import router as ws_router
from backend.api.v2.routes import router as v2_router

app = FastAPI(title="OdaTrade API", version="1.0.0", description="OdaTrade Trading Platform API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(health_router)
app.include_router(api_router)
app.include_router(portfolio_router)
app.include_router(trades_router)
app.include_router(strategies_router)
app.include_router(backtest_router)
app.include_router(alerts_router)
app.include_router(metrics_router)
app.include_router(ws_router)
app.include_router(v2_router)

bot_running = False
bot_process = None

@app.get("/status")
def status():
    return {"running": bot_running, "service": "OdaTrade"}

@app.post("/start")
def start():
    global bot_running
    bot_running = True
    return {"status": "started", "service": "OdaTrade"}

@app.post("/stop")
def stop():
    global bot_running
    bot_running = False
    return {"status": "stopped", "service": "OdaTrade"}
