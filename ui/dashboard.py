# ui/dashboard.py

import streamlit as st
import time
from mqtt_client import fleet_state, is_connected, get_debug_info
from .map import render_map
from .agv_details import render_agv_details
from .controls import render_quick_controls

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
        # Fleet table with selection
        if fleet_state:
            # Sort by last update time (most recent first)
            sorted_agvs = sorted(fleet_state.values(), key=lambda x: x.last_update, reverse=True)
            
            # Create AGV selection dropdown
            agv_options = [f"{agv.serial} (Battery: {agv.battery:.1f}%)" for agv in sorted_agvs]
            agv_serials = [agv.serial for agv in sorted_agvs]
            
            def update_agv_selection():
                """Callback function to handle AGV selection changes"""
                selected_display = st.session_state.agv_selector_key
                if selected_display:
                    selected_serial = agv_serials[agv_options.index(selected_display)]
                    st.session_state['selected_agv'] = selected_serial
            
            # Initialize session state
            if 'selected_agv' not in st.session_state:
                st.session_state['selected_agv'] = agv_serials[0] if agv_serials else None
            
            # Get current selection index
            current_selection = st.session_state.get('selected_agv')
            default_idx = 0
            if current_selection and current_selection in agv_serials:
                default_idx = agv_serials.index(current_selection)
            
            # Create selectbox with callback
            selected_agv_display = st.selectbox(
                "Select AGV:",
                options=agv_options,
                index=default_idx,
                key="agv_selector_key",
                on_change=update_agv_selection
            )
            
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
            
            # Show total count
            st.caption(f"Total AGVs: {len(fleet_state)}")
        else:
            st.write("No AGV data available.")
            st.caption("Waiting for AGV state messages...")
    
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
