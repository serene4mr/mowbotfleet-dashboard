# streamlit_cloud_optimization.py
"""
Optimizations for Streamlit Community Cloud deployment
Handles session timeouts, connection drops, and resource limits
"""

import streamlit as st
import time
import threading
import os
from datetime import datetime, timedelta
from mqtt_client import is_connected, connect, disconnect
from broker_config_manager import broker_config_manager
from config import load_config, get_broker_url, get_broker_credentials

def is_streamlit_cloud():
    """Detect if running on Streamlit Community Cloud"""
    return os.environ.get('STREAMLIT_CLOUD', '').lower() == 'true'

class StreamlitCloudOptimizer:
    """Handles Streamlit Community Cloud specific optimizations"""
    
    def __init__(self):
        self.last_connection_check = None
        self.connection_check_interval = 30  # Check every 30 seconds
        self.max_session_duration = 3600  # 1 hour max session
        self.session_start_time = datetime.now()
    
    def check_session_health(self):
        """Check if session is still healthy and within limits"""
        # Only apply cloud optimizations on Streamlit Cloud
        if not is_streamlit_cloud():
            return True
            
        current_time = datetime.now()
        session_duration = (current_time - self.session_start_time).total_seconds()
        
        # Check if session is too old (only on cloud)
        if session_duration > self.max_session_duration:
            st.warning("🔄 Session timeout detected. Please refresh the page to continue.")
            return False
        
        # Check MQTT connection periodically (only on cloud)
        if (self.last_connection_check is None or 
            (current_time - self.last_connection_check).total_seconds() > self.connection_check_interval):
            
            if not is_connected():
                st.warning("🔌 Connection lost. Attempting to reconnect...")
                self._attempt_reconnection()
            
            self.last_connection_check = current_time
        
        return True
    
    def _attempt_reconnection(self):
        """Attempt to reconnect to MQTT broker"""
        try:
            # Try secure config first
            try:
                broker_url = broker_config_manager.get_broker_url()
                username, password = broker_config_manager.get_broker_credentials()
            except:
                # Fallback to YAML config
                cfg = load_config()
                username, password = get_broker_credentials(cfg)
                broker_url = get_broker_url(cfg)
            
            # Attempt reconnection
            import asyncio
            asyncio.run(connect(
                broker_url,
                username,
                password,
                client_id="MowbotFleet_Reconnect"
            ))
            
            if is_connected():
                st.success("✅ Reconnected successfully!")
            else:
                st.error("❌ Reconnection failed. Please check broker settings.")
                
        except Exception as e:
            st.error(f"❌ Reconnection error: {str(e)}")
    
    def optimize_for_cloud(self):
        """Apply optimizations for Streamlit Community Cloud"""
        # Only apply cloud optimizations on Streamlit Cloud
        if not is_streamlit_cloud():
            return True
            
        # Use session state for connection status
        if "connection_status" not in st.session_state:
            st.session_state.connection_status = "disconnected"
        
        # Check session health
        if not self.check_session_health():
            return False
        
        # Optimize memory usage
        self._optimize_memory()
        
        return True
    
    def _optimize_memory(self):
        """Optimize memory usage for cloud deployment"""
        # Clear old session data if needed
        if "old_data" in st.session_state:
            del st.session_state.old_data
        
        # Limit data retention
        if "fleet_data_history" in st.session_state:
            # Keep only last 100 entries
            if len(st.session_state.fleet_data_history) > 100:
                st.session_state.fleet_data_history = st.session_state.fleet_data_history[-100:]

def render_cloud_status():
    """Render cloud-specific status information"""
    # Only show cloud status on Streamlit Cloud
    if not is_streamlit_cloud():
        return
        
    if st.sidebar.button("🔄 Refresh Connection"):
        st.rerun()
    
    # Show session info
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now()
    
    session_duration = datetime.now() - st.session_state.session_start
    st.sidebar.caption(f"Session: {session_duration.seconds // 60}min")
    
    # Show connection status
    if is_connected():
        st.sidebar.success("🟢 Connected")
    else:
        st.sidebar.error("🔴 Disconnected")
        if st.sidebar.button("🔌 Reconnect"):
            st.rerun()

def handle_cloud_limitations():
    """Handle Streamlit Community Cloud limitations"""
    # Skip cloud optimizations for local development
    if not is_streamlit_cloud():
        return True
        
    optimizer = StreamlitCloudOptimizer()
    
    # Apply optimizations
    if not optimizer.optimize_for_cloud():
        return False
    
    # Render cloud status
    render_cloud_status()
    
    return True

# Global optimizer instance
cloud_optimizer = StreamlitCloudOptimizer()
