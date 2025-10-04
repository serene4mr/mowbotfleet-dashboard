# ui/components/mission_table.py

import streamlit as st
from datetime import datetime
from mqtt_client import fleet_state

def render_active_missions():
    """Render active missions table with real-time updates"""
    st.markdown("#### 🔄 Active Missions")
    
    # Get active missions (placeholder - will be implemented with mission tracking)
    active_missions = get_active_missions()
    
    if not active_missions:
        st.write("No active missions.")
        return
    
    # Create missions table
    for mission in active_missions:
        with st.expander(f"Mission {mission['order_id']} - {mission['agv_serial']}", expanded=True):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
            
            with col1:
                st.write(f"**Order:** {mission['order_id']}")
                st.write(f"**AGV:** {mission['agv_serial']}")
            
            with col2:
                status_color = {
                    'Running': '🟢',
                    'Paused': '🟡',
                    'Completed': '✅',
                    'Failed': '🔴',
                    'Cancelled': '❌'
                }.get(mission['status'], '🔵')
                st.write(f"**Status:** {status_color} {mission['status']}")
            
            with col3:
                st.write(f"**Progress:** {mission['progress']}")
            
            with col4:
                st.write(f"**Nodes:** {mission['current_node']}/{mission['total_nodes']}")
            
            with col5:
                # Mission controls
                if mission['status'] == 'Running':
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("⏸️ Pause", key=f"pause_{mission['order_id']}"):
                            pause_mission(mission['order_id'], mission['agv_serial'])
                    with col_b:
                        if st.button("❌ Cancel", key=f"cancel_{mission['order_id']}"):
                            cancel_mission(mission['order_id'], mission['agv_serial'])
                
                elif mission['status'] == 'Paused':
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("▶️ Resume", key=f"resume_{mission['order_id']}"):
                            resume_mission(mission['order_id'], mission['agv_serial'])
                    with col_b:
                        if st.button("❌ Cancel", key=f"cancel_{mission['order_id']}"):
                            cancel_mission(mission['order_id'], mission['agv_serial'])

def get_active_missions():
    """Get active missions (placeholder implementation)"""
    # This will be replaced with real mission tracking
    return []

def pause_mission(order_id: str, agv_serial: str):
    """Pause a mission"""
    st.success(f"Mission {order_id} paused")
    # TODO: Implement actual pause functionality

def resume_mission(order_id: str, agv_serial: str):
    """Resume a mission"""
    st.success(f"Mission {order_id} resumed")
    # TODO: Implement actual resume functionality

def cancel_mission(order_id: str, agv_serial: str):
    """Cancel a mission"""
    st.success(f"Mission {order_id} cancelled")
    # TODO: Implement actual cancel functionality
