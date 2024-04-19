"""OdaTrade Alerts page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Alerts | OdaTrade", layout="wide")
section_header("Alerts", "OdaTrade Platform")

channel = st.selectbox("Channel", ["Webhook", "Email", "Telegram"])
condition = st.text_input("Condition", "drawdown > 10%")
if st.button("Add Alert"):
    st.success(f"Alert created: {condition} via {channel}")
