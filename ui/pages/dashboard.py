# ui/pages/dashboard.py

import streamlit as st
import time
from datetime import datetime
from mqtt_client import fleet_state, is_connected, get_debug_info
from ..components.map import render_map
from ..components.agv_details import render_agv_details
from ..components.controls import render_quick_controls


@st.fragment(run_every="1s")
def render_fleet_table():
    """Render fleet table with AGV selection checkboxes (auto-refresh every 1s)"""
    # Get current fleet state (handle empty state gracefully)
    current_fleet_state = fleet_state or {}
    
    # Sort by connection timestamp (first connected first)
    sorted_agvs = sorted(current_fleet_state.values(), key=lambda x: x.connect_timestamp)
    
    # Always show the header
    st.markdown("**Select AGV:**")
    
    if sorted_agvs:
        # Show table header (compact)
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        with col1:
            st.markdown("**Serial (Manufacturer)**")
        with col2:
            st.markdown("**Battery**")
        with col3:
            st.markdown("**Mode**")
        with col4:
            st.markdown("**Alerts**")
        with col5:
            st.markdown("**Last Update**")
        # Initialize selected AGV if not set
        if 'selected_agv' not in st.session_state:
            st.session_state['selected_agv'] = sorted_agvs[0].serial
        
        # Check if currently selected AGV is still available
        current_selection = st.session_state.get('selected_agv')
        available_serials = [agv.serial for agv in sorted_agvs]
        
        # Auto-fallback if selected AGV is no longer available
        if current_selection and current_selection not in available_serials and available_serials:
            st.session_state['selected_agv'] = available_serials[0]
            current_selection = available_serials[0]
        
        selected_agv = None
        
        for i, agv in enumerate(sorted_agvs):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                # Get AGV manufacturer from factsheet or default
                manufacturer = getattr(agv, 'manufacturer', 'Unknown')
                agv_display_name = f"{agv.serial} ({manufacturer})"
                
                # Radio button with AGV serial and manufacturer as the option
                is_selected = st.radio(
                    f"Select {agv_display_name}",
                    options=[agv.serial],
                    index=0 if agv.serial == current_selection else None,
                    key=f"agv_radio_{agv.serial}",
                    label_visibility="collapsed"
                )
                if is_selected and is_selected != current_selection:
                    st.session_state['selected_agv'] = is_selected
                    selected_agv = is_selected
            
            with col2:
                st.write(f"{agv.battery:.1f}%")
            
            with col3:
                st.write(agv.operating_mode)
            
            with col4:
                alert_count = len(agv.errors)
                if alert_count > 0:
                    st.write(f"🔴 {alert_count}")
                else:
                    st.write("✅ 0")
            
            with col5:
                st.write(agv.last_update.strftime("%H:%M:%S"))
        
        # Update session state if selection changed
        if selected_agv:
            st.session_state['selected_agv'] = selected_agv
        
        # Show total count and update time
        st.caption(f"Total AGVs: {len(current_fleet_state)} | Updated: {datetime.now().strftime('%H:%M:%S')}")
        
        # Show tips for AGV selection
        with st.expander("💡 Tips for AGV Selection", expanded=False):
            st.markdown("""
            **AGV Selection:**
            - Click the radio button next to an AGV to select it
            - Selected AGV will be highlighted on the map
            - Selection is remembered even when the table refreshes
            - If selected AGV disconnects, it auto-selects the first available AGV
            """)
    else:
        # Show placeholder when no AGVs are connected
        st.write("No AGVs connected")
        st.caption("Waiting for AGV connections...")
        
        # Show tips for AGV selection even when no AGVs
        with st.expander("💡 Tips for AGV Selection", expanded=False):
            st.markdown("""
            **AGV Selection:**
            - AGVs will appear here when they connect to the broker
            - Click the radio button next to an AGV to select it
            - Selected AGV will be highlighted on the map
            - Selection is remembered even when the table refreshes
            """)

def render_header():
    st.markdown("### Dashboard")
    
    # Auto-updating status section (fragment)
    render_header_status()

@st.fragment(run_every="1s")
def render_header_status():
    """Render header status that auto-updates every second"""
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

def render_row1():
    """Fleet Overview & Map"""
    st.subheader("Fleet Overview & Map")
    col1, col2 = st.columns(2)
    
    with col1:
        # Fleet table with AGV selection (auto-refresh every 1s)
        render_fleet_table()
    
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
