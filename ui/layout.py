# ui/layout.py

import streamlit as st
from .pages.dashboard import render_header, render_row1, render_row2, render_debug
from .pages.settings import render_settings
from .pages.missions import render_missions
from streamlit.runtime.scriptrunner import RerunException, RerunData
from mqtt_client import get_broker_info
from i18n_manager import t

def render_sidebar():
    if st.sidebar.button(t("navigation.logout")):
        st.session_state.clear()
        raise RerunException(RerunData())
    
    # Broker connection status in sidebar
    broker_info = get_broker_info()
    if broker_info["status"] == "Connected":
        tls_icon = "🔒" if broker_info["tls"] else "🔓"
        st.sidebar.success(f"🟢 {t('dashboard.broker_status')}: {broker_info['host']}:{broker_info['port']} {tls_icon}")
        st.sidebar.caption(f"User: {broker_info['username']}")
    else:
        st.sidebar.error(f"🔴 {t('dashboard.broker_status')}: {t('dashboard.disconnected')}")
    
    st.sidebar.markdown("---")
    
    # Navigation - pure Streamlit state management, no manual index
    selected_page = st.sidebar.radio(
        t("navigation.navigate"), 
        [t("navigation.dashboard"), t("navigation.missions"), t("navigation.settings")],
        key="page_navigation"
    )
    
    return selected_page

def render_dashboard():
    render_header()
    render_row1()
    render_row2()
    render_debug()

def render_missions_page():
    render_missions()
