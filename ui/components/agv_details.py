# ui/components/agv_details.py

import streamlit as st
from datetime import datetime
from mqtt_client import fleet_state
from i18n_manager import t

@st.fragment(run_every="1s")
def render_agv_details():
    """
    Render detailed information panel for selected AGV.
    """
    selected_serial = st.session_state.get('selected_agv')
    
    if not selected_serial:
        st.write(t("dashboard.select_agv"))
        return
    
    agv = fleet_state.get(selected_serial)
    if not agv:
        st.write(f"AGV {selected_serial} not found in fleet state.")
        return
    
    # AGV Identity Section
    st.subheader(t("agv.agv_details", serial=agv.serial))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{t('agv.identity_status')}**")
        st.write(f"{t('agv.serial_number')}: `{agv.serial}`")
        st.write(f"{t('agv.manufacturer')}: `{agv.manufacturer}`")
        st.write(f"{t('agv.operating_mode')}: `{agv.operating_mode}`")
        st.write(f"{t('agv.connection')}: `{agv.connection or t('dashboard.online')}`")
        st.write(f"{t('agv.last_update')}: `{agv.last_update.strftime('%H:%M:%S')}`")
    
    with col2:
        st.markdown(f"**{t('agv.position_navigation')}**")
        lat, lon = agv.position
        st.write(f"{t('agv.latitude')}: `{lat:.6f}`")
        st.write(f"{t('agv.longitude')}: `{lon:.6f}`")
        st.write(f"{t('agv.orientation')}: `{agv.theta:.2f}` rad")
        st.write(f"{t('agv.battery_level')}: `{agv.battery:.1f}%`")
        
        # Battery status indicator
        if agv.battery > 50:
            st.success("🔋 Battery Normal")
        elif agv.battery > 20:
            st.warning("🔋 Battery Low")
        else:
            st.error("🔋 Battery Critical")

    # Mission Progress Section - Commented out
    # st.markdown("**Mission Status**")
    # if agv.current_order:
    #     st.write(f"Current Order: `{agv.current_order}`")
    # else:
    #     st.write("No active mission")

    # Sensor Diagnostics Section
    if agv.sensor_status:
        st.markdown(f"**{t('agv.sensor_diagnostics')}**")
        
        # Build horizontal display string
        sensor_displays = []
        for sensor_name, status in agv.sensor_status.items():
            status_upper = status.upper()
            
            # Choose icon based on status
            if status_upper == "OK":
                icon = "✅"
            elif status_upper in ("WARN", "WARNING"):
                icon = "⚠️"
            elif status_upper == "ERROR":
                icon = "❌"
            else:
                icon = "ℹ️"
            
            sensor_displays.append(f"{icon} {sensor_name}: {status}")
        
        # Display all sensors on one line with separator
        st.write(" | ".join(sensor_displays))
    
    # Errors Section
    if agv.errors:
        st.markdown(f"**{t('agv.active_errors')}**")
        for error in agv.errors:
            severity_color = {
                'WARNING': '🟡',
                'ERROR': '🔴',
                'FATAL': '🚨'
            }.get(error.severity, '🔵')
            
            st.write(f"{severity_color} **{error.type}**: {error.description}")
            st.caption(f"{t('agv.occurred')}: {error.timestamp.strftime('%H:%M:%S')}")
    else:
        st.success(f"✅ {t('common.no')} {t('agv.active_errors').lower()}")

    # Factsheet Section (Static for now) - Commented out
    # with st.expander("AGV Specifications"):
    #     st.write("**Physical Specifications**")
    #     st.write("- Length: 1.2m")
    #     st.write("- Width: 0.8m") 
    #     st.write("- Height: 1.5m")
    #     st.write("- Max Load: 500kg")
    #     st.write("- Max Speed: 2.0 m/s")
    #     st.write("- Navigation: LiDAR + GPS")
