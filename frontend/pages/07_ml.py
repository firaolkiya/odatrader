"""OdaTrade ML Models page."""
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from frontend.components.widgets import section_header, metric_row

st.set_page_config(page_title="ML Models | OdaTrade", layout="wide")
section_header("ML Models", "OdaTrade Platform")

st.selectbox("Model", ["LightGBM", "LSTM", "Ensemble"])
col1, col2 = st.columns(2)
with col1:
    if st.button("Retrain Model"):
        st.info("Training started...")
with col2:
    st.download_button("Export Model", data=b"", file_name="model.pkl")
