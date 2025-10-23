# ui/components/controls.py

import streamlit as st
from mqtt_client import fleet_state, send_instant_action
from i18n_manager import t

@st.fragment(run_every="1s")
def render_quick_controls():
    """
    Render quick control buttons for selected AGV.
    """
    selected_serial = st.session_state.get('selected_agv')
    
    if not selected_serial:
        st.write(t("agv.select_agv"))
        return
    
    agv = fleet_state.get(selected_serial)
    if not agv:
        st.write(t("agv.agv_not_available"))
        return

    st.markdown(f"**{selected_serial} {t('agv.controls')}**")
    
    # E-STOP button
    if st.button(t("agv.estop"), type="primary", use_container_width=True):
        success = send_estop_command(selected_serial)
        if success:
            st.success(t("agv.estop_success", serial=selected_serial))
        else:
            st.error(t("agv.estop_error", serial=selected_serial))

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

