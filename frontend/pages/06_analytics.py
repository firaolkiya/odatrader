"""OdaTrade Analytics page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="Analytics | OdaTrade", layout="wide")
section_header("Analytics", "OdaTrade Platform")

import plotly.graph_objs as go
fig = go.Figure()
fig.update_layout(title="OdaTrade Equity Curve", template="plotly_dark")
st.plotly_chart(fig)
