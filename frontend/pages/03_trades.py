"""OdaTrade Trade History page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Trade History | OdaTrade", layout="wide")
section_header("Trade History", "OdaTrade Platform")

st.dataframe({"Time": [], "Symbol": [], "Side": [], "Price": [], "PnL": [], "Strategy": []})
