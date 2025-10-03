# mqtt_client.py

"""
Stub MQTT client for MowbotFleet.
Provides minimal interface so the app can import and run.
"""

# Global flag to indicate connection status
connected = False

async def connect(broker_url: str, user: str, pwd: str, client_id: str) -> None:
    """
    Stub connect function.
    Should eventually establish MQTT connection and set connected=True.
    """
    global connected
    connected = True

async def disconnect() -> None:
    """
    Stub disconnect function.
    Should eventually tear down MQTT client and set connected=False.
    """
    global connected
    connected = False
