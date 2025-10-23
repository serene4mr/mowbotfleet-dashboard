# ui/pages/missions.py

import streamlit as st
from datetime import datetime
from mqtt_client import fleet_state
from ..components.mission_dispatch import render_mission_dispatch
from ..components.mission_table import render_active_missions
from ..components.mission_controls import render_mission_status_summary
from i18n_manager import t

def render_missions():
    """Render the Missions page"""
    st.markdown(f"### 🚀 {t('missions.title')}")
    
    # Mission status summary (top) - Commented out
    # render_mission_status_summary()
    # 
    # st.markdown("---")
    
    # Active missions table - Commented out
    # render_active_missions()
    # 
    # st.markdown("---")
    
    # Mission dispatch form (bottom)
    render_mission_dispatch()
