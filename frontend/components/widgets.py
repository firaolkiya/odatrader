"""Shared Streamlit UI components for OdaTrade."""
import streamlit as st

def metric_row(metrics: dict):
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        col.metric(label, value)

def section_header(title: str, subtitle: str = ""):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)

def status_badge(running: bool):
    color = "green" if running else "red"
    label = "RUNNING" if running else "STOPPED"
    st.markdown(f'<span style="color:{color};font-weight:bold;">● {label}</span>', unsafe_allow_html=True)
