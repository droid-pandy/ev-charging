import streamlit as st
import json
from datetime import datetime, timedelta
from agents.coordinator import CoordinatorAgent
import time

st.set_page_config(page_title="EV Concierge", page_icon="🚗", layout="wide")

# Initialize
if 'coordinator' not in st.session_state:
    st.session_state.coordinator = CoordinatorAgent()
    st.session_state.vehicle = {"model": "Tesla Model Y", "battery_percent": 45, "range_miles": 300}
    st.session_state.preferences = {"auto_order_coffee": True, "favorite_drink": "Large Latte", "wallet_id": "WALLET-12345"}
    st.session_state.agent_status = {}
    st.session_state.trip_active = False
    st.session_state.notifications = []

# Header
st.markdown("# 🚗 Proactive EV Concierge")
st.markdown("### Multi-Agent AI System for Autonomous Charging Management")

# Main Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🗺️ Trip Planning")
    
    # Trip Input
    with st.form("trip_form"):
        destination = st.selectbox("Destination", ["Los Angeles, CA", "San Francisco, CA", "San Diego, CA", "Seattle, WA", "Las Vegas, NV"])
        departure = st.selectbox("Departure", ["Tomorrow Morning", "Tonight", "Next Week"])
        
        col_a, col_b = st.columns(2)
        with col_a:
            current_battery = st.slider("Current Battery %", 0, 100, st.session_state.vehicle['battery_percent'])
        with col_b:
            priority = st.selectbox("Priority", ["Fastest Route", "Cheapest Charging", "Most Amenities"])
        
        submitted = st.form_submit_button("🚀 Start Trip Planning", use_container_width=True)
    
    if submitted:
        st.session_state.trip_active = True
        st.session_state.notifications = []
        
        # Build trip data
        distance_map = {"Los Angeles, CA": 280, "San Francisco, CA": 380, "San Diego, CA": 120, "Seattle, WA": 1150, "Las Vegas, NV": 270}
        trip_data = {
            "origin": "Current Location",
            "destination": destination,
            "distance_miles": distance_map.get(destination, 280),
            "departure": (datetime.now() + timedelta(days=1)).replace(hour=9, minute=0).isoformat()
        }
        st.session_state.vehicle['battery_percent'] = current_battery
        
        # Agent Activity Panel
        st.markdown("---")
        st.markdown("### 🤖 Agent Activity (Live)")
        
        agent_container = st.container()
        with agent_container:
            status_cols = st.columns(6)
            agent_names = ["Coordinator", "Trip Planning", "Charging", "Amenities", "Payment", "Monitoring"]
            
            for idx, agent in enumerate(agent_names):
                with status_cols[idx]:
                    st.markdown(f"**{agent}**")
                    placeholder = st.empty()
                    placeholder.info("⏳ Waiting")
                    st.session_state.agent_status[agent] = placeholder
        
        # Simulate agent execution
        progress_bar = st.progress(0)
        result_placeholder = st.empty()
        
        try:
            # Update agent statuses
            for idx, agent in enumerate(agent_names):
                st.session_state.agent_status[agent].warning("🔄 Working...")
                progress_bar.progress((idx + 1) / len(agent_names))
                time.sleep(0.3)
            
            # Run coordinator
            result = st.session_state.coordinator.orchestrate(
                st.session_state.vehicle,
                trip_data,
                st.session_state.preferences
            )
            
            # Mark agents complete
            for agent in agent_names:
                st.session_state.agent_status[agent].success("✅ Complete")
            
            progress_bar.progress(100)
            
            # Display results
            result_placeholder.success(f"### ✅ Trip Planned Successfully\n\n{result['summary']}")
            
            # Add notifications
            st.session_state.notifications.append({
                "time": datetime.now().strftime("%H:%M"),
                "message": f"Trip to {destination} planned",
                "type": "success"
            })
            
            if 'results' in result and 'charging' in result['results']:
                charging_tools = result['results']['charging'].get('tool_results', [])
                for tool_result in charging_tools:
                    if isinstance(tool_result, dict) and 'reservation_id' in tool_result:
                        st.session_state.notifications.append({
                            "time": datetime.now().strftime("%H:%M"),
                            "message": f"Charger reserved: {tool_result['reservation_id']}",
                            "type": "info"
                        })
            
        except Exception as e:
            result_placeholder.error(f"❌ Error: {str(e)}")
            for agent in agent_names:
                st.session_state.agent_status[agent].error("❌ Failed")

with col2:
    st.markdown("### ⚙️ Vehicle Status")
    
    # Vehicle Info Card
    with st.container():
        st.markdown(f"**Model:** {st.session_state.vehicle['model']}")
        st.metric("Battery Level", f"{st.session_state.vehicle['battery_percent']}%", 
                  delta=None if not st.session_state.trip_active else "-5%")
        st.metric("Range", f"{st.session_state.vehicle['range_miles']} mi")
        
        # Battery visualization
        battery_color = "🟢" if st.session_state.vehicle['battery_percent'] > 50 else "🟡" if st.session_state.vehicle['battery_percent'] > 20 else "🔴"
        st.progress(st.session_state.vehicle['battery_percent'] / 100)
        st.caption(f"{battery_color} Battery Status")
    
    st.markdown("---")
    st.markdown("### 🔔 Notifications")
    
    # Notifications Panel
    notif_container = st.container()
    with notif_container:
        if st.session_state.notifications:
            for notif in reversed(st.session_state.notifications[-5:]):
                icon = "✅" if notif['type'] == 'success' else "ℹ️"
                st.markdown(f"{icon} **{notif['time']}** - {notif['message']}")
        else:
            st.info("No notifications yet")
    
    st.markdown("---")
    st.markdown("### 🎯 Preferences")
    
    with st.expander("Edit Preferences"):
        auto_order = st.checkbox("Auto-order coffee/food", value=st.session_state.preferences['auto_order_coffee'])
        favorite_drink = st.text_input("Favorite Drink", value=st.session_state.preferences['favorite_drink'])
        wallet_id = st.text_input("Wallet ID", value=st.session_state.preferences['wallet_id'])
        
        if st.button("Save Preferences"):
            st.session_state.preferences = {
                "auto_order_coffee": auto_order,
                "favorite_drink": favorite_drink,
                "wallet_id": wallet_id
            }
            st.success("Preferences saved!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>
    🤖 <b>Multi-Agent Architecture</b>: Trip Planning • Charging Negotiation • Amenities • Payment • Monitoring • Coordinator<br>
    Powered by <b>Amazon Bedrock (Claude 3.5 Sonnet)</b> + AWS Strands SDK
    </small>
</div>
""", unsafe_allow_html=True)
