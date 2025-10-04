# app.py

import streamlit as st
import asyncio
from config import load_config, get_broker_url, get_broker_credentials
from auth import ensure_default_admin
from mqtt_client import connect, is_connected
from ui.login import render_login
from ui.layout import render_sidebar, render_dashboard, render_missions_page
from ui.pages.settings import render_settings

st.set_page_config(page_title="MowbotFleet", layout="wide")

# Ensure default admin user exists
ensure_default_admin()

# Authentication gating
if "user" not in st.session_state:
    render_login()
    st.stop()

page = render_sidebar()

if page != "Settings" and not is_connected():
    cfg = load_config()
    username, password = get_broker_credentials(cfg)
    asyncio.run(connect(
        get_broker_url(cfg),
        username,
        password,
        client_id="MowbotFleet"
    ))

# Render the selected page
if page == "Dashboard":
    render_dashboard()
elif page == "Missions":
    render_missions_page()
elif page == "Settings":
    render_settings()
