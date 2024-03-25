# backend/risk/risk_manager.py

from datetime import datetime, timezone
from collections import defaultdict
import os, sys
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import (
    MAX_TRADES_PER_DAY, MAX_DRAWDOWN, STOP_LOSS_PCT, 
    TAKE_PROFIT_PCT, FIXED_RISK_PCT, DAILY_LOSS_LIMIT
)

from backend.risk.kill_switch import (
    is_kill_switch_active, activate_kill_switch, deactivate_kill_switch
)

# === Risk Parameters ===
MAX_DRAWDOWN_PCT = MAX_DRAWDOWN

# === Trade Log (per-symbol, per-day) ===
trade_logs = defaultdict(list)

# === Cumulative Daily PnL Tracker ===
cumulative_daily_loss = defaultdict(float)

def check_risk_limits(signal, price, current_position, balance):
    now = datetime.now(timezone.utc)
    today = now.date()
    symbol = signal.get("symbol", "").upper()

    # Check if it's a new day to reset kill switch
    deactivate_kill_switch()

    if is_kill_switch_active():
        return False, "[RISK] Kill Switch is Active. No trading allowed."

    # Clean old logs for today
    trade_logs[symbol] = [t for t in trade_logs[symbol] if t["timestamp"].date() == today]

    # === Max Trades Per Day ===
    if len(trade_logs[symbol]) >= MAX_TRADES_PER_DAY:
        return False, f"[RISK] Max trades ({MAX_TRADES_PER_DAY}) reached for {symbol} today."

    # === Position Sizing ===
    usd_risk = max(balance * FIXED_RISK_PCT, 50)  # Minimum $50 trade
    position_size = usd_risk / price
    signal["position_size"] = position_size

    # === SL/TP Enforcement ===
    if signal["action"].upper() == "SELL" and current_position:
        entry_price = current_position.get("entry_price")
        if entry_price:
            change_pct = (price - entry_price) / entry_price

            if change_pct <= -STOP_LOSS_PCT:
                return True, f"Forced SELL by Stop Loss ({change_pct:.2%})"

            if change_pct >= TAKE_PROFIT_PCT:
                return True, f"Forced SELL by Take Profit ({change_pct:.2%})"

            if change_pct < 0.0045:
                return False, f"[RISK] Profit below 0.45% threshold ({change_pct:.2%})"

    # === Daily Drawdown per Symbol ===
    net_pnl_today = sum(t["net_pnl"] for t in trade_logs[symbol])
    if net_pnl_today < -balance * MAX_DRAWDOWN_PCT:
        return False, f"[RISK] Max daily drawdown reached for {symbol}: {net_pnl_today:.2f}"

    # === Cumulative Daily PnL ===
    total_loss_today = sum([sum(t["net_pnl"] for t in trades) for trades in trade_logs.values()])
    if total_loss_today < -DAILY_LOSS_LIMIT:
        activate_kill_switch()
        return False, f"[RISK] DAILY LOSS LIMIT REACHED (${total_loss_today:.2f}). Kill Switch Activated."

    return True, "PASS"

def register_trade(signal, net_pnl):
    now = datetime.now(timezone.utc)
    symbol = signal.get("symbol", "").upper()

    trade_logs[symbol].append({
        "timestamp": now,
        "action": signal.get("action", "N/A"),
        "strategy": signal.get("strategy", "N/A"),
        "net_pnl": net_pnl
    })
