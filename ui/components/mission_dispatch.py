# ui/components/mission_dispatch.py

import streamlit as st
from datetime import datetime
from mqtt_client import fleet_state
from utils.mission_utils import (
    parse_nodes_input, validate_nodes, format_nodes_preview, generate_order_id,
    create_vda5050_order, create_mission_summary, validate_order_id, send_mission_order
)
from config import load_config

@st.fragment(run_every="1s")
def get_current_agv_options():
    """Get current AGV options that auto-update with fleet changes"""
    if not fleet_state:
        return [], []
    
    # Create AGV options with simplified display (name only)
    agv_options = []
    agv_display_names = []
    
    for serial, agv in fleet_state.items():
        # Get AGV manufacturer from factsheet or default
        manufacturer = getattr(agv, 'manufacturer', 'Unknown')
        
        # Simple display name with just AGV name and manufacturer
        display_name = f"{serial} ({manufacturer})"
        agv_options.append(serial)
        agv_display_names.append(display_name)
    
    return agv_options, agv_display_names

def render_agv_selection_with_dropdown():
    """Render AGV selection dropdown with immediate selection response"""
    # Get current AGV options (auto-updates every 1s)
    agv_options, agv_display_names = get_current_agv_options()
    
    if not agv_display_names:
        st.warning("⚠️ No AGVs available for mission dispatch.")
        st.info("Connect AGVs to the fleet to enable mission dispatch.")
        return None
    
    # Initialize session state if not exists
    if 'mission_selected_agv_serial' not in st.session_state:
        dashboard_selected = st.session_state.get('selected_agv')
        if dashboard_selected and dashboard_selected in agv_options:
            st.session_state.mission_selected_agv_serial = dashboard_selected
        else:
            st.session_state.mission_selected_agv_serial = agv_options[0] if agv_options else None
    
    # Check if currently selected AGV is still available
    current_selection = st.session_state.mission_selected_agv_serial
    if current_selection and current_selection not in agv_options:
        # Selected AGV is no longer available, pick first available
        st.session_state.mission_selected_agv_serial = agv_options[0] if agv_options else None
        current_selection = st.session_state.mission_selected_agv_serial
    
    # Find index of currently selected AGV
    selected_index = 0
    if current_selection and current_selection in agv_options:
        selected_index = agv_options.index(current_selection)
    
    # Dropdown outside fragment for immediate response
    target_agv = st.selectbox(
        "Select Target AGV:",
        options=agv_display_names,
        index=selected_index,
        key="mission_target_agv_display",
        help="Select the AGV that will execute this mission"
    )
    
    # Update session state with new selection immediately
    target_agv_serial = agv_options[agv_display_names.index(target_agv)]
    st.session_state.mission_selected_agv_serial = target_agv_serial
    
    return target_agv_serial

@st.fragment(run_every="1s")
def render_agv_info(target_agv_serial):
    """Render real-time AGV information metrics"""
    if target_agv_serial and target_agv_serial in fleet_state:
        agv = fleet_state[target_agv_serial]
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Battery", f"{agv.battery:.1f}%")
        with col2:
            st.metric("Mode", agv.operating_mode)
        with col3:
            st.metric("Position", f"({agv.position[0]:.6f}, {agv.position[1]:.6f})")
        with col4:
            error_count = len(getattr(agv, 'errors', []))
            st.metric("Errors", error_count)

