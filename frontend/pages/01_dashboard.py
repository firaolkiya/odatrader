"""OdaTrade real-time dashboard with WebSocket updates."""
import os
import sys
import time

import streamlit as st
import plotly.graph_objs as go
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from frontend.components.widgets import section_header, metric_row, status_badge
from frontend.auth import require_auth, get_auth_headers, logout_button
from frontend.ws_client import OdaTradeWebSocketClient

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="Dashboard | OdaTrade", layout="wide")
require_auth()
logout_button()

section_header("OdaTrade Dashboard", "Real-time trading platform")

# Initialize WebSocket client
if "ws_client" not in st.session_state:
    ws_url = API_BASE.replace("http://", "ws://").replace("https://", "wss://")
    st.session_state.ws_client = OdaTradeWebSocketClient(ws_url)
    st.session_state.ws_client.connect_all()
    st.session_state.ws_client.connect_bots()

# Fetch platform status
headers = get_auth_headers()
try:
    status_resp = requests.get(f"{API_BASE}/status", headers=headers, timeout=5)
    status_data = status_resp.json() if status_resp.ok else {}
    bots_resp = requests.get(f"{API_BASE}/bots/", headers=headers, timeout=5)
    bots_data = bots_resp.json() if bots_resp.ok else {"bots": [], "aggregate": {}}
except Exception:
    status_data = {}
    bots_data = {"bots": [], "aggregate": {}}

agg = bots_data.get("aggregate", {})
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Running Bots", agg.get("running_bots", 0))
with col2:
    st.metric("Total Bots", agg.get("total_bots", 0))
with col3:
    st.metric("Total Trades", agg.get("total_trades", 0))
with col4:
    pnl = agg.get("aggregate_pnl", 0)
    st.metric("Aggregate PnL", f"${pnl:,.2f}")

# Service health
st.subheader("Service Health")
health_cols = st.columns(3)
with health_cols[0]:
    redis_ok = status_data.get("redis", False)
    st.markdown(f"Redis: {'🟢' if redis_ok else '🔴'}")
with health_cols[1]:
    pg_ok = status_data.get("postgres", False)
    st.markdown(f"PostgreSQL: {'🟢' if pg_ok else '🔴'}")
with health_cols[2]:
    ws_ok = st.session_state.ws_client.is_connected
    st.markdown(f"WebSocket: {'🟢' if ws_ok else '🔴'}")

# Bot list with controls
st.subheader("Active Bots")
bots = bots_data.get("bots", [])
if bots:
    for bot in bots:
        bc1, bc2, bc3, bc4 = st.columns([2, 2, 1, 1])
        with bc1:
            st.write(f"**{bot.get('name', 'Unknown')}** (`{bot.get('bot_id', '')}`)")
        with bc2:
            status_badge(bot.get("status") == "running")
        with bc3:
            if st.button("Start", key=f"start_{bot['bot_id']}"):
                requests.post(f"{API_BASE}/bots/{bot['bot_id']}/start", headers=headers)
                st.rerun()
        with bc4:
            if st.button("Stop", key=f"stop_{bot['bot_id']}"):
                requests.post(f"{API_BASE}/bots/{bot['bot_id']}/stop", headers=headers)
                st.rerun()
else:
    st.info("No bots configured. Create one in Settings or via API.")

# Real-time PnL chart placeholder
st.subheader("Equity Curve")
fig = go.Figure()
fig.add_trace(go.Scatter(y=[5000, 5010, 5005, 5020, 5035], mode="lines", name="Equity",
                          line=dict(color="#00d4aa")))
fig.update_layout(template="plotly_dark", height=300, title="Portfolio Equity")
st.plotly_chart(fig, use_container_width=True)

# Latest WebSocket data
latest = st.session_state.ws_client.get_latest("all")
if latest:
    with st.expander("Latest WebSocket Event"):
        st.json(latest)

# Auto-refresh
time.sleep(5)
st.rerun()
