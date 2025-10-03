# ui/dashboard.py

import streamlit as st
import time
from mqtt_client import fleet_state, is_connected, get_debug_info
from .map import render_map
from .agv_details import render_agv_details
from .controls import render_quick_controls

def render_agv_selection():
    """Render AGV selection dropdown (stable, updates with Refresh Dashboard button)"""
    if fleet_state:
        # Sort by connection timestamp (first connected first)
        sorted_agvs = sorted(fleet_state.values(), key=lambda x: x.connect_timestamp)
        
        # Create AGV selection dropdown
        agv_options = [agv.serial for agv in sorted_agvs]
        agv_serials = [agv.serial for agv in sorted_agvs]
        
        # Initialize session state
        if 'selected_agv' not in st.session_state:
            st.session_state['selected_agv'] = agv_serials[0] if agv_serials else None
        
        # Auto-fallback logic: only if selected AGV is truly disconnected (serial not in list)
        current_selection = st.session_state.get('selected_agv')
        current_agv_serials = [agv.serial for agv in sorted_agvs]
        if current_selection and current_selection not in current_agv_serials and agv_serials:
            st.session_state['selected_agv'] = agv_serials[0]
            current_selection = agv_serials[0]
        
        # Get current selection index
        default_idx = 0
        if current_selection and current_selection in agv_serials:
            default_idx = agv_serials.index(current_selection)
        
        # Create selectbox with one-click selection
        selected_agv_display = st.selectbox(
            "Select AGV:",
            options=agv_options,
            index=default_idx,
            key="agv_selector_key"
        )
        
        # Update session state directly (one-click selection)
        if selected_agv_display and selected_agv_display in agv_options:
            selected_serial = agv_serials[agv_options.index(selected_agv_display)]
            st.session_state['selected_agv'] = selected_serial

@st.fragment(run_every="1s")
def render_fleet_table_fragment():
    """Render fleet table with real-time updates (fragment)"""
    if fleet_state:
        # Sort by connection timestamp (first connected first)
        sorted_agvs = sorted(fleet_state.values(), key=lambda x: x.connect_timestamp)
        
        # Display fleet table (read-only)
        data = [{
            "Serial": agv.serial,
            "Battery (%)": f"{agv.battery:.1f}",
            "Operating Mode": agv.operating_mode,
            "Alerts": len(agv.errors),
            "Last Update": agv.last_update.strftime("%H:%M:%S")
        } for agv in sorted_agvs]
        
        st.dataframe(
            data,
            width='stretch',
            hide_index=True
        )
        
        # Show total count and update time
        from datetime import datetime
        st.caption(f"Total AGVs: {len(fleet_state)} | Updated: {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.write("No AGV data available.")
        st.caption("Waiting for AGV state messages...")

def render_header():
    st.markdown("### Dashboard")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "🟢 Connected" if is_connected() else "🔴 Disconnected"
        st.write(f"**Broker:** {status}")
    
    with col2:
        online_count = len(fleet_state)
        st.write(f"**Fleet:** {online_count} Online")
    
    with col3:
        error_count = sum(len(agv.errors) for agv in fleet_state.values())
        st.write(f"**Alerts:** {error_count}")
    
    # Manual refresh button
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

def render_row1():
    """Fleet Overview & Map"""
    st.subheader("Fleet Overview & Map")
    col1, col2 = st.columns(2)
    
    with col1:
        # AGV selection (stable, updates with Refresh Dashboard button)
        render_agv_selection()
        
        # Fleet table (auto-updates)
        render_fleet_table_fragment()
    
    with col2:
        render_map()

def render_row2():
    """AGV Details & Quick Controls"""
    st.subheader("AGV Details & Quick Controls")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        render_agv_details()
    
    with col2:
        render_quick_controls()

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
