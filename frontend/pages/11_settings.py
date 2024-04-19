"""OdaTrade Settings page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Settings | OdaTrade", layout="wide")
section_header("Settings", "OdaTrade Platform")

st.text_input("Binance API Key", type="password")
st.text_input("Groq API Key", type="password")
st.selectbox("Default Symbols", ["BTCUSDT", "ETHUSDT"], accept_new_options=True)
if st.button("Save Settings"):
    st.success("Settings saved")
