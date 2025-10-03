# ui/map.py

import streamlit as st
import pydeck as pdk
from mqtt_client import fleet_state
import urllib.parse

def create_arrow_icon(color):
    """Create an SVG arrow icon with the specified color"""
    # Convert color array to hex
    if isinstance(color, list) and len(color) >= 3:
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
    else:
        hex_color = "#00ff00"  # Default green
    
    # SVG arrow pointing North (NED convention: 0° = North)
    svg = f"""
    <svg width="30" height="30" viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
        <path d="M15 3 L15 27 M9 9 L15 3 L21 9" 
              stroke="{hex_color}" 
              stroke-width="4" 
              fill="none" 
              stroke-linecap="round" 
              stroke-linejoin="round"/>
        <circle cx="15" cy="15" r="4" fill="{hex_color}"/>
    </svg>
    """
    return urllib.parse.quote(svg)

# Set Mapbox access token (you'll need to get one from https://account.mapbox.com/)
# For now, we'll use a placeholder - you'll need to replace this with your actual token
# pdk.settings.mapbox_key = "pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw"

@st.fragment(run_every="2s")
def render_map():
    """
    Render interactive map with AGV markers using PyDeck.
    Updates session state when markers are clicked.
    Auto-refreshes every 2 seconds to show latest AGV positions.
    """
    if not fleet_state:
        st.write("No AGVs to display on map.")
        return

    # Prepare data for PyDeck
    map_data = []
    for agv in fleet_state.values():
        lat, lon = agv.position
        # Color based on battery level
        if agv.battery < 20:
            color = [255, 0, 0]  # Red for low battery
        elif agv.battery < 50:
            color = [255, 165, 0]  # Orange for medium battery
        else:
            color = [0, 255, 0]  # Green for good battery
            
        map_data.append({
            'serial': agv.serial,
            'lat': lat,
            'lon': lon,
            'battery': agv.battery,
            'mode': agv.operating_mode,
            'theta': agv.theta,
            'color': color,
            'radius': 30,  # Base icon size for better zoom scaling
            'heading': agv.theta * 180 / 3.14159,  # Convert radians to degrees (NED: 0° = North)
            'icon': {
                'url': 'data:image/svg+xml;charset=utf-8,' + create_arrow_icon(color),
                'width': 30,
                'height': 30,
                'anchorX': 15,
                'anchorY': 15
            }
        })

    # Configure PyDeck layer with arrow icons showing orientation
    layer = pdk.Layer(
        "IconLayer",
        data=map_data,
        get_position=["lon", "lat"],
        get_icon="icon",
        get_size="radius",
        get_angle="heading",  # Rotation angle in degrees
        size_scale=1,
        size_min_pixels=12,  # Larger when zoomed out
        size_max_pixels=32,  # Much larger when zoomed in
        pickable=True,
        auto_highlight=True
    )

    # Set view state based on selected AGV or default location
    selected_serial = st.session_state.get('selected_agv')
    
    if selected_serial and selected_serial in fleet_state:
        # Center on selected AGV
        agv = fleet_state[selected_serial]
        lat, lon = agv.position
        view_state = pdk.ViewState(
            longitude=lon,
            latitude=lat,
            zoom=16,  # Closer zoom for selected AGV
            pitch=0
        )
    elif map_data:
        # Center on first AGV if no selection
        view_state = pdk.ViewState(
            longitude=map_data[0]["lon"],
            latitude=map_data[0]["lat"],
            zoom=15,
            pitch=0
        )
    else:
        # Default Seoul coordinates
        view_state = pdk.ViewState(
            longitude=127.0567,
            latitude=37.5075,
            zoom=12,
            pitch=0
        )

    # Create and display map with default style (no token required)
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "AGV: {serial}\nBattery: {battery}%\nMode: {mode}\nHeading: {heading}°"},
        map_style="light"  # Use built-in light style
    )

    # Display map
    st.pydeck_chart(deck)
    
    # Show last update time
    from datetime import datetime
    st.caption(f"Map updated: {datetime.now().strftime('%H:%M:%S')}")    
    # Note: PyDeck selection handling is complex in Streamlit
    # For now, we'll rely on the fleet table for AGV selection
    # TODO: Implement proper map marker selection

