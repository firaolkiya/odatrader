"""OdaTrade Strategies page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Strategies | OdaTrade", layout="wide")
section_header("Strategies", "OdaTrade Platform")

strategies = ["RSI", "MACD", "EMA Crossover", "Bollinger", "Stochastic", "ADX", "VWAP", "Ichimoku", "ML", "GPT"]
for s in strategies:
    enabled = st.toggle(s, value=True, key=s)
    weight = st.slider(f"{s} weight", 0.0, 1.0, 0.1, key=f"w_{s}")
