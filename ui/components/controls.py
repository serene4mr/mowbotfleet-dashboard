# ui/components/controls.py

import streamlit as st
from mqtt_client import fleet_state

@st.fragment(run_every="1s")
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
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("🛑 E-STOP", type="primary", width='stretch'):
            send_estop_command(selected_serial)
            st.success(f"E-STOP sent to {selected_serial}")
    
    with col2:
        # Single toggle button for Pause/Resume based on AGV state
        is_paused = get_agv_pause_state(agv)
        
        if is_paused:
            if st.button("▶️ Resume Mission", type="primary", width='stretch'):
                send_resume_command(selected_serial)
                st.success(f"Resume sent to {selected_serial}")
        else:
            if st.button("⏸️ Pause Mission", width='stretch'):
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

def get_agv_pause_state(agv):
    """
    Determine if AGV is currently paused based on its state.
    This is a placeholder implementation - in real scenario, 
    this would check the AGV's actual pause state from VDA5050 data.
    """
    # For now, we'll use a simple heuristic based on operating mode
    # In real implementation, this should check the AGV's pause state from VDA5050
    if hasattr(agv, 'operating_mode'):
        # If AGV is in PAUSED mode, it's paused
        return agv.operating_mode.upper() == 'PAUSED'
    
    # Default to not paused if we can't determine state
    return False
