"""OdaTrade Portfolio page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Portfolio | OdaTrade", layout="wide")
section_header("Portfolio", "OdaTrade Platform")

st.subheader("Open Positions")
st.dataframe({"Symbol": [], "Qty": [], "Entry": [], "PnL": []})
