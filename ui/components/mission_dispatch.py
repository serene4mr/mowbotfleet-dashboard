# ui/components/mission_dispatch.py

import streamlit as st
from datetime import datetime
from mqtt_client import fleet_state

def render_mission_dispatch():
    """Render mission dispatch form"""
    st.markdown("#### 📝 Dispatch New Mission")
    
    if not fleet_state:
        st.warning("No AGVs available for mission dispatch.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Target AGV selection
        agv_options = list(fleet_state.keys())
        target_agv = st.selectbox(
            "Target AGV:",
            options=agv_options,
            key="mission_target_agv"
        )
    
    with col2:
        # Auto-generated Order ID
        order_id = f"ORDER-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        st.text_input(
            "Order ID:",
            value=order_id,
            disabled=True,
            key="mission_order_id"
        )
    
    # Nodes input
    st.markdown("**Nodes:** (Format: nodeId,x,y,theta)")
    nodes_text = st.text_area(
        "Enter nodes (one per line):",
        placeholder="warehouse_pickup,10.5,20.3,0.0\ndelivery_zone_A,15.2,25.1,1.57\ncharging_station,5.0,5.0,3.14",
        height=120,
        key="mission_nodes_input"
    )
    
    # Send mission button
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🚀 Send Mission", type="primary"):
            if nodes_text.strip():
                try:
                    # Parse nodes
                    nodes = parse_nodes(nodes_text)
                    if nodes:
                        # Send mission (placeholder for now)
                        st.success(f"Mission {order_id} sent to {target_agv}")
                        st.rerun()
                    else:
                        st.error("Please enter valid nodes.")
                except Exception as e:
                    st.error(f"Failed to send mission: {str(e)}")
            else:
                st.error("Please enter at least one node.")
    
    with col2:
        if st.button("🗑️ Clear Form"):
            st.rerun()

def parse_nodes(nodes_text: str) -> list:
    """Parse nodes from text input"""
    nodes = []
    for line in nodes_text.strip().split('\n'):
        if line.strip():
            parts = line.strip().split(',')
            if len(parts) >= 4:
                try:
                    node = {
                        'nodeId': parts[0].strip(),
                        'x': float(parts[1].strip()),
                        'y': float(parts[2].strip()),
                        'theta': float(parts[3].strip())
                    }
                    nodes.append(node)
                except ValueError:
                    continue
    return nodes
