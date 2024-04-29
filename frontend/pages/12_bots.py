"""Multi-bot management page."""
import os
import sys
import requests
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from frontend.components.widgets import section_header
from frontend.auth import require_auth, get_auth_headers, logout_button

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="Bots | OdaTrade", layout="wide")
require_auth()
logout_button()

section_header("Multi-Bot Management", "Create and manage isolated trading bots")

headers = get_auth_headers()

# Create new bot
with st.expander("Create New Bot", expanded=False):
    name = st.text_input("Bot Name", "BTC Scalper")
    symbols = st.multiselect("Symbols", ["btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt"], default=["btcusdt"])
    strategy = st.selectbox("Strategy", ["strategy_voter", "rsi", "macd", "ml"])
    risk = st.selectbox("Risk Profile", ["conservative", "moderate", "aggressive"])
    balance = st.number_input("Starting Balance", value=5000.0)
    if st.button("Create Bot"):
        resp = requests.post(f"{API_BASE}/bots/", headers=headers, json={
            "name": name, "symbols": symbols, "strategy": strategy,
            "risk_profile": risk, "starting_balance": balance,
        })
        if resp.ok:
            st.success(f"Bot created: {resp.json().get('bot_id')}")
            st.rerun()
        else:
            st.error(f"Failed: {resp.text}")

# List bots
try:
    resp = requests.get(f"{API_BASE}/bots/", headers=headers, timeout=5)
    data = resp.json() if resp.ok else {"bots": [], "aggregate": {}}
except Exception:
    data = {"bots": [], "aggregate": {}}

agg = data.get("aggregate", {})
st.metric("Aggregate PnL", f"${agg.get('aggregate_pnl', 0):,.2f}")

bots = data.get("bots", [])
if bots:
    for bot in bots:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.markdown(f"### {bot.get('name', 'Unknown')}")
                st.caption(f"ID: `{bot.get('bot_id')}` | Strategy: {bot.get('strategy')}")
                st.caption(f"Symbols: {', '.join(bot.get('symbols', []))}")
            with c2:
                status = bot.get("status", "unknown")
                color = "green" if status == "running" else "orange"
                st.markdown(f"Status: :{color}[{status.upper()}]")
                st.caption(f"Risk: {bot.get('risk_profile', 'moderate')}")
            with c3:
                bid = bot.get("bot_id")
                if st.button("▶ Start", key=f"s_{bid}"):
                    requests.post(f"{API_BASE}/bots/{bid}/start", headers=headers)
                    st.rerun()
                if st.button("⏹ Stop", key=f"x_{bid}"):
                    requests.post(f"{API_BASE}/bots/{bid}/stop", headers=headers)
                    st.rerun()
                if st.button("📊 Details", key=f"d_{bid}"):
                    detail = requests.get(f"{API_BASE}/bots/{bid}", headers=headers)
                    if detail.ok:
                        st.json(detail.json())
else:
    st.info("No bots yet. Create one above.")

if st.button("⏹ Stop All Bots"):
    requests.post(f"{API_BASE}/bots/stop-all", headers=headers)
    st.warning("All bots stopped")
    st.rerun()
