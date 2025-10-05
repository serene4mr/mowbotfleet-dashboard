# utils/map_utils.py

import pydeck as pdk
from config import load_config
import os

def get_map_style():
    """
    Get the appropriate map style based on configuration.
    
    Returns:
        str: Map style string for PyDeck
    """
    cfg = load_config()
    map_config = cfg.get("general", {}).get("map", {})
    map_style = map_config.get("style", "default")
    
    if map_style == "mapbox_satellite":
        # Check if API key is available
        api_key = map_config.get("mapbox_api_key", "")
        if api_key:
            return "mapbox://styles/mapbox/satellite-streets-v11"
        else:
            # Fall back to default if no API key
            return pdk.map_styles.CARTO_LIGHT
    
    # Default style
    return pdk.map_styles.CARTO_LIGHT

def get_map_style_for_pydeck():
    """
    Get map style in the format expected by PyDeck Deck constructor.
    
    Returns:
        str: Map style for PyDeck Deck map_style parameter
    """
    cfg = load_config()
    map_config = cfg.get("general", {}).get("map", {})
    map_style = map_config.get("style", "default")
    
    if map_style == "mapbox_satellite":
        api_key = map_config.get("mapbox_api_key", "")
        if api_key:
            # Return Mapbox satellite style
            return "mapbox://styles/mapbox/satellite-v9"
        else:
            # Fall back to default
            return pdk.map_styles.CARTO_LIGHT
    
    # Default style
    return pdk.map_styles.CARTO_LIGHT

def get_mapbox_api_keys():
    """
    Get API keys dictionary for PyDeck Deck constructor.
    
    Returns:
        dict: API keys dictionary for PyDeck
    """
    cfg = load_config()
    map_config = cfg.get("general", {}).get("map", {})
    map_style = map_config.get("style", "default")
    
    if map_style == "mapbox_satellite":
        api_key = map_config.get("mapbox_api_key", "")
        if api_key:
            return {"mapbox": api_key}
    
    return {}

def get_mapbox_api_key():
    """
    Get Mapbox API key if available.
    
    Returns:
        str: Mapbox API key or empty string
    """
    cfg = load_config()
    return cfg.get("general", {}).get("map", {}).get("mapbox_api_key", "")

def is_satellite_enabled():
    """
    Check if satellite imagery is enabled and properly configured.
    
    Returns:
        bool: True if satellite is enabled and API key is available
    """
    cfg = load_config()
    map_config = cfg.get("general", {}).get("map", {})
    return (map_config.get("style") == "mapbox_satellite" and 
            bool(map_config.get("mapbox_api_key", "")))

def get_default_zoom():
    """
    Get the default zoom level for maps.
    
    Returns:
        int: Default zoom level (1-20)
    """
    cfg = load_config()
    return cfg.get("general", {}).get("map", {}).get("default_zoom", 15)
