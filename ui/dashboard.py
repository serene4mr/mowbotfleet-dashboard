# ui/dashboard.py

import streamlit as st
import time
from mqtt_client import fleet_state, is_connected, get_debug_info

def render_header():
    st.markdown("### Dashboard")
    status = "🟢 Connected" if is_connected() else "🔴 Disconnected"
    st.write(f"**Broker Status:** {status}")
    
    # Manual refresh button
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

def render_row1():
    st.subheader("Fleet Overview & Map")
    col1, col2 = st.columns(2)
    with col1:
        if fleet_state:
            # Sort by last update time (most recent first)
            sorted_agvs = sorted(fleet_state.values(), key=lambda x: x.last_update, reverse=True)
            data = [{
                "Serial": agv.serial,
                "Battery (%)": f"{agv.battery:.1f}",
                "Operating Mode": agv.operating_mode,
                "Last Update": agv.last_update.strftime("%H:%M:%S")
            } for agv in sorted_agvs]
            st.table(data)
            
            # Show total count
            st.caption(f"Total AGVs: {len(fleet_state)}")
        else:
            st.write("No AGV data available.")
            st.caption("Waiting for AGV state messages...")
    with col2:
        st.write("Map View (to be implemented)")
        if fleet_state:
            # Show position data for debugging
            st.write("**AGV Positions:**")
            for agv in fleet_state.values():
                st.write(f"• {agv.serial}: ({agv.position[0]:.2f}, {agv.position[1]:.2f}) θ={agv.theta:.2f}")

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

def render_debug():
    """Debug section to show MQTT connection and message details"""
    with st.expander("🔧 Debug Information", expanded=False):
        debug_info = get_debug_info()
        
        st.write("**Connection Status:**")
        st.write(f"- Connected: {debug_info['connected']}")
        st.write(f"- Client Exists: {debug_info['client_exists']}")
        st.write(f"- Connection Task Alive: {debug_info['connection_task_alive']}")
        st.write(f"- Fleet State Count: {debug_info['fleet_state_count']}")
        st.write(f"- Fleet State Keys: {debug_info['fleet_state_keys']}")
        
        st.write("**Expected MQTT Topics:**")
        st.write("- State: `uagv/v2/+/+/state`")
        st.write("- Connection: `uagv/v2/+/+/connection`")
        st.write("- Factsheet: `uagv/v2/+/+/factsheet`")
        
        if fleet_state:
            st.write("**Latest AGV Data:**")
            for serial, agv in fleet_state.items():
                st.write(f"**{serial}:**")
                st.write(f"- Battery: {agv.battery}%")
                st.write(f"- Mode: {agv.operating_mode}")
                st.write(f"- Position: ({agv.position[0]:.2f}, {agv.position[1]:.2f})")
                st.write(f"- Last Update: {agv.last_update}")
                if agv.errors:
                    st.write(f"- Errors: {len(agv.errors)}")
                st.write("---")
        else:
            st.write("No AGV data received yet.")
            st.caption("Make sure AGVs are publishing state messages to the MQTT broker.")
            st.caption("Check the console output for connection and subscription details.")
