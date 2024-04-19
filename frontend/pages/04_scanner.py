"""OdaTrade Market Scanner page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Market Scanner | OdaTrade", layout="wide")
section_header("Market Scanner", "OdaTrade Platform")

st.multiselect("Symbols", ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"], default=["BTCUSDT"])
filter_type = st.selectbox("Filter", ["RSI Oversold", "RSI Overbought", "High Volume", "Breakout"])
if st.button("Scan"):
    st.write("Scan results will appear here.")
