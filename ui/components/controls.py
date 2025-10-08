# ui/components/controls.py

import streamlit as st
from mqtt_client import fleet_state, send_instant_action

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
    """
    Send emergency stop command to AGV using VDA5050 instant action.
    
    This sends an "emergencyStop" instant action with HARD blocking type,
    which immediately stops the AGV and cancels the current mission.
    """
    success = send_instant_action(
        serial=serial,
        action_type="emergencyStop",
        blocking_type="HARD"
    )
    return success

def send_resume_command(serial: str):
    """
    Send resume command to AGV.
    
    Note: This is a placeholder. VDA5050 doesn't have a standard "resume" instant action.
    In practice, you would either:
    1. Send a new order to continue the mission
    2. Use a custom action if your AGV supports it
    """
    # TODO: Implement proper resume logic (might need to resend order)
    print(f"⚠️ Resume command not yet implemented for {serial}")
    print(f"   VDA5050 doesn't have a standard 'resume' instant action")
    return False

def send_pause_command(serial: str):
    """
    Send pause command to AGV.
    
    Note: This is a placeholder. VDA5050 doesn't have a standard "pause" instant action.
    In practice, you would either:
    1. Send an order update to pause the mission
    2. Use a custom action if your AGV supports it
    """
    # TODO: Implement proper pause logic (might need order update)
    print(f"⚠️ Pause command not yet implemented for {serial}")
    print(f"   VDA5050 doesn't have a standard 'pause' instant action")
    return False

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
