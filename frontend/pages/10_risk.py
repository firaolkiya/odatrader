"""OdaTrade Risk Management page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Risk Management | OdaTrade", layout="wide")
section_header("Risk Management", "OdaTrade Platform")

st.number_input("Max Drawdown %", value=15.0)
st.number_input("Max Trades/Day", value=30)
st.number_input("Stop Loss %", value=2.0)
st.number_input("Take Profit %", value=2.0)
if st.button("Update Risk Limits"):
    st.success("Risk limits updated")
