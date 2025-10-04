# ui/components/mission_controls.py

import streamlit as st
from datetime import datetime

def render_mission_status_summary():
    """Render mission status summary"""
    st.markdown("#### 📊 Mission Status Summary")
    
    # Get mission statistics (placeholder implementation)
    stats = get_mission_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Missions", stats['total'])
    
    with col2:
        st.metric("Active", stats['active'], delta=None)
    
    with col3:
        st.metric("Completed", stats['completed'], delta=None)
    
    with col4:
        st.metric("Failed", stats['failed'], delta=None)
    
    st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

def get_mission_statistics():
    """Get mission statistics (placeholder implementation)"""
    # This will be replaced with real mission tracking
    return {
        'total': 0,
        'active': 0,
        'completed': 0,
        'failed': 0
    }
