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
    
    # E-STOP button
    if st.button("🛑 E-STOP", type="primary", use_container_width=True):
        success = send_estop_command(selected_serial)
        if success:
            st.success(f"✅ E-STOP sent to {selected_serial}")
        else:
            st.error(f"❌ Failed to send E-STOP to {selected_serial}")

def send_estop_command(serial: str):
    """
    Send emergency stop command to AGV using VDA5050 instant action.
    
    This sends an "emergencyStop" instant action with HARD blocking type,
    which immediately stops the AGV and cancels the current mission.
    """
    print(f"🛑 Attempting to send E-STOP to {serial}")
    success = send_instant_action(
        serial=serial,
        action_type="emergencyStop",
        blocking_type="HARD"
    )
    print(f"🛑 E-STOP result for {serial}: {success}")
    return success

