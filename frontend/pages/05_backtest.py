"""OdaTrade Backtest page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Backtest | OdaTrade", layout="wide")
section_header("Backtest", "OdaTrade Platform")

symbol = st.selectbox("Symbol", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
strategy = st.selectbox("Strategy", ["RSI", "MACD", "EMA", "Bollinger", "Stochastic", "ADX"])
days = st.slider("Days", 7, 365, 30)
if st.button("Run Backtest"):
    st.success(f"Backtest queued: {symbol} / {strategy} / {days}d")
