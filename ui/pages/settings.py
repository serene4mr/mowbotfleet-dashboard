# ui/pages/settings.py

import streamlit as st
import asyncio
from config import load_config, save_config, get_broker_url
from mqtt_client import connect, disconnect
from auth import add_or_update_user, list_users, delete_user, get_user_count, ensure_default_admin, verify_user
from broker_config_manager import broker_config_manager
from streamlit.runtime.scriptrunner import RerunException, RerunData

def render_settings():
    st.header("Settings")

    # Load config
    cfg = load_config()
    
    # General Configuration (displayed first)
    st.subheader("General Configuration")
    st.caption("Fleet client identification settings")
    
    # General settings
    manufacturer = st.text_input("Manufacturer", value=cfg["general"]["manufacturer"])
    serial_number = st.text_input("Serial Number", value=cfg["general"]["serial_number"])
    
    if st.button("💾 Save General Settings"):
        # Update general settings
        new_cfg = cfg.copy()
        new_cfg["general"]["manufacturer"] = manufacturer
        new_cfg["general"]["serial_number"] = serial_number
        
        # Save only the general settings
        general_config = {
            "general": new_cfg["general"]
        }
        save_config(general_config)
        
        # Check what was changed to show appropriate message
        mqtt_related_changed = (
            manufacturer != cfg["general"]["manufacturer"] or 
            serial_number != cfg["general"]["serial_number"]
        )
        
        st.success("General settings saved.")
        
        if mqtt_related_changed:
            st.info("⚠️ Manufacturer/Serial Number changes will take effect after MQTT reconnection.")

    st.markdown("---")
    
    # Map Configuration
    st.subheader("Map Configuration")
    st.caption("Configure map display settings for all maps in the application")
    
    map_style = st.selectbox(
        "Map Style",
        options=["default", "mapbox_satellite"],
        index=0 if cfg["general"].get("map", {}).get("style", "default") == "default" else 1,
        help="Choose between default map or Mapbox satellite imagery",
        key="map_style_select"
    )
    
    default_zoom = st.slider(
        "Default Zoom Level",
        min_value=1,
        max_value=20,
        value=cfg["general"].get("map", {}).get("default_zoom", 15),
        help="Default zoom level for all maps (1=world view, 20=building level)",
        key="default_zoom_slider"
    )
    
    # Add zoom level reference
    st.caption("📏 **Zoom Reference:** 1=World • 5=Country • 10=City • 15=Street • 20=Building (Max)")
    
    # Heading offset for orientation display
    heading_offset = st.number_input(
        "Heading Offset (degrees)",
        min_value=-180,
        max_value=180,
        value=cfg["general"].get("map", {}).get("heading_offset_degrees", -30),
        step=1,
        help="Empirical correction for AGV arrow orientation on map (adjust if arrows don't point correctly)",
        key="heading_offset_input"
    )
    st.caption("🧭 **Tip:** Adjust this if AGV arrows don't point in the correct direction on the map")
    
    # Show Mapbox API key field only if satellite is selected
    mapbox_api_key = ""
    if map_style == "mapbox_satellite":
        mapbox_api_key = st.text_input(
            "Mapbox API Key", 
            value=cfg["general"].get("map", {}).get("mapbox_api_key", ""),
            type="password",
            help="Required: Enter your Mapbox API key to use satellite imagery",
            key="mapbox_api_key"
        )
        
        if not mapbox_api_key:
            st.warning("⚠️ Mapbox API key is required for satellite imagery")
    else:
        # Use existing API key if available, but don't require it
        mapbox_api_key = cfg["general"].get("map", {}).get("mapbox_api_key", "")
    
    if st.button("🗺️ Save Map Settings"):
        # Validate Mapbox configuration
        if map_style == "mapbox_satellite" and not mapbox_api_key:
            st.error("❌ Mapbox API key is required for satellite imagery")
            return
        
        # Update map configuration
        new_cfg = cfg.copy()
        if "map" not in new_cfg["general"]:
            new_cfg["general"]["map"] = {}
        new_cfg["general"]["map"]["style"] = map_style
        new_cfg["general"]["map"]["mapbox_api_key"] = mapbox_api_key
        new_cfg["general"]["map"]["default_zoom"] = default_zoom
        new_cfg["general"]["map"]["heading_offset_degrees"] = heading_offset
        
        # Save only the map settings
        map_config = {
            "general": {
                "map": new_cfg["general"]["map"]
            }
        }
        save_config(map_config)
        
        st.success("✅ Map settings saved! Changes will apply on next page refresh.")
        st.info("🗺️ Maps will use the new configuration immediately.")

    st.markdown("---")
    
    # Broker Configuration (Secure)
    st.subheader("Broker Configuration")
    st.info("🔒 Broker credentials are stored securely in encrypted database")
    
    # Load secure broker config
    broker_config = broker_config_manager.get_broker_config()
    
    host = st.text_input("Broker Host", value=broker_config["host"])
    port = st.number_input("Broker Port", value=broker_config["port"])
    use_tls = st.checkbox("Use TLS", value=broker_config["use_tls"])
    buser = st.text_input("Broker Username", value=broker_config["user"])
    bpass = st.text_input("Broker Password", type="password", value=broker_config["password"])

    col1, col2 = st.columns([3, 1])
    
    with col1:
        save_button = st.button("💾 Save & Reconnect", use_container_width=True)
    
    with col2:
        delete_button = st.button("🗑️ Delete Config", use_container_width=True, type="secondary")
    
    if save_button:
        # Update broker configuration securely
        new_broker_config = {
            "host": host,
            "port": port,
            "use_tls": use_tls,
            "user": buser,
            "password": bpass
        }
        
        # Save securely to encrypted database
        print(f"🔒 Saving broker config securely: {host}:{port} (TLS: {use_tls})")
        if broker_config_manager.save_broker_config(new_broker_config):
            st.success("✅ Broker configuration saved securely!")
        else:
            st.error("❌ Failed to save broker configuration")
            return

        # Reconnect MQTT synchronously
        try:
            asyncio.run(disconnect())
            broker_url = broker_config_manager.get_broker_url()
            username, password = broker_config_manager.get_broker_credentials()
            asyncio.run(connect(broker_url, username, password, client_id="MowbotFleet"))
            st.success("🔄 Reconnected to broker successfully!")
        except Exception as e:
            st.error(f"Reconnection failed: {e}")
            # Continue anyway to save the config

        # Rerun to update header
        raise RerunException(RerunData())
    
    if delete_button:
        # Delete broker configuration
        if broker_config_manager.delete_broker_config():
            st.success("🗑️ Broker configuration deleted!")
            st.info("ℹ️ Will fallback to YAML configuration on next restart")
        else:
            st.error("❌ Failed to delete broker configuration")
        
        # Rerun to update form
        raise RerunException(RerunData())

    # Debug Section (for development)
    with st.expander("🔧 Debug Information"):
        st.caption("Development tools for broker configuration management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Show Config Status"):
                metadata = broker_config_manager.get_config_metadata()
                if metadata.get("exists"):
                    st.success(f"✅ Config exists")
                    st.write(f"Created: {metadata.get('created_at')}")
                    st.write(f"Updated: {metadata.get('updated_at')}")
                else:
                    st.warning("⚠️ No secure config found")
        
        with col2:
            if st.button("📊 List All Configs"):
                configs = broker_config_manager.list_all_configs()
                if configs:
                    for key, info in configs.items():
                        st.write(f"**{key}**: {info['updated_at']}")
                else:
                    st.info("No configurations found")
        
        with col3:
            if st.button("🔄 Reset to Defaults"):
                if broker_config_manager.delete_broker_config():
                    st.success("✅ Reset to defaults")
                else:
                    st.error("❌ Failed to reset")

    st.markdown("---")
    
    # User Management Section
    st.subheader("User Management")
    st.caption("Manage system users with full CRUD operations")
    
    # Ensure default admin user exists
    ensure_default_admin()
    
    # Display current users table
    st.markdown("### 👥 Current Users")
    
    users = list_users()
    user_count = get_user_count()
    
    if user_count > 0:
        # Create user table with actions
        for i, (username, created_at, updated_at) in enumerate(users):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
            
            with col1:
                st.write(f"**{username}**")
                if username == "admin":
                    st.caption("🔑 Default admin user")
            
            with col2:
                st.write(f"Created: {created_at}")
            
            with col3:
                st.write(f"Updated: {updated_at}")
            
            with col4:
                # Edit user button
                if st.button("✏️", key=f"edit_{username}", help="Edit user"):
                    st.session_state[f"editing_{username}"] = True
            
            with col5:
                # Delete user button (disabled for admin)
                if username == "admin":
                    st.button("🔒", key=f"delete_{username}", disabled=True, help="Cannot delete admin user")
                else:
                    if st.button("🗑️", key=f"delete_{username}", help="Delete user"):
                        st.session_state["user_to_delete"] = username
            
            # Edit user form (shown when edit button is clicked)
            if st.session_state.get(f"editing_{username}", False):
                st.markdown(f"#### ✏️ Editing User: {username}")
                
                # Password change form with current password verification
                col1, col2 = st.columns(2)
                with col1:
                    current_password = st.text_input(
                        f"Current Password",
                        type="password",
                        key=f"current_pass_{username}",
                        placeholder="Enter current password"
                    )
                
                with col2:
                    new_password = st.text_input(
                        f"New Password",
                        type="password",
                        key=f"new_pass_{username}",
                        placeholder="Enter new password"
                    )
                
                # Action buttons
                col3, col4 = st.columns(2)
                with col3:
                    if st.button("💾 Save Changes", key=f"save_{username}"):
                        # Validate inputs
                        if not current_password:
                            st.error("Current password is required")
                        elif not new_password:
                            st.error("New password is required")
                        else:
                            # Verify current password
                            if verify_user(username, current_password):
                                # Current password is correct, update to new password
                                if add_or_update_user(username, new_password):
                                    st.success(f"✅ Password updated successfully for {username}")
                                    st.session_state[f"editing_{username}"] = False
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to update password for {username}")
                            else:
                                st.error("❌ Current password is incorrect. Cannot update password.")
                
                with col4:
                    if st.button("❌ Cancel", key=f"cancel_{username}"):
                        st.session_state[f"editing_{username}"] = False
                        st.rerun()
                
                # Help text
                st.info("🔒 **Security:** You must enter the current password correctly to change it to a new password.")
            
            # Delete confirmation (shown when delete button is clicked)
            if st.session_state.get("user_to_delete") == username:
                st.error(f"⚠️ Are you sure you want to delete user '{username}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", key=f"confirm_delete_{username}"):
                        if delete_user(username):
                            st.success(f"User '{username}' deleted successfully")
                            st.session_state["user_to_delete"] = None
                            st.rerun()
                        else:
                            st.error(f"Failed to delete user '{username}'")
                
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_delete_{username}"):
                        st.session_state["user_to_delete"] = None
                        st.rerun()
        
        st.markdown("---")
    
    # Add new user section
    st.markdown("### ➕ Add New User")
    
    col1, col2 = st.columns(2)
    with col1:
        new_user = st.text_input("Username", key="new_user", placeholder="Enter username")
    
    with col2:
        new_pass = st.text_input("Password", type="password", key="new_pass", placeholder="Enter password")
    
    if st.button("➕ Add User", type="primary"):
        if not new_user or not new_pass:
            st.error("Username and password cannot be empty.")
        elif new_user.strip() == "":
            st.error("Username cannot be empty or just spaces.")
        else:
            if add_or_update_user(new_user.strip(), new_pass):
                st.success(f"User '{new_user}' added successfully!")
                st.rerun()
            else:
                st.error(f"Failed to add user '{new_user}'. User may already exist.")
    
    # User management info
    st.info(f"📊 **Total Users:** {user_count} | 🔑 **Admin User:** Always available | 🛡️ **Admin Protection:** Cannot be deleted")