def render_mission_dispatch():
    """Render mission dispatch form with enhanced validation and AGV selection"""
    st.markdown("#### 📝 Dispatch New Mission")
    
    # Handle form clearing flag
    if st.session_state.get('mission_form_clear', False):
        st.session_state.mission_nodes_list = []
        st.session_state.mission_order_id = generate_order_id()
        st.session_state.mission_form_clear = False
        st.rerun()
    
    # Load configuration for mission settings
    config = load_config()
    mission_config = config.get("mission", {})
    
    # Target AGV selection with enhanced display (auto-refresh every 1s)
    st.markdown("**🎯 Target AGV Selection**")
    target_agv_serial = render_agv_selection_with_dropdown()
    
    if not target_agv_serial:
        return
    
    # Display selected AGV details (auto-refresh every 1s)
    render_agv_info(target_agv_serial)
    
    st.markdown("---")
    
    # Order ID section
    st.markdown("**📋 Mission Details**")
    
    # Order ID input
    # Initialize session state if not exists
    if 'mission_order_id' not in st.session_state:
        st.session_state.mission_order_id = generate_order_id()
    
    order_id = st.text_input(
        "Order ID:",
        key="mission_order_id",
        help="Unique identifier for this mission. Auto-generated if left as default."
    )
    
    # Nodes input with enhanced validation
    st.markdown("**🗺️ Mission Waypoints**")
    
    # Show format help
    with st.expander("📖 Node Format Help"):
        st.markdown("""
        **Format:** `nodeId,x,y,theta` (one per line)
        
        **Example:**
        ```
        warehouse_pickup,10.5,20.3,0.0
        delivery_zone_A,15.2,25.1,1.57
        charging_station,5.0,5.0,3.14
        ```
        
        **Parameters:**
        - `nodeId`: Unique identifier for the waypoint
        - `x`: X coordinate in meters
        - `y`: Y coordinate in meters  
        - `theta`: Orientation in radians (0 = North, π/2 = East)
        """)
    
    # Load max nodes from config
    max_nodes = mission_config.get("max_nodes_per_mission", 100)
    
    # Initialize nodes list in session state if not exists
    if 'mission_nodes_list' not in st.session_state:
        st.session_state.mission_nodes_list = []
    
    # Two-column layout: Form on left, Map on right
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("**📍 Add New Node**")
        
        with st.form("add_node_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                node_id = st.text_input(
                    "Node ID:",
                    placeholder="e.g., warehouse_pickup",
                    key="new_node_id"
                )
            
            with col2:
                x_coord = st.number_input(
                    "X (Longitude):",
                    value=0.0,
                    step=0.001,
                    format="%.6f",
                    key="new_node_x",
                    help="Longitude in degrees (-180 to 180)"
                )
            
            with col3:
                y_coord = st.number_input(
                    "Y (Latitude):",
                    value=0.0,
                    step=0.001,
                    format="%.6f",
                    key="new_node_y",
                    help="Latitude in degrees (-90 to 90)"
                )
            
            with col4:
                theta = st.number_input(
                    "Heading (rad):",
                    value=0.0,
                    step=0.001,
                    format="%.6f",
                    key="new_node_theta"
                )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                add_node = st.form_submit_button("➕ Add Node", use_container_width=True)
            
            with col2:
                if add_node:
                    if node_id.strip():
                        # Validate the new node
                        try:
                            new_node = {
                                'nodeId': node_id.strip(),
                                'x': float(x_coord),
                                'y': float(y_coord),
                                'theta': float(theta)
                            }
                            
                            # Check if we're under the limit
                            if len(st.session_state.mission_nodes_list) >= max_nodes:
                                st.error(f"❌ Maximum {max_nodes} nodes allowed per mission")
                            else:
                                # Check for duplicate node ID
                                existing_ids = [node['nodeId'] for node in st.session_state.mission_nodes_list]
                                if node_id.strip() in existing_ids:
                                    st.error(f"❌ Node ID '{node_id.strip()}' already exists")
                                else:
                                    st.session_state.mission_nodes_list.append(new_node)
                                    st.success(f"✅ Added node '{node_id.strip()}'")
                        except ValueError as e:
                            st.error(f"❌ Invalid coordinate values: {str(e)}")
                    else:
                        st.error("❌ Node ID is required")
        
        # Display current nodes table
        if st.session_state.mission_nodes_list:
            st.markdown(f"**📋 Current Mission Nodes ({len(st.session_state.mission_nodes_list)}/{max_nodes})**")
            
            # Create table data
            table_data = []
            for i, node in enumerate(st.session_state.mission_nodes_list):
                table_data.append({
                    "Order": i + 1,
                    "Node ID": node['nodeId'],
                    "X": f"{node['x']:.6f}",
                    "Y": f"{node['y']:.6f}",
                    "Heading": f"{node['theta']:.6f}",
                    "Actions": f"Delete"
                })
            
            # Display table headers
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 1])
            with col1:
                st.write("**Order**")
            with col2:
                st.write("**Node ID**")
            with col3:
                st.write("**X (Lon)**")
            with col4:
                st.write("**Y (Lat)**")
            with col5:
                st.write("**Heading**")
            with col6:
                st.write("**Actions**")
            
            # Display table with delete buttons
            for i, row in enumerate(table_data):
                col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{row['Order']}**")
                with col2:
                    st.write(f"**{row['Node ID']}**")
                with col3:
                    st.write(row['X'])
                with col4:
                    st.write(row['Y'])
                with col5:
                    st.write(row['Heading'])
                with col6:
                    if st.button("🗑️", key=f"delete_node_{i}", help="Delete this node"):
                        st.session_state.mission_nodes_list.pop(i)
                        st.rerun()
            
            # Clear all nodes button
            if st.button("🗑️ Clear All Nodes", type="secondary"):
                st.session_state.mission_nodes_list = []
                st.rerun()
            
            # Mission validation
            try:
                validation_errors = validate_nodes(st.session_state.mission_nodes_list)
                
                if validation_errors:
                    st.error("❌ Mission Validation Errors:")
                    for error in validation_errors:
                        st.error(f"• {error}")
                else:
                    st.success(f"✅ Valid mission with {len(st.session_state.mission_nodes_list)} waypoints")
                    
                    # Show VDA5050 Order preview if we have a valid target AGV
                    if target_agv_serial and order_id.strip():
                        try:
                            # Get AGV manufacturer (from factsheet or default)
                            agv = fleet_state[target_agv_serial]
                            manufacturer = getattr(agv, 'manufacturer', 'Unknown')
                            
                            # Validate order ID
                            if not validate_order_id(order_id):
                                st.warning("⚠️ Invalid Order ID format")
                            else:
                                # Create VDA5050 Order
                                vda5050_order = create_vda5050_order(
                                    order_id=order_id,
                                    target_manufacturer=manufacturer,
                                    target_serial=target_agv_serial,
                                    nodes=st.session_state.mission_nodes_list
                                )
                                
                                # Show VDA5050 Order summary
                                summary = create_mission_summary(vda5050_order)
                                
                                st.markdown("**📋 VDA5050 Order Summary:**")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Order ID", summary["order_id"])
                                    st.metric("Target AGV", summary["target_agv"])
                                with col2:
                                    st.metric("Nodes", summary["total_nodes"])
                                    st.metric("Edges", summary["total_edges"])
                                with col3:
                                    st.metric("Released Nodes", summary["released_nodes"])
                                    st.metric("Released Edges", summary["released_edges"])
                                
                                # Show JSON preview
                                with st.expander("🔍 VDA5050 Order JSON Preview"):
                                    import json
                                    order_json = vda5050_order.model_dump_json(indent=2)
                                    st.code(order_json, language="json")
                                    
                        except Exception as e:
                            st.warning(f"⚠️ Cannot create VDA5050 Order preview: {str(e)}")
                            
            except Exception as e:
                st.error(f"❌ Error validating mission: {str(e)}")
        else:
            st.info("💡 Add nodes above to create a mission")
    
    with col_right:
        st.markdown("**🗺️ Mission Map**")
        
        # Create map with waypoints using pydeck (always show map)
        import pydeck as pdk
        import pandas as pd
        import numpy as np
        
        # Default view coordinates (you can change these to your preferred location)
        default_lat, default_lon = 37.5075, 127.0567  # Seoul coordinates as example
        
        # Note: If your coordinates are in meters (local coordinate system), 
        # you may need to adjust the scale or convert them to geographic coordinates
        
        if st.session_state.mission_nodes_list:
            # Prepare data for pydeck
            waypoint_data = []
            arrow_data = []
            
            for i, node in enumerate(st.session_state.mission_nodes_list):
                # Treat X as longitude and Y as latitude directly
                x_coord = float(node['x'])  # This is longitude
                y_coord = float(node['y'])  # This is latitude
                
                # Validate coordinates are within valid ranges
                if -180 <= x_coord <= 180 and -90 <= y_coord <= 90:
                    waypoint_data.append({
                        'lon': x_coord,  # X is longitude
                        'lat': y_coord,  # Y is latitude
                        'node_id': node['nodeId'],
                        'heading': node['theta'],
                        'sequence': i + 1,
                        'color': [0, 0, 255] if i == 0 else [255, 0, 0] if i == len(st.session_state.mission_nodes_list)-1 else [0, 255, 0]
                    })
                
                # Add heading arrow (if heading is not zero and coordinates are valid)
                if node['theta'] != 0 and -180 <= x_coord <= 180 and -90 <= y_coord <= 90:
                    arrow_length = 0.001  # Adjust for map scale
                    end_x = x_coord + arrow_length * np.cos(node['theta'])  # End longitude
                    end_y = y_coord + arrow_length * np.sin(node['theta'])  # End latitude
                    
                    # Only add arrow if both start and end coordinates are valid
                    if -180 <= end_x <= 180 and -90 <= end_y <= 90:
                        arrow_data.append({
                            'start_lon': x_coord,  # Start longitude (X)
                            'start_lat': y_coord,  # Start latitude (Y)
                            'end_lon': end_x,      # End longitude
                            'end_lat': end_y,      # End latitude
                            'color': [255, 165, 0]  # Orange
                        })
            
            # Create waypoints layer
            waypoints_layer = pdk.Layer(
                'ScatterplotLayer',
                data=waypoint_data,
                get_position='[lon, lat]',
                get_color='color',
                get_radius=1,   # Base radius (minimal base size)
                size_scale=0.1, # Scale down to 10% of original size
                size_min_pixels=1,   # Keep small when zoomed in
                size_max_pixels=30,  # Bigger when zoomed out for better visibility
                pickable=True,
                auto_highlight=True
            )
            
            # Create arrows layer
            arrows_layer = pdk.Layer(
                'LineLayer',
                data=arrow_data,
                get_source_position='[start_lon, start_lat]',
                get_target_position='[end_lon, end_lat]',
                get_color='color',
                get_width=5,
                pickable=False
            )
            
            # Create path layer (connecting waypoints)
            path_layer = None
            if len(waypoint_data) > 1:
                path_data = [{
                    'path': [[point['lon'], point['lat']] for point in waypoint_data],
                    'color': [0, 0, 255, 100]  # Blue with transparency
                }]
                
                path_layer = pdk.Layer(
                    'PathLayer',
                    data=path_data,
                    get_path='path',
                    get_color='color',
                    get_width=10,
                    pickable=False
                )
            
            # Calculate view state
            if waypoint_data:
                center_lon = sum(node['lon'] for node in waypoint_data) / len(waypoint_data)
                center_lat = sum(node['lat'] for node in waypoint_data) / len(waypoint_data)
            else:
                center_lon, center_lat = 0, 0
            
            view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=18,
                pitch=0
            )
            
            # Create layers list
            layers = [waypoints_layer, arrows_layer]
            if path_layer:
                layers.append(path_layer)
            
            # Create and display map
            r = pdk.Deck(
                map_style=pdk.map_styles.CARTO_LIGHT,
                initial_view_state=view_state,
                layers=layers,
                tooltip={
                    'html': '<b>Node {sequence}: {node_id}</b><br/>X (Lon): {lon:.6f}<br/>Y (Lat): {lat:.6f}<br/>Heading: {heading:.3f} rad',
                    'style': {
                        'backgroundColor': 'steelblue',
                        'color': 'white'
                    }
                }
            )
            
            st.pydeck_chart(r, height=400)
            
            # Add coordinate system info
            if waypoint_data:
                st.info("📍 **Coordinate System:** X = Longitude, Y = Latitude (in degrees). Coordinates must be within valid ranges: -180 ≤ X ≤ 180, -90 ≤ Y ≤ 90.")
        else:
            # Show empty map when no waypoints
            view_state = pdk.ViewState(
                latitude=default_lat,
                longitude=default_lon,
                zoom=10,
                pitch=0
            )
            
            # Create empty map
            r = pdk.Deck(
                map_style=pdk.map_styles.CARTO_LIGHT,
                initial_view_state=view_state,
                layers=[],
                tooltip={
                    'html': 'No waypoints added yet. Use the form on the left to add waypoints.',
                    'style': {
                        'backgroundColor': 'steelblue',
                        'color': 'white'
                    }
                }
            )
            
            st.pydeck_chart(r, height=400)
            st.info("📍 Use the form on the left to add waypoints and see them on the map")
    
    st.markdown("---")
    
    # Mission dispatch controls
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        send_enabled = (
            len(st.session_state.get('mission_nodes_list', [])) > 0 and 
            target_agv_serial and 
            order_id.strip()
        )
        
        if st.button("🚀 Send Mission", type="primary", disabled=not send_enabled):
            try:
                # Get nodes from session state
                nodes = st.session_state.mission_nodes_list
                validation_errors = validate_nodes(nodes)
                
                if validation_errors:
                    st.error("Cannot send mission with validation errors")
                    return
                
                # Validate order ID
                if not validate_order_id(order_id):
                    st.error("Invalid Order ID format")
                    return
                
                # Get AGV manufacturer
                agv = fleet_state[target_agv_serial]
                manufacturer = getattr(agv, 'manufacturer', 'Unknown')
                
                # Create VDA5050 Order
                vda5050_order = create_vda5050_order(
                    order_id=order_id,
                    target_manufacturer=manufacturer,
                    target_serial=target_agv_serial,
                    nodes=nodes
                )
                
                # Send mission via MQTT
                from mqtt_client import get_client
                mqtt_client = get_client()
                
                if not mqtt_client or not mqtt_client.is_connected():
                    st.error("❌ MQTT client not connected. Cannot send mission.")
                    st.info("Please check broker connection in Settings.")
                    return
                
                # Send the order via MQTT
                import asyncio
                try:
                    # Run the async send function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(send_mission_order(vda5050_order, mqtt_client))
                    loop.close()
                    
                    if success:
                        # Store mission in session state for tracking
                        if 'active_missions' not in st.session_state:
                            st.session_state.active_missions = {}
                        
                        mission_summary = create_mission_summary(vda5050_order)
                        st.session_state.active_missions[order_id] = {
                            'order': vda5050_order,
                            'summary': mission_summary,
                            'status': 'sent',
                            'created_at': datetime.now(),
                            'sent_at': datetime.now()
                        }
                        
                        st.success(f"✅ Mission '{order_id}' sent successfully!")
                        st.info(f"📡 Target: {manufacturer}/{target_agv_serial}")
                        st.info(f"🗺️ Waypoints: {len(nodes)} nodes, {len(nodes)-1} edges")
                        st.info("📋 Mission sent via MQTT and stored for tracking")
                    else:
                        st.error("❌ Failed to send mission via MQTT")
                        
                except Exception as mqtt_error:
                    st.error(f"❌ MQTT Error: {str(mqtt_error)}")
                    st.info("Mission created but not sent. Check MQTT connection.")
                
                # Set flag to clear form on next render
                st.session_state.mission_form_clear = True
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to create mission: {str(e)}")
    
    with col2:
        if st.button("🗑️ Clear Form"):
            # Set flag to clear form on next render
            st.session_state.mission_form_clear = True
            st.rerun()
    
    with col3:
        st.caption("💡 Tip: Use the dashboard to select an AGV, then dispatch missions to it")
