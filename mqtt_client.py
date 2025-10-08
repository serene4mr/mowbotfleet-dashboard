# mqtt_client.py

import asyncio
import threading
from datetime import datetime, timezone
from typing import Dict
from vda5050.clients.master_control import MasterControlClient
from vda5050.models.state import State
from vda5050.models.instant_action import InstantActions
from vda5050.models.base import Action, BlockingType
from models import AGVInfo, ErrorInfo
from config import load_config
import uuid

# Shared application state
fleet_state: Dict[str, AGVInfo] = {}
_client = None
_connection_task = None
_connection_lock = threading.Lock()

def _update_agv(serial: str, state: State):
    """Update fleet_state with AGV information from VDA5050 State"""
    info = fleet_state.get(serial)
    if not info:
        info = AGVInfo(
            serial=serial,
            manufacturer=state.manufacturer,
            connection="",
            battery=0.0,
            operating_mode="",
            position=(0.0, 0.0),
            theta=0.0,
            last_update=datetime.now(timezone.utc)
        )
        fleet_state[serial] = info

    # Update AGV information from state
    info.battery = state.batteryState.batteryCharge
    info.operating_mode = state.operatingMode.value
    
    # Handle position data (may be None in some state messages)
    if state.agvPosition:
        info.position = (state.agvPosition.x, state.agvPosition.y)  # (x, y) = (longitude, latitude)
        info.theta = state.agvPosition.theta or 0.0
    else:
        # Keep existing position if no new position data
        pass
    
    info.last_update = datetime.now(timezone.utc)
    info.current_order = state.orderId
    info.errors = [
        ErrorInfo(datetime.now(timezone.utc), e.errorType, e.errorDescription, e.errorLevel.value)
        for e in (getattr(state, 'errors', []) or [])
    ]

def on_state_update(serial: str, state: State):
    """Callback for VDA5050 state updates"""
    _update_agv(serial, state)

def on_connected():
    """Handle connection established"""
    pass

def on_disconnected():
    """Handle connection lost"""
    with _connection_lock:
        fleet_state.clear()

def is_connected() -> bool:
    """Thread-safe way to check connection status"""
    # For now, just return True if we have a client and connection task is alive
    if _client and _connection_task and _connection_task.is_alive():
        return True
    return False

def _connect_in_thread(broker_url: str, username: str, password: str, client_id: str):
    """
    Connect to MQTT broker in a separate thread to avoid event loop conflicts.
    """
    global _client
    
    def run_connection():
        global _client
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Parse broker URL to extract host and port
            if '://' in broker_url:
                # Remove protocol prefix (mqtt://, mqtts://, etc.)
                broker_url_clean = broker_url.split('://', 1)[1]
            else:
                broker_url_clean = broker_url
            
            if ':' in broker_url_clean:
                broker_host, broker_port = broker_url_clean.split(':', 1)
                try:
                    broker_port = int(broker_port)
                except ValueError:
                    # Invalid port number
                    return
            else:
                # Invalid broker URL format
                return
            
            # Load config for general client settings
            config = load_config()
            general_config = config.get("general", {})
            
            # Initialize MasterControlClient with required parameters
            _client = MasterControlClient(
                broker_url=broker_host,
                manufacturer=general_config.get("manufacturer", "MowbotAI"),
                serial_number=general_config.get("serial_number", "MowbotFleetClient"),
                broker_port=broker_port,
                username=username if username else None,
                password=password if password else None,
                validate_messages=True  # Enable validation now that schema files are included
            )
            
            # Register callbacks using the correct API
            _client.on_state_update(on_state_update)
            _client.on_connection_change(lambda serial, state: on_connected() if state == "ONLINE" else on_disconnected())
            
            
            # Connect to broker
            success = loop.run_until_complete(_client.connect())
            
            if success:
                on_connected()  # Use thread-safe function
                # Keep the event loop running
                try:
                    loop.run_forever()
                except KeyboardInterrupt:
                    pass  # Connection thread interrupted
                finally:
                    loop.close()
            else:
                loop.close()
                
        except Exception as e:
            # Connection error - will be handled by the caller
            loop.close()
    
    # Start connection in a separate thread
    thread = threading.Thread(target=run_connection, daemon=True)
    thread.start()
    return thread

