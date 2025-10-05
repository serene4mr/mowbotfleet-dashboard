# utils/mission_utils.py

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from config import load_config

# VDA5050 imports
from vda5050.models.order import Order, Node, Edge, NodePosition
from vda5050.models.base import Action, BlockingType


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


def create_vda5050_order(
    order_id: str,
    target_manufacturer: str,
    target_serial: str,
    nodes: List[Dict[str, Any]],
    version: str = "2.1.0",
    header_id: int = 1
) -> Order:
    """
    Create a VDA5050 Order message from parsed nodes.
    
    Args:
        order_id: Unique order identifier
        target_manufacturer: Target AGV manufacturer
        target_serial: Target AGV serial number
        nodes: List of parsed node dictionaries
        version: VDA5050 protocol version
        header_id: Header ID for the order
        
    Returns:
        VDA5050 Order message object
        
    Raises:
        ValueError: If nodes list is empty or invalid
    """
    if not nodes:
        raise ValueError("Cannot create order with empty nodes list")
    
    # Create VDA5050 Node objects
    vda5050_nodes = []
    for i, node_data in enumerate(nodes):
        # Create node position from parsed coordinates
        node_position = NodePosition(
            x=node_data['x'],
            y=node_data['y'],
            theta=node_data['theta'],
            mapId='default_map'  # Default map ID for mission waypoints
        )
        
        node = Node(
            nodeId=node_data['nodeId'],
            sequenceId=i * 2,  # Even numbers for nodes
            released=True,  # All nodes are released for MVP
            nodePosition=node_position,  # Include the actual coordinates
            actions=[]  # No actions for MVP
        )
        vda5050_nodes.append(node)
    
    # Create VDA5050 Edge objects (connect consecutive nodes)
    vda5050_edges = []
    for i in range(len(nodes) - 1):
        edge = Edge(
            edgeId=f"edge_{nodes[i]['nodeId']}_to_{nodes[i+1]['nodeId']}",
            sequenceId=i * 2 + 1,  # Odd numbers for edges
            released=True,  # All edges are released for MVP
            startNodeId=nodes[i]['nodeId'],
            endNodeId=nodes[i+1]['nodeId'],
            actions=[]  # No actions for MVP
        )
        vda5050_edges.append(edge)
    
    # Create VDA5050 Order
    order = Order(
        headerId=header_id,
        timestamp=datetime.now(timezone.utc),
        version=version,
        manufacturer=target_manufacturer,
        serialNumber=target_serial,
        orderId=order_id,
        orderUpdateId=0,  # Initial order
        nodes=vda5050_nodes,
        edges=vda5050_edges
    )
    
    return order


def create_mission_summary(order: Order) -> Dict[str, Any]:
    """
    Create a human-readable summary of the mission order.
    
    Args:
        order: VDA5050 Order object
        
    Returns:
        Dictionary with mission summary information
    """
    return {
        "order_id": order.orderId,
        "target_agv": f"{order.manufacturer}/{order.serialNumber}",
        "total_nodes": len(order.nodes),
        "total_edges": len(order.edges),
        "released_nodes": len([n for n in order.nodes if n.released]),
        "released_edges": len([e for e in order.edges if e.released]),
        "timestamp": order.timestamp.isoformat(),
        "version": order.version
    }


async def send_mission_order(order: Order, mqtt_client) -> bool:
    """
    Send a VDA5050 Order message via MQTT.
    
    Args:
        order: VDA5050 Order object to send
        mqtt_client: Connected MQTT client (MasterControlClient)
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Use the MasterControlClient's send_order method
        success = await mqtt_client.send_order(
            target_manufacturer=order.manufacturer,
            target_serial=order.serialNumber,
            order=order
        )
        
        return success
        
    except Exception as e:
        # Log error (will be handled by calling code)
        raise Exception(f"Failed to send order {order.orderId}: {str(e)}")
