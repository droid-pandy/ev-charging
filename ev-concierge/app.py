import gradio as gr
import json
from datetime import datetime, timedelta
from agents.coordinator import CoordinatorAgent

# Initialize coordinator
coordinator = CoordinatorAgent()

# Default user state
default_vehicle = {
    "model": "Tesla Model Y",
    "battery_percent": 45,
    "range_miles": 300
}

default_preferences = {
    "auto_order_coffee": True,
    "favorite_drink": "Large Latte",
    "wallet_id": "WALLET-12345"
}

def parse_user_message(message: str, vehicle_state: dict) -> dict:
    """Parse natural language into trip data"""
    message_lower = message.lower()
    
    # Extract destination
    destination = "Los Angeles, CA"
    if "san francisco" in message_lower or "sf" in message_lower:
        destination = "San Francisco, CA"
        distance = 380
    elif "san diego" in message_lower:
        destination = "San Diego, CA"
        distance = 120
    elif "seattle" in message_lower:
        destination = "Seattle, WA"
        distance = 1150
    elif "las vegas" in message_lower:
        destination = "Las Vegas, NV"
        distance = 270
    else:
        distance = 280
    
    # Extract battery if mentioned
    battery = vehicle_state['battery_percent']
    if "battery" in message_lower or "charge" in message_lower or "%" in message:
        words = message.split()
        for i, word in enumerate(words):
            if '%' in word or (word.isdigit() and int(word) <= 100):
                try:
                    battery = int(word.replace('%', ''))
                    break
                except:
                    pass
    
    # Determine departure time
    tomorrow = datetime.now() + timedelta(days=1)
    if "tomorrow" in message_lower:
        departure = tomorrow.replace(hour=9, minute=0).isoformat()
    elif "tonight" in message_lower:
        departure = datetime.now().replace(hour=20, minute=0).isoformat()
    else:
        departure = tomorrow.replace(hour=9, minute=0).isoformat()
    
    return {
        "origin": "Current Location",
        "destination": destination,
        "distance_miles": distance,
        "departure": departure
    }, battery

def chat_interface(message, history, vehicle_state, preferences):
    """Main chat interface"""
    if not message:
        return history, vehicle_state, preferences
    
    # Parse user message
    trip_data, new_battery = parse_user_message(message, vehicle_state)
    vehicle_state['battery_percent'] = new_battery
    
    # Add user message to history
    history.append([message, None])
    
    # Show thinking message
    thinking_msg = "🤖 Analyzing your trip and coordinating agents..."
    history[-1][1] = thinking_msg
    yield history, vehicle_state, preferences
    
    try:
        # Run coordinator
        result = coordinator.orchestrate(vehicle_state, trip_data, preferences)
        
        # Format response
        response = f"**🚗 EV Concierge Summary**\n\n{result['summary']}\n\n"
        
        # Add details if available
        if 'results' in result:
            response += "\n**📋 Details:**\n"
            if 'charging' in result['results']:
                charging_tools = result['results']['charging'].get('tool_results', [])
                for tool_result in charging_tools:
                    if isinstance(tool_result, dict) and 'reservation_id' in tool_result:
                        response += f"- Reservation: `{tool_result['reservation_id']}`\n"
            
            if 'amenities' in result['results']:
                amenity_tools = result['results']['amenities'].get('tool_results', [])
                for tool_result in amenity_tools:
                    if isinstance(tool_result, dict) and 'order_id' in tool_result:
                        response += f"- Order: `{tool_result['order_id']}`\n"
        
        history[-1][1] = response
        
    except Exception as e:
        history[-1][1] = f"❌ Error: {str(e)}\n\nPlease check your AWS credentials and Bedrock access."
    
    yield history, vehicle_state, preferences

def update_vehicle_state(model, battery, range_miles):
    """Update vehicle state from UI"""
    return {
        "model": model,
        "battery_percent": int(battery),
        "range_miles": int(range_miles)
    }

