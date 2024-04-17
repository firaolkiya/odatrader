"""OdaTrade multi-page Streamlit application."""
import streamlit as st

st.set_page_config(page_title="OdaTrade", page_icon="📈", layout="wide")

pages = {
    "Trading": [
        st.Page("pages/01_dashboard.py", title="Dashboard", icon="📊"),
        st.Page("pages/02_portfolio.py", title="Portfolio", icon="💼"),
        st.Page("pages/03_trades.py", title="Trades", icon="📋"),
        st.Page("pages/04_scanner.py", title="Scanner", icon="🔍"),
    ],
    "Analysis": [
        st.Page("pages/05_backtest.py", title="Backtest", icon="🧪"),
        st.Page("pages/06_analytics.py", title="Analytics", icon="📈"),
        st.Page("pages/07_ml.py", title="ML Models", icon="🤖"),
    ],
    "Config": [
        st.Page("pages/08_strategies.py", title="Strategies", icon="⚙️"),
        st.Page("pages/09_alerts.py", title="Alerts", icon="🔔"),
        st.Page("pages/10_risk.py", title="Risk", icon="🛡️"),
        st.Page("pages/11_settings.py", title="Settings", icon="🔧"),
    ],
}

pg = st.navigation(pages)
pg.run()