async def connect(broker_url: str, username: str, password: str, client_id: str):
    """
    Establish MQTT connection with VDA5050 MasterControlClient.
    """
    global _connection_task
    
    # Start connection in a separate thread
    _connection_task = _connect_in_thread(broker_url, username, password, client_id)
    
    # Give the connection a moment to establish
    await asyncio.sleep(0.5)

async def disconnect():
    """Disconnect from MQTT broker and clear state"""
    global _client, _connection_task
    if _client:
        try:
            # Disconnect gracefully
            await _client.disconnect()
        except Exception as e:
            # Disconnect errors are handled gracefully
            pass
        finally:
            _client = None
    
    on_disconnected()
    
    # Stop the connection thread
    if _connection_task and _connection_task.is_alive():
        # The thread will stop when the event loop is closed
        _connection_task = None

def is_connected():
    """Check if MQTT client is connected"""
    return _client is not None and _connection_task is not None and _connection_task.is_alive()

def get_client():
    """Get the current MQTT client instance"""
    return _client if is_connected() else None

def get_debug_info():
    """Get debug information about the MQTT connection"""
    return {
        "connected": is_connected(),
        "client_exists": _client is not None,
        "connection_task_alive": _connection_task.is_alive() if _connection_task else False,
        "fleet_state_count": len(fleet_state),
        "fleet_state_keys": list(fleet_state.keys())
    }

async def send_instant_action_async(serial: str, action_type: str, blocking_type: str = "HARD", action_parameters: list = None) -> bool:
    """
    Send an instant action to a specific AGV.
    
    Args:
        serial: AGV serial number
        action_type: Type of action (e.g., "stopVehicle", "pause", "resume")
        blocking_type: Blocking type - "NONE", "SOFT", or "HARD" (default: "HARD")
        action_parameters: Optional list of action parameters
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not is_connected():
        print(f"Cannot send instant action: Not connected to broker")
        return False
    
    agv = fleet_state.get(serial)
    if not agv:
        print(f"Cannot send instant action: AGV {serial} not found")
        return False
    
    try:
        # Create the action
        action = Action(
            actionType=action_type,
            actionId=str(uuid.uuid4()),
            blockingType=BlockingType(blocking_type),
            actionParameters=action_parameters
        )
        
        # Create instant actions message
        instant_actions = InstantActions(
            headerId=1,  # This should be incremented per message in production
            timestamp=datetime.now(timezone.utc),
            version="2.1.0",
            manufacturer=agv.manufacturer,
            serialNumber=serial,
            actions=[action]
        )
        
        # Send via the client
        success = await _client.send_instant_action(
            target_manufacturer=agv.manufacturer,
            target_serial=serial,
            action=instant_actions
        )
        
        if success:
            print(f"✅ Sent instant action '{action_type}' to {serial}")
        else:
            print(f"❌ Failed to send instant action '{action_type}' to {serial}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error sending instant action to {serial}: {e}")
        return False

def send_instant_action(serial: str, action_type: str, blocking_type: str = "HARD", action_parameters: list = None) -> bool:
    """
    Synchronous wrapper to send instant action from non-async context.
    
    Args:
        serial: AGV serial number
        action_type: Type of action (e.g., "stopVehicle", "pause", "resume")
        blocking_type: Blocking type - "NONE", "SOFT", or "HARD" (default: "HARD")
        action_parameters: Optional list of action parameters
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not is_connected():
        return False
    
    try:
        # Get the event loop from the connection thread
        # We need to use the same loop that the client is using
        if _client and hasattr(_client, '_loop'):
            loop = _client._loop
        else:
            # Fallback: try to get the running loop or create new one
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        
        # Schedule the coroutine in the client's event loop
        future = asyncio.run_coroutine_threadsafe(
            send_instant_action_async(serial, action_type, blocking_type, action_parameters),
            loop
        )
        
        # Wait for result with timeout
        return future.result(timeout=5.0)
        
    except Exception as e:
        print(f"❌ Error in send_instant_action: {e}")
        return False
