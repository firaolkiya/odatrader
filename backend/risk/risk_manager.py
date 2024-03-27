# backend/risk/risk_manager.py

from datetime import datetime, timezone
from collections import defaultdict
import os, sys
import logging
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import (
    MAX_TRADES_PER_DAY, MAX_DRAWDOWN, STOP_LOSS_PCT, 
    TAKE_PROFIT_PCT, FIXED_RISK_PCT, DAILY_LOSS_LIMIT,
    TRAILING_STOP_PCT
)

from backend.risk.kill_switch import (
    is_kill_switch_active, activate_kill_switch, deactivate_kill_switch
)

# === File for storing trailing stop data ===
TRAILING_FILE = os.path.join(os.path.dirname(__file__), "trailing_highs.json")

# === Risk Parameters ===
MAX_DRAWDOWN_PCT = MAX_DRAWDOWN

# === Trade Log (per-symbol, per-day) ===
trade_logs = defaultdict(list)

# === Cumulative Daily PnL Tracker ===
cumulative_daily_loss = defaultdict(float)

# === Track last kill switch reset date ===
last_reset_date = datetime.now(timezone.utc).date()

# === Load Trailing Data from Disk ===
def load_trailing_data():
    if os.path.exists(TRAILING_FILE):
        try:
            with open(TRAILING_FILE, "r") as f:
                data = json.load(f)
                return defaultdict(lambda: None, data)
        except Exception as e:
            logging.error(f"Failed to load trailing stop data: {e}")
    return defaultdict(lambda: None)

# === Save Trailing Data to Disk ===
def save_trailing_data():
    try:
        with open(TRAILING_FILE, "w") as f:
            json.dump(dict(trailing_data), f, default=str)
    except Exception as e:
        logging.error(f"Failed to save trailing stop data: {e}")

# Initialize trailing stop context
trailing_data = load_trailing_data()

def reset_trailing(symbol):
    """Remove a symbol's trailing stop info."""
    if symbol in trailing_data:
        trailing_data.pop(symbol, None)
        save_trailing_data()

def check_risk_limits(signal, price, current_position, balance):
    global last_reset_date

    now = datetime.now(timezone.utc)
    today = now.date()
    symbol = signal.get("symbol", "").upper()

    # === Reset kill switch at the start of each new day ===
    if today > last_reset_date:
        deactivate_kill_switch()
        last_reset_date = today
        logging.info(f"[RISK] New day detected ({today}). Kill switch reset.")

    if is_kill_switch_active():
        return False, "[RISK] Kill Switch is Active. No trading allowed."

    # === Clean old logs for today ===
    trade_logs[symbol] = [t for t in trade_logs[symbol] if t["timestamp"].date() == today]

    # === Max Trades Per Day ===
    if len(trade_logs[symbol]) >= MAX_TRADES_PER_DAY:
        return False, f"[RISK] Max trades ({MAX_TRADES_PER_DAY}) reached for {symbol} today."

    # === Position Sizing ===
    usd_risk = max(balance * FIXED_RISK_PCT, 50)  # Minimum $50 trade
    position_size = usd_risk / price
    signal["position_size"] = position_size

    # === SL/TP + Trailing Stop Enforcement ===
    if current_position:
        entry_price = current_position.get("entry_price")
        if entry_price:
            change_pct = (price - entry_price) / entry_price

            # Stop Loss
            if change_pct <= -STOP_LOSS_PCT:
                reset_trailing(symbol)
                return True, f"Forced SELL by Stop Loss ({change_pct:.2%})"

            # Take Profit (hard TP)
            if change_pct >= TAKE_PROFIT_PCT:
                reset_trailing(symbol)
                return True, f"Forced SELL by Take Profit ({change_pct:.2%})"

            # If profit < 0.45% → don't sell yet
            if change_pct < 0.0050:
                reset_trailing(symbol)
                return False, f"[RISK] Profit below 0.50% threshold ({change_pct:.2%})"

            # Once above 0.45%, start or continue trailing stop
            if not trailing_data[symbol]:
                # Start tracking
                trailing_data[symbol] = {
                    "entry_price": entry_price,
                    "trailing_high": price,
                    "start_time": now.isoformat()
                }
                save_trailing_data()
            else:
                # Update peak price
                if price > trailing_data[symbol]["trailing_high"]:
                    trailing_data[symbol]["trailing_high"] = price
                    save_trailing_data()

                # Calculate drop from peak
                drop_pct = (price - trailing_data[symbol]["trailing_high"]) / trailing_data[symbol]["trailing_high"]

                if drop_pct <= -TRAILING_STOP_PCT:
                    reset_trailing(symbol)
                    return True, f"Forced SELL by Trailing Stop ({drop_pct:.2%} from peak)"

    # === Daily Drawdown per Symbol ===
    net_pnl_today = sum(t["net_pnl"] for t in trade_logs[symbol])
    if net_pnl_today < -balance * MAX_DRAWDOWN_PCT:
        return False, f"[RISK] Max daily drawdown reached for {symbol}: {net_pnl_today:.2f}"

    # === Cumulative Daily PnL ===
    total_loss_today = sum(sum(t["net_pnl"] for t in trades) for trades in trade_logs.values())
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
