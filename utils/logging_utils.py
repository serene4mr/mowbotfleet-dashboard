# utils/logging_utils.py

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    name: str = "mowbot_fleet",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console: Whether to log to console
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_mission_logger() -> logging.Logger:
    """Get logger for mission dispatch operations."""
    return logging.getLogger("mowbot_fleet.mission")


def get_mqtt_logger() -> logging.Logger:
    """Get logger for MQTT operations."""
    return logging.getLogger("mowbot_fleet.mqtt")


def get_agv_logger() -> logging.Logger:
    """Get logger for AGV operations."""
    return logging.getLogger("mowbot_fleet.agv")


def log_mission_dispatch(
    order_id: str,
    target_agv: str,
    node_count: int,
    success: bool,
    error: Optional[str] = None
) -> None:
    """
    Log mission dispatch events.
    
    Args:
        order_id: Mission order ID
        target_agv: Target AGV serial
        node_count: Number of waypoints
        success: Whether dispatch was successful
        error: Error message if failed
    """
    logger = get_mission_logger()
    
    if success:
        logger.info(
            f"Mission dispatched successfully - "
            f"Order: {order_id}, AGV: {target_agv}, Nodes: {node_count}"
        )
    else:
        logger.error(
            f"Mission dispatch failed - "
            f"Order: {order_id}, AGV: {target_agv}, Error: {error}"
        )


def log_agv_state_update(
    agv_serial: str,
    position: tuple,
    battery: float,
    mode: str,
    error_count: int
) -> None:
    """
    Log AGV state updates.
    
    Args:
        agv_serial: AGV serial number
        position: (x, y) position coordinates
        battery: Battery percentage
        mode: Operating mode
        error_count: Number of active errors
    """
    logger = get_agv_logger()
    
    x, y = position
    logger.debug(
        f"AGV state update - "
        f"Serial: {agv_serial}, Position: ({x:.2f}, {y:.2f}), "
        f"Battery: {battery:.1f}%, Mode: {mode}, Errors: {error_count}"
    )


def log_mqtt_event(
    event_type: str,
    details: str,
    level: str = "INFO"
) -> None:
    """
    Log MQTT events.
    
    Args:
        event_type: Type of MQTT event (connect, disconnect, publish, subscribe)
        details: Event details
        level: Log level
    """
    logger = get_mqtt_logger()
    
    log_level = getattr(logging, level.upper())
    logger.log(log_level, f"MQTT {event_type.upper()}: {details}")


def log_mission_progress(
    order_id: str,
    agv_serial: str,
    current_node: str,
    progress: str,
    status: str
) -> None:
    """
    Log mission progress updates.
    
    Args:
        order_id: Mission order ID
        agv_serial: AGV serial number
        current_node: Current node ID
        progress: Progress description
        status: Mission status
    """
    logger = get_mission_logger()
    
    logger.info(
        f"Mission progress - "
        f"Order: {order_id}, AGV: {agv_serial}, "
        f"Node: {current_node}, Progress: {progress}, Status: {status}"
    )


def log_system_event(
    event: str,
    details: Optional[str] = None,
    level: str = "INFO"
) -> None:
    """
    Log general system events.
    
    Args:
        event: Event description
        details: Additional details
        level: Log level
    """
    logger = logging.getLogger("mowbot_fleet.system")
    
    message = event
    if details:
        message += f" - {details}"
    
    log_level = getattr(logging, level.upper())
    logger.log(log_level, message)


# Initialize default logging
def initialize_logging():
    """Initialize default logging configuration."""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Set up main logger
    setup_logging(
        name="mowbot_fleet",
        level="INFO",
        log_file="logs/mowbot_fleet.log",
        console=True
    )
    
    # Set up specific loggers
    setup_logging(
        name="mowbot_fleet.mission",
        level="INFO",
        log_file="logs/missions.log",
        console=False
    )
    
    setup_logging(
        name="mowbot_fleet.mqtt",
        level="DEBUG",
        log_file="logs/mqtt.log",
        console=False
    )
    
    setup_logging(
        name="mowbot_fleet.agv",
        level="INFO",
        log_file="logs/agv.log",
        console=False
    )
    
    setup_logging(
        name="mowbot_fleet.system",
        level="INFO",
        log_file="logs/system.log",
        console=False
    )
    
    # Log initialization
    logger = logging.getLogger("mowbot_fleet.system")
    logger.info("Logging system initialized")


if __name__ == "__main__":
    # Test logging setup
    initialize_logging()
    
    # Test different loggers
    log_mission_dispatch("ORDER-123", "AGV-001", 3, True)
    log_mission_dispatch("ORDER-124", "AGV-002", 5, False, "AGV offline")
    log_agv_state_update("AGV-001", (10.5, 20.3), 85.2, "AUTOMATIC", 0)
    log_mqtt_event("connect", "Connected to broker at localhost:1883")
    log_mission_progress("ORDER-123", "AGV-001", "node_2", "2/3 nodes", "RUNNING")
    log_system_event("Application started", "Streamlit server running on port 8501")
    
    print("✅ Logging test completed - check logs/ directory for output files")
