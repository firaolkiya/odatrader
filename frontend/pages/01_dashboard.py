"""OdaTrade Dashboard page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Dashboard | OdaTrade", layout="wide")
section_header("Dashboard", "OdaTrade Platform")

metric_row({"Balance": "$5,000", "PnL": "+$0", "Trades": "0", "Win Rate": "0%"})
st.info("Connect to OdaTrade API to view live data.")
