# ui/components/agv_details.py

import streamlit as st
from datetime import datetime
from mqtt_client import fleet_state

@st.fragment(run_every="1s")
def render_agv_details():
    """
    Render detailed information panel for selected AGV.
    """
    selected_serial = st.session_state.get('selected_agv')
    
    if not selected_serial:
        st.write("No AGV selected. Click an AGV in the table or map to view details.")
        return
    
    agv = fleet_state.get(selected_serial)
    if not agv:
        st.write(f"AGV {selected_serial} not found in fleet state.")
        return

    # AGV Identity Section
    st.subheader(f"AGV Details: {agv.serial}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Identity & Status**")
        st.write(f"Serial Number: `{agv.serial}`")
        st.write(f"Manufacturer: `{agv.manufacturer}`")
        st.write(f"Operating Mode: `{agv.operating_mode}`")
        st.write(f"Connection: `{agv.connection or 'Online'}`")
        st.write(f"Last Update: `{agv.last_update.strftime('%H:%M:%S')}`")
    
    with col2:
        st.markdown("**Position & Navigation**")
        lat, lon = agv.position
        st.write(f"Latitude: `{lat:.6f}`")
        st.write(f"Longitude: `{lon:.6f}`")
        st.write(f"Orientation (θ): `{agv.theta:.2f}` rad")
        st.write(f"Battery Level: `{agv.battery:.1f}%`")
        
        # Battery status indicator
        if agv.battery > 50:
            st.success("🔋 Battery Normal")
        elif agv.battery > 20:
            st.warning("🔋 Battery Low")
        else:
            st.error("🔋 Battery Critical")

    # Mission Progress Section
    st.markdown("**Mission Status**")
    if agv.current_order:
        st.write(f"Current Order: `{agv.current_order}`")
    else:
        st.write("No active mission")

    # Sensor Diagnostics Section
    if agv.sensor_status:
        st.markdown("**Sensor Diagnostics**")
        
        # Group sensors by status for better visualization
        ok_sensors = []
        warn_sensors = []
        error_sensors = []
        
        for sensor_name, status in agv.sensor_status.items():
            status_upper = status.upper()
            if status_upper == "OK":
                ok_sensors.append(sensor_name)
            elif status_upper == "WARN" or status_upper == "WARNING":
                warn_sensors.append(sensor_name)
            elif status_upper == "ERROR":
                error_sensors.append(sensor_name)
            else:
                # Unknown status, treat as warning
                warn_sensors.append(f"{sensor_name} ({status})")
        
        # Display sensors by status
        cols = st.columns(3)
        
        with cols[0]:
            if ok_sensors:
                st.markdown("**🟢 OK**")
                for sensor in ok_sensors:
                    st.write(f"✅ {sensor}")
        
        with cols[1]:
            if warn_sensors:
                st.markdown("**🟡 WARN**")
                for sensor in warn_sensors:
                    st.write(f"⚠️ {sensor}")
        
        with cols[2]:
            if error_sensors:
                st.markdown("**🔴 ERROR**")
                for sensor in error_sensors:
                    st.write(f"❌ {sensor}")
    
    # Errors Section
    if agv.errors:
        st.markdown("**Active Errors**")
        for error in agv.errors:
            severity_color = {
                'WARNING': '🟡',
                'ERROR': '🔴',
                'FATAL': '🚨'
            }.get(error.severity, '🔵')
            
            st.write(f"{severity_color} **{error.type}**: {error.description}")
            st.caption(f"Occurred: {error.timestamp.strftime('%H:%M:%S')}")
    else:
        st.success("✅ No active errors")

    # Factsheet Section (Static for now)
    with st.expander("AGV Specifications"):
        st.write("**Physical Specifications**")
        st.write("- Length: 1.2m")
        st.write("- Width: 0.8m") 
        st.write("- Height: 1.5m")
        st.write("- Max Load: 500kg")
        st.write("- Max Speed: 2.0 m/s")
        st.write("- Navigation: LiDAR + GPS")
