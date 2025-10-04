# ui/pages/missions.py

import streamlit as st
from datetime import datetime
from mqtt_client import fleet_state
from ..components.mission_dispatch import render_mission_dispatch
from ..components.mission_table import render_active_missions
from ..components.mission_controls import render_mission_status_summary

def render_missions():
    """Render the Missions page"""
    st.markdown("### 🚀 Missions")
    
    # Mission dispatch form
    render_mission_dispatch()
    
    st.markdown("---")
    
    # Active missions table
    render_active_missions()
    
    st.markdown("---")
    
    # Mission status summary
    render_mission_status_summary()