def update_preferences(auto_order, favorite_drink, wallet_id):
    """Update user preferences from UI"""
    return {
        "auto_order_coffee": auto_order,
        "favorite_drink": favorite_drink,
        "wallet_id": wallet_id
    }

# Example prompts
examples = [
    ["I'm driving to Los Angeles tomorrow morning. Current battery is at 35%."],
    ["Trip to San Francisco next week. Battery at 50%. Find cheapest charging."],
    ["Emergency: Need to get to San Diego now. Only 25% charge left."],
    ["Road trip to Seattle. Battery at 80%. Plan all charging stops."],
    ["Going to Las Vegas tonight. 40% battery. Pre-order my usual coffee."]
]

# Build Gradio UI
with gr.Blocks(title="EV Concierge", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🚗 Proactive EV Concierge
    ### Multi-Agent AI System for Intelligent EV Charging Management
    
    Tell me about your trip and I'll handle everything: find chargers, make reservations, 
    pre-order food, and process payments autonomously.
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                height=500,
                label="Chat with your EV Concierge",
                show_label=True
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="e.g., 'I'm driving to LA tomorrow, battery at 40%'",
                    label="Your Message",
                    scale=4
                )
                submit = gr.Button("Send", variant="primary", scale=1)
            
            gr.Examples(
                examples=examples,
                inputs=msg,
                label="Example Requests"
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Vehicle Settings")
            vehicle_model = gr.Textbox(
                value=default_vehicle['model'],
                label="Vehicle Model"
            )
            battery_level = gr.Slider(
                minimum=0,
                maximum=100,
                value=default_vehicle['battery_percent'],
                step=1,
                label="Current Battery %"
            )
            vehicle_range = gr.Slider(
                minimum=100,
                maximum=500,
                value=default_vehicle['range_miles'],
                step=10,
                label="Vehicle Range (miles)"
            )
            
            gr.Markdown("### 🎯 Preferences")
            auto_order = gr.Checkbox(
                value=default_preferences['auto_order_coffee'],
                label="Auto-order coffee/food"
            )
            favorite_drink = gr.Textbox(
                value=default_preferences['favorite_drink'],
                label="Favorite Drink"
            )
            wallet_id = gr.Textbox(
                value=default_preferences['wallet_id'],
                label="Wallet ID"
            )
    
    # State management
    vehicle_state = gr.State(default_vehicle)
    preferences_state = gr.State(default_preferences)
    
    # Update states when settings change
    vehicle_inputs = [vehicle_model, battery_level, vehicle_range]
    for inp in vehicle_inputs:
        inp.change(
            fn=update_vehicle_state,
            inputs=vehicle_inputs,
            outputs=vehicle_state
        )
    
    pref_inputs = [auto_order, favorite_drink, wallet_id]
    for inp in pref_inputs:
        inp.change(
            fn=update_preferences,
            inputs=pref_inputs,
            outputs=preferences_state
        )
    
    # Chat interaction
    msg.submit(
        fn=chat_interface,
        inputs=[msg, chatbot, vehicle_state, preferences_state],
        outputs=[chatbot, vehicle_state, preferences_state]
    ).then(
        lambda: "",
        outputs=msg
    )
    
    submit.click(
        fn=chat_interface,
        inputs=[msg, chatbot, vehicle_state, preferences_state],
        outputs=[chatbot, vehicle_state, preferences_state]
    ).then(
        lambda: "",
        outputs=msg
    )
    
    gr.Markdown("""
    ---
    ### 🤖 Multi-Agent Architecture
    - **Trip Planning Agent**: Analyzes energy needs and route optimization
    - **Charging Negotiation Agent**: Finds and reserves optimal chargers
    - **Amenities Agent**: Pre-orders food and drinks
    - **Payment Agent**: Handles autonomous transactions
    - **Monitoring Agent**: Real-time tracking and alerts
    - **Coordinator Agent**: Orchestrates all agents
    
    **Powered by**: Amazon Bedrock (Claude 3.5 Sonnet) + AWS Strands SDK
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
