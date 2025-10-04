"""
Enhanced Configuration management for MowbotFleet Dashboard.
Handles loading with defaults + user overrides + environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge override dict into base dict.
    Preserves nested structure for broker.host, logging.modules, etc.
    
    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def load_config() -> Dict[str, Any]:
    """
    Load configuration with hierarchy: defaults + user overrides + environment variables.
    
    Loading order:
    1. Load config/config_default.yaml (developer defaults)
    2. Load config/config_local.yaml (user overrides)
    3. Apply environment variable overrides
    
    Returns:
        Complete configuration dictionary
        
    Raises:
        FileNotFoundError: If config_default.yaml is missing
        yaml.YAMLError: If YAML files are malformed
    """
    # 1. Load defaults (always present in source code)
    defaults_path = Path("config/config_default.yaml")
    if not defaults_path.exists():
        raise FileNotFoundError("config_default.yaml missing - corrupted installation")
    
    with open(defaults_path) as f:
        config = yaml.safe_load(f) or {}
    
    # 2. Load user overrides (optional)
    local_path = Path("config/config_local.yaml")
    if local_path.exists():
        try:
            with open(local_path) as f:
                user_config = yaml.safe_load(f) or {}
                config = deep_merge(config, user_config)
        except yaml.YAMLError as e:
            print(f"Warning: Invalid config_local.yaml: {e}")
            print("Using defaults only...")
    
    # 3. Environment variable overrides (production/Docker)
    if "BROKER_HOST" in os.environ:
        config["broker"]["host"] = os.environ["BROKER_HOST"]
    if "BROKER_PORT" in os.environ:
        config["broker"]["port"] = int(os.environ["BROKER_PORT"])
    if "BROKER_USER" in os.environ:
        config["broker"]["user"] = os.environ["BROKER_USER"]
    if "BROKER_PASSWORD" in os.environ:
        config["broker"]["password"] = os.environ["BROKER_PASSWORD"]
    if "BROKER_TLS" in os.environ:
        config["broker"]["use_tls"] = os.environ["BROKER_TLS"].lower() in ["1", "true", "yes"]
    
    return config

def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to local YAML file.
    Only saves user-overridable settings to avoid overwriting defaults.
    
    Args:
        config: Configuration dictionary to persist
        
    Raises:
        IOError: If file cannot be written
        yaml.YAMLError: If YAML serialization fails
    """
    local_path = Path("config/config_local.yaml")
    local_path.parent.mkdir(exist_ok=True)
    
    try:
        with open(local_path, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False, indent=2)
    except (yaml.YAMLError, IOError) as e:
        raise IOError(f"Could not save configuration to {local_path}: {e}")

def get_broker_url(config: Dict[str, Any]) -> str:
    """
    Construct broker URL from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Complete MQTT broker URL (host:port format for VDA5050 client)
    """
    broker_config = config.get("broker", {})
    host = broker_config.get("host", "127.0.0.1")
    port = broker_config.get("port", 1883)
    
    # For VDA5050 client, return host:port format
    return f"{host}:{port}"

def get_broker_credentials(config: Dict[str, Any]) -> tuple:
    """
    Get broker credentials from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (username, password)
    """
    broker_config = config.get("broker", {})
    username = broker_config.get("user", "")
    password = broker_config.get("password", "")
    return username, password

def validate_config(config: Dict[str, Any]) -> list:
    """
    Validate configuration for required settings and logical consistency.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Validate broker settings
    broker = config.get("broker", {})
    if not broker.get("host"):
        errors.append("Broker host is required")
    if not isinstance(broker.get("port"), int) or broker.get("port", 0) <= 0:
        errors.append("Broker port must be a positive integer")
    
    # Validate mission settings
    mission = config.get("mission", {})
    max_nodes = mission.get("max_nodes_per_mission", 0)
    if not isinstance(max_nodes, int) or max_nodes <= 0:
        errors.append("max_nodes_per_mission must be a positive integer")
    
    # Validate logging settings
    logging_config = config.get("logging", {})
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if logging_config.get("global_level") not in valid_levels:
        errors.append(f"Logging global_level must be one of: {valid_levels}")
    
    return errors