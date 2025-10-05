# utils/mission_utils.py

import re
from typing import List, Dict, Any
from datetime import datetime, timezone
from config import load_config


def parse_nodes_input(nodes_text: str) -> List[Dict[str, Any]]:
    """
    Parse nodes input text into structured data.
    
    Expected format: nodeId,x,y,theta (one per line)
    Example:
        warehouse_pickup,10.5,20.3,0.0
        delivery_zone_A,15.2,25.1,1.57
        charging_station,20.0,25.0,3.14
    
    Args:
        nodes_text: Raw text input from user
        
    Returns:
        List of parsed node dictionaries
        
    Raises:
        ValueError: If parsing fails or format is invalid
    """
    if not nodes_text or not nodes_text.strip():
        raise ValueError("Empty nodes input")
    
    nodes = []
    lines = nodes_text.strip().split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Split by comma and validate
        parts = [part.strip() for part in line.split(',')]
        
        if len(parts) != 4:
            raise ValueError(f"Line {line_num}: Expected 4 values (nodeId,x,y,theta), got {len(parts)}")
        
        node_id, x_str, y_str, theta_str = parts
        
        # Validate node ID
        if not node_id:
            raise ValueError(f"Line {line_num}: Node ID cannot be empty")
        
        # Validate and convert coordinates
        try:
            x = float(x_str)
            y = float(y_str)
            theta = float(theta_str)
        except ValueError as e:
            raise ValueError(f"Line {line_num}: Invalid number format - {str(e)}")
        
        # Basic range validation (can be adjusted based on AGV capabilities)
        if abs(x) > 1000 or abs(y) > 1000:
            raise ValueError(f"Line {line_num}: Coordinates seem too large (max ±1000m)")
        
        # Normalize theta to [-π, π] range
        while theta > 3.14159265359:
            theta -= 2 * 3.14159265359
        while theta < -3.14159265359:
            theta += 2 * 3.14159265359
        
        node = {
            'nodeId': node_id,
            'x': x,
            'y': y,
            'theta': theta,
            'line_number': line_num
        }
        
        nodes.append(node)
    
    if not nodes:
        raise ValueError("No valid nodes found")
    
    # Check for duplicate node IDs
    node_ids = [node['nodeId'] for node in nodes]
    if len(node_ids) != len(set(node_ids)):
        duplicates = [node_id for node_id in set(node_ids) if node_ids.count(node_id) > 1]
        raise ValueError(f"Duplicate node IDs found: {', '.join(duplicates)}")
    
    return nodes


def validate_nodes(nodes: List[Dict[str, Any]]) -> List[str]:
    """
    Validate parsed nodes for logical consistency.
    
    Args:
        nodes: List of parsed node dictionaries
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not nodes:
        errors.append("No nodes provided")
        return errors
    
    # Load config for mission limits
    config = load_config()
    mission_config = config.get("mission", {})
    max_nodes = mission_config.get("max_nodes_per_mission", 100)
    
    # Check maximum nodes limit
    if len(nodes) > max_nodes:
        errors.append(f"Too many nodes: {len(nodes)} (maximum: {max_nodes})")
        return errors
    
    # Check minimum distance between consecutive nodes
    for i in range(len(nodes) - 1):
        current = nodes[i]
        next_node = nodes[i + 1]
        
        # Calculate distance
        dx = next_node['x'] - current['x']
        dy = next_node['y'] - current['y']
        distance = (dx**2 + dy**2)**0.5
        
        # Warn if nodes are too close (adjust threshold as needed)
        if distance < 0.1:  # 10cm minimum
            errors.append(f"Nodes '{current['nodeId']}' and '{next_node['nodeId']}' are very close ({distance:.2f}m)")
    
    return errors


def format_nodes_preview(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format nodes for preview display.
    
    Args:
        nodes: List of parsed node dictionaries
        
    Returns:
        List formatted for Streamlit dataframe display
    """
    preview_data = []
    
    for i, node in enumerate(nodes):
        preview_data.append({
            "Order": i + 1,
            "Node ID": node['nodeId'],
            "X (m)": f"{node['x']:.2f}",
            "Y (m)": f"{node['y']:.2f}",
            "Theta (rad)": f"{node['theta']:.3f}",
            "Line": node['line_number']
        })
    
    return preview_data


def generate_order_id(prefix: str = None) -> str:
    """
    Generate a unique order ID with timestamp.
    
    Args:
        prefix: Order ID prefix (if None, uses config default)
        
    Returns:
        Unique order ID string
    """
    if prefix is None:
        config = load_config()
        mission_config = config.get("mission", {})
        prefix = mission_config.get("default_order_prefix", "ORDER")
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"{prefix}-{timestamp}"


def validate_order_id(order_id: str) -> bool:
    """
    Validate order ID format.
    
    Expected format: ORDER-YYYYMMDD-HHMMSS or custom format
    
    Args:
        order_id: Order ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not order_id or not order_id.strip():
        return False
    
    # Allow alphanumeric with hyphens and underscores
    pattern = r'^[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, order_id.strip()))
