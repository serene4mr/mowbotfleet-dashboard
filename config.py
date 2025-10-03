"""
Configuration management for MowbotFleet Dashboard.
Handles loading, saving, and environment variable overrides.
"""

import os
import yaml
from typing import Dict, Any

# Configuration file path
LOCAL_CFG_PATH = "config_local.yaml"

# Default configuration values
DEFAULT_CONFIG = {
    "broker_host": "localhost",
    "broker_port": 1883,
    "use_tls": False,
    "broker_user": "",
    "broker_pass": "",
    "users": {}  # username -> hashed_password mapping
}

def load_config() -> Dict[str, Any]:
    """
    Load configuration from file with environment variable overrides.
    
    Loading order:
    1. Start with defaults
    2. Override with config_local.yaml values (if file exists)
    3. Override with environment variables (if set)
    
    Returns:
        Dict containing complete configuration
    """
    # Start with defaults
    config = DEFAULT_CONFIG.copy()
    
    # Load from file if it exists
    if os.path.exists(LOCAL_CFG_PATH):
        try:
            with open(LOCAL_CFG_PATH, 'r') as f:
                file_config = yaml.safe_load(f) or {}
                config.update(file_config)
        except (yaml.YAMLError, IOError) as e:
            print(f"Warning: Could not load {LOCAL_CFG_PATH}: {e}")
            print("Using defaults...")
    
    # Environment variable overrides
    config["broker_host"] = os.getenv("BROKER_HOST", config["broker_host"])
    config["broker_port"] = int(os.getenv("BROKER_PORT", str(config["broker_port"])))
    config["use_tls"] = os.getenv("BROKER_TLS", str(config["use_tls"])).lower() in ["1", "true", "yes"]
    config["broker_user"] = os.getenv("BROKER_USER", config["broker_user"])
    config["broker_pass"] = os.getenv("BROKER_PASS", config["broker_pass"])
    
    return config

def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to local YAML file.
    
    Args:
        config: Configuration dictionary to persist
        
    Raises:
        IOError: If file cannot be written
        yaml.YAMLError: If YAML serialization fails
    """
    try:
        with open(LOCAL_CFG_PATH, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False, indent=2)
    except (yaml.YAMLError, IOError) as e:
        raise IOError(f"Could not save configuration to {LOCAL_CFG_PATH}: {e}")

def get_broker_url(config: Dict[str, Any]) -> str:
    """
    Construct broker URL from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Complete MQTT broker URL
    """
    scheme = "mqtts" if config["use_tls"] else "mqtt"
    return f"{scheme}://{config['broker_host']}:{config['broker_port']}"
