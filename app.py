# app.py

import streamlit as st
import asyncio
from config import load_config, get_broker_url
from auth import ensure_default_admin
from mqtt_client import connect, connected
from ui.login import render_login
from ui.layout import render_sidebar, render_dashboard, render_settings

st.set_page_config(page_title="MowbotFleet", layout="wide")

# Ensure default admin user exists
ensure_default_admin()

# Authentication gating
if "user" not in st.session_state:
    render_login()
    st.stop()

# Sidebar and routing
page = render_sidebar()

# Auto-connect to broker on non-Settings pages if not already connected
if page != "Settings" and not connected:
    cfg = load_config()
    broker_url = get_broker_url(cfg)
    # Run connect coroutine directly
    asyncio.run(connect(
        broker_url, cfg["broker_user"], cfg["broker_pass"], client_id="MowbotFleet"
    ))

# Render selected page
if page == "Dashboard":
    render_dashboard()
elif page == "Settings":
    render_settings()
