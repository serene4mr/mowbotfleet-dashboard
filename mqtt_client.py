# mqtt_client.py

import asyncio
import threading
from datetime import datetime
from typing import Dict
from vda5050.clients.master_control import MasterControlClient
from vda5050.models.state import State
from models import AGVInfo, ErrorInfo

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
            last_update=datetime.utcnow()
        )
        fleet_state[serial] = info

    # Update AGV information from state
    info.battery = state.batteryState.batteryCharge
    info.operating_mode = state.operatingMode.value
    info.position = (state.agvPosition.y, state.agvPosition.x)
    info.theta = state.agvPosition.theta or 0.0
    info.last_update = datetime.utcnow()
    info.current_order = state.orderId
    info.errors = [
        ErrorInfo(datetime.utcnow(), e.errorType, e.errorDescription, e.errorLevel.value)
        for e in (state.errorList or [])
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
                    print(f"Invalid port number in broker URL: {broker_port}")
                    return
            else:
                print(f"Port must be specified in broker URL. Expected format: 'host:port', got: '{broker_url_clean}'")
                return
            
            # Initialize MasterControlClient with required parameters
            _client = MasterControlClient(
                broker_url=broker_host,
                manufacturer="MowbotAI",
                serial_number="MowbotFleetClient",
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
            print(f"Connection error: {e}")
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
            # Log any disconnect errors but don't crash
            print(f"Warning: Disconnect error: {e}")
        finally:
            _client = None
    
    on_disconnected()
    
    # Stop the connection thread
    if _connection_task and _connection_task.is_alive():
        # The thread will stop when the event loop is closed
        _connection_task = None
