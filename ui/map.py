# ui/map.py

import streamlit as st
import pydeck as pdk
from mqtt_client import fleet_state

# Set Mapbox access token (you'll need to get one from https://account.mapbox.com/)
# For now, we'll use a placeholder - you'll need to replace this with your actual token
# pdk.settings.mapbox_key = "pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw"

def render_map():
    """
    Render interactive map with AGV markers using PyDeck.
    Updates session state when markers are clicked.
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
            'radius': 10  # Base radius for dynamic scaling (reduced from 50)
        })

    # Configure PyDeck layer with dynamic radius based on zoom level
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="radius",  # Use dynamic radius from data
        radius_scale=1,  # Scale factor
        radius_min_pixels=4,  # Larger when zoomed out (increased from 2)
        radius_max_pixels=8,  # Even smaller when zoomed in (decreased from 12)
        pickable=True,
        auto_highlight=True
    )

    # Set initial view state (center on first AGV or default location)
    if map_data:
        view_state = pdk.ViewState(
            longitude=map_data[0]["lon"],
            latitude=map_data[0]["lat"],
            zoom=15,
            pitch=0
        )
    else:
        view_state = pdk.ViewState(
            longitude=127.0567,  # Default Seoul coordinates
            latitude=37.5075,
            zoom=12,
            pitch=0
        )

    # Create and display map with default style (no token required)
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "AGV: {serial}\nBattery: {battery}%\nMode: {mode}"},
        map_style="light"  # Use built-in light style
    )

    # Display map
    st.pydeck_chart(deck)
    
    # Note: PyDeck selection handling is complex in Streamlit
    # For now, we'll rely on the fleet table for AGV selection
    # TODO: Implement proper map marker selection
