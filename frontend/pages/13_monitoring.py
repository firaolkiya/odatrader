"""OdaTrade monitoring and observability dashboard."""
import os
import sys
import requests
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from frontend.components.widgets import section_header
from frontend.auth import require_auth, get_auth_headers, logout_button

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="Monitoring | OdaTrade", layout="wide")
require_auth()
logout_button()

section_header("Platform Monitoring", "Service health, system metrics, and bot observability")

headers = get_auth_headers()

# Health check
try:
    health = requests.get(f"{API_BASE}/monitoring/health", timeout=5).json()
    system = requests.get(f"{API_BASE}/monitoring/system", timeout=5).json()
    services = requests.get(f"{API_BASE}/monitoring/services", timeout=5).json()
    bots_summary = requests.get(f"{API_BASE}/monitoring/bots/summary", headers=headers, timeout=5).json()
except Exception as e:
    st.error(f"Monitoring API unavailable: {e}")
    st.stop()

# Platform health
st.subheader("Platform Health")
hc1, hc2, hc3, hc4 = st.columns(4)
with hc1:
    st.metric("Status", health.get("status", "unknown").upper())
with hc2:
    st.metric("Uptime", f"{health.get('uptime_seconds', 0):.0f}s")
with hc3:
    st.metric("WS Connections", health.get("websocket_connections", 0))
with hc4:
    st.metric("Version", health.get("version", "?"))

# System resources
st.subheader("System Resources")
sc1, sc2, sc3 = st.columns(3)
with sc1:
    st.metric("CPU", f"{system.get('cpu_percent', 0):.1f}%")
with sc2:
    mem = system.get("memory", {})
    st.metric("Memory", f"{mem.get('percent', 0):.1f}%")
    st.caption(f"{mem.get('used_gb', 0):.1f} / {mem.get('total_gb', 0):.1f} GB")
with sc3:
    disk = system.get("disk", {})
    st.metric("Disk", f"{disk.get('percent', 0):.1f}%")

# Service status
st.subheader("Services")
for service, info in services.items():
    with st.expander(f"{service.upper()}", expanded=True):
        if isinstance(info, dict):
            status = info.get("status", "unknown")
            icon = "🟢" if status in ("healthy", "ok") else "🔴"
            st.markdown(f"{icon} **{status}**")
            for k, v in info.items():
                if k != "status":
                    st.text(f"{k}: {v}")
        else:
            st.json(info)

# Bot monitoring
st.subheader("Bot Monitoring")
agg = bots_summary.get("aggregate", {})
mc1, mc2, mc3 = st.columns(3)
with mc1:
    st.metric("Total Bots", agg.get("total_bots", 0))
with mc2:
    st.metric("Running", agg.get("running_bots", 0))
with mc3:
    st.metric("Aggregate PnL", f"${agg.get('aggregate_pnl', 0):,.2f}")

bot_details = bots_summary.get("bots", [])
if bot_details:
    for bot in bot_details:
        with st.container(border=True):
            st.markdown(f"**{bot.get('name', bot.get('bot_id'))}**")
            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                st.text(f"Status: {bot.get('status', '?')}")
                st.text(f"Pipeline: {'running' if bot.get('pipeline_running') else 'stopped'}")
            with bc2:
                metrics = bot.get("metrics", {})
                st.text(f"Signals: {metrics.get('signals_generated', 0)}")
                st.text(f"Orders: {metrics.get('orders_filled', 0)}")
            with bc3:
                st.text(f"Risk Approved: {metrics.get('risk_approved', 0)}")
                st.text(f"Risk Rejected: {metrics.get('risk_rejected', 0)}")
else:
    st.info("No bots to monitor")

# Reports
st.subheader("Quick Reports")
if st.button("Generate Performance Report"):
    resp = requests.get(f"{API_BASE}/reports/performance", headers=headers, timeout=10)
    if resp.ok:
        st.json(resp.json())

if st.button("Generate Risk Report"):
    resp = requests.get(f"{API_BASE}/reports/risk", headers=headers, timeout=10)
    if resp.ok:
        st.json(resp.json())
