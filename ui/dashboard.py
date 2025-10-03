# ui/dashboard.py

import streamlit as st

def render_header():
    st.markdown("### Dashboard")
    status = "🟢 Connected" if st.session_state.get("user") and st.query_params.get("connected", "false") == "true" else "🔴 Disconnected"
    st.write(f"**Broker Status:** {status}")

def render_row1():
    st.subheader("Fleet Overview & Map")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Fleet Table (placeholder)")
    with col2:
        st.write("Map View (placeholder)")

def render_row2():
    st.subheader("AGV Details & Quick Controls")
    col1, col2 = st.columns([3,1])
    with col1:
        st.write("AGV Details (placeholder)")
    with col2:
        st.write("Controls: [🛑 E-STOP] [▶️ Resume] [⏸️ Pause] [🔄]")

def render_row3():
    st.subheader("Mission Dispatch")
    st.write("Mission Dispatch Form (placeholder)")
