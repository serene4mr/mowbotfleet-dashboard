# ui/dashboard.py

import streamlit as st
from mqtt_client import fleet_state, is_connected

def render_header():
    st.markdown("### Dashboard")
    status = "🟢 Connected" if is_connected() else "🔴 Disconnected"
    st.write(f"**Broker Status:** {status}")

def render_row1():
    st.subheader("Fleet Overview & Map")
    col1, col2 = st.columns(2)
    with col1:
        if fleet_state:
            data = [{
                "Serial": agv.serial,
                "Battery (%)": f"{agv.battery:.1f}",
                "Operating Mode": agv.operating_mode,
                "Last Update": agv.last_update.strftime("%H:%M:%S")
            } for agv in fleet_state.values()]
            st.table(data)
        else:
            st.write("No AGV data available.")
    with col2:
        st.write("Map View (to be implemented)")

def render_row2():
    st.subheader("AGV Details & Quick Controls")
    col1, col2 = st.columns([3,1])
    with col1:
        st.write("AGV Details (placeholder)")
    with col2:
        st.write("Controls: [🛑 E-STOP] [▶️ Resume] [⏸️ Pause] [🔄]")

def render_row3():
    st.subheader("Mission Dispatch")
    st.write("Mission Dispatch Form (placeholder)")
