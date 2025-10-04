# ui/settings.py

import streamlit as st
import asyncio
from config import load_config, save_config, get_broker_url
from mqtt_client import connect, disconnect
from auth import add_or_update_user
from streamlit.runtime.scriptrunner import RerunException, RerunData

def render_settings():
    st.header("Settings")

    # Load and display current broker config
    cfg = load_config()
    st.subheader("Broker Configuration")
    host = st.text_input("Broker Host", value=cfg["broker_host"])
    port = st.number_input("Broker Port", value=cfg["broker_port"])
    use_tls = st.checkbox("Use TLS", value=cfg["use_tls"])
    buser = st.text_input("Broker Username", value=cfg["broker_user"])
    bpass = st.text_input("Broker Password", type="password", value=cfg["broker_pass"])

    if st.button("💾 Save & Reconnect"):
        # Persist new broker settings
        new_cfg = {**cfg, "broker_host": host, "broker_port": port,
                   "use_tls": use_tls, "broker_user": buser, "broker_pass": bpass}
        save_config(new_cfg)

        # Reconnect MQTT synchronously
        try:
            asyncio.run(disconnect())
            asyncio.run(connect(get_broker_url(new_cfg), buser, bpass, client_id="MowbotFleet"))
        except Exception as e:
            st.error(f"Reconnection failed: {e}")
            # Continue anyway to save the config

        st.success("Broker settings saved and reconnected.")
        # Rerun to update header
        raise RerunException(RerunData())

    st.markdown("---")
    st.subheader("User Management")
    new_user = st.text_input("New Username", key="new_user")
    new_pass = st.text_input("New Password", type="password", key="new_pass")
    if st.button("💾 Save Changes"):
        if not new_user or not new_pass:
            st.error("Username and password cannot be empty.")
        else:
            add_or_update_user(new_user, new_pass)
            st.success("User credentials updated. Please logout and login again.")
