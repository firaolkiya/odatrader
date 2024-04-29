"""Authentication for OdaTrade Streamlit dashboard."""
import os
import streamlit as st
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


def login_form():
    st.sidebar.subheader("🔐 Login")
    username = st.sidebar.text_input("Username", value="admin")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        try:
            resp = requests.post(f"{API_BASE}/auth/login", json={
                "username": username, "password": password,
            }, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                st.session_state["token"] = data["access_token"]
                st.session_state["role"] = data["role"]
                st.session_state["username"] = username
                st.session_state["authenticated"] = True
                st.sidebar.success(f"Logged in as {username}")
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")
        except Exception as e:
            st.sidebar.error(f"Login failed: {e}")
    return st.session_state.get("authenticated", False)


def require_auth():
    if not st.session_state.get("authenticated"):
        login_form()
        st.stop()


def get_auth_headers() -> dict:
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def logout_button():
    if st.session_state.get("authenticated"):
        if st.sidebar.button("Logout"):
            for key in ["token", "role", "username", "authenticated"]:
                st.session_state.pop(key, None)
            st.rerun()
