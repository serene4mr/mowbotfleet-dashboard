# ui/controls.py

import streamlit as st
from mqtt_client import fleet_state

def render_quick_controls():
    """
    Render quick control buttons for selected AGV.
    """
    selected_serial = st.session_state.get('selected_agv')
    
    if not selected_serial:
        st.write("Select an AGV to enable controls.")
        return
    
    agv = fleet_state.get(selected_serial)
    if not agv:
        st.write("Selected AGV not available.")
        return

    st.markdown(f"**Quick Controls for {selected_serial}**")
    
    # Create button layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛑 E-STOP", type="primary", width='stretch'):
            send_estop_command(selected_serial)
            st.success(f"E-STOP sent to {selected_serial}")
    
    with col2:
        if st.button("▶️ Resume", width='stretch'):
            send_resume_command(selected_serial)
            st.success(f"Resume sent to {selected_serial}")
    
    with col3:
        if st.button("⏸️ Pause", width='stretch'):
            send_pause_command(selected_serial)
            st.success(f"Pause sent to {selected_serial}")

def send_estop_command(serial: str):
    """Send emergency stop command to AGV"""
    # TODO: Implement VDA5050 instant action command
    print(f"Sending E-STOP to {serial}")

def send_resume_command(serial: str):
    """Send resume command to AGV"""
    # TODO: Implement VDA5050 resume command
    print(f"Sending Resume to {serial}")

def send_pause_command(serial: str):
    """Send pause command to AGV"""
    # TODO: Implement VDA5050 pause command
    print(f"Sending Pause to {serial}")
