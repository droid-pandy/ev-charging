from strands.models import BedrockModel
from strands import Agent
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.charging_tools import search_chargers, reserve_charging_slot, check_charger_status
import json
import asyncio

class ChargingNegotiationAgent:
    def __init__(self):
        self.model = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            temperature=0.7
        )
    
    def find_and_reserve(self, trip_data: dict, preferences: dict = None) -> dict:
        """Synchronous wrapper for async find_and_reserve"""
        return asyncio.run(self.find_and_reserve_async(trip_data, preferences))
    
    async def find_and_reserve_async(self, trip_data: dict, preferences: dict = None) -> dict:
        origin = trip_data.get('origin', 'Unknown')
        destination = trip_data.get('destination', 'Unknown')
        
        # Extract vehicle data for range calculation
        vehicle_data = trip_data.get('vehicle_data', {})
        battery_percent = vehicle_data.get('battery_percent', 100)
        vehicle_range = vehicle_data.get('range_miles', 300)
        current_range = int((battery_percent / 100) * vehicle_range)
        
        system_prompt = """You are a charging negotiation specialist. Find the best charger 
based on price, speed, location, and availability. Reserve the optimal slot.

IMPORTANT: 
1. Call search_chargers with the ORIGIN, DESTINATION, and CURRENT_RANGE_MILES
2. The system will only return stations you can actually reach with your current battery
3. If the response contains an "error" field with "insufficient_range":
   - DO NOT try to reserve a station
   - Inform the user they need to charge at home first
   - Show them which stations they could reach if fully charged (from "stations_if_fully_charged")
   - Recommend charging to 100% before departure
4. If stations are found, reserve the best one and include:
   - charger_id: from the search results
   - time_slot: pick from available slots
   - location: the location field from the charger
   - network: the network field from the charger (e.g., "Tesla Supercharger", "EVgo")

Example responses:
- If insufficient range: "⚠️ Your current battery (35%, 105 miles) cannot reach any charging stations on this route. Please charge to 100% at home before departure. Once fully charged, your first stop would be: Tesla Supercharger at Lost Hills, CA (134 miles away)."
- If stations found: search_chargers() then reserve_charging_slot(charger_id="OCM-12345", time_slot="10:00", location="Kettleman City, CA", network="Tesla Supercharger")"""
        
        user_prompt = f"""
Trip: {origin} → {destination}
Current Battery: {battery_percent}% ({current_range} miles range)
User Preferences: {preferences or 'Prioritize speed and convenience'}

CRITICAL: First call search_chargers(route="{origin}", destination="{destination}", min_power_kw=150, current_range_miles={current_range})

If the response contains "error": "insufficient_range":
- DO NOT attempt to reserve
- Explain to the user they need to charge at home first
- Mention the stations they could reach if fully charged

If stations are found:
- Reserve the best one with all required parameters (charger_id, time_slot, location, network)"""
        
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=[search_chargers, reserve_charging_slot, check_charger_status]
        )
        
        response_text = ""
        tool_results = []
        
        try:
            async for event in agent.stream_async(user_prompt):
                if isinstance(event, dict):
                    if 'data' in event:
                        response_text += str(event['data'])
                    
                    # Extract tool results from message
                    if 'message' in event:
                        message = event['message']
                        if isinstance(message, dict) and 'content' in message:
                            for content_block in message['content']:
                                if isinstance(content_block, dict) and 'toolResult' in content_block:
                                    tool_result = content_block['toolResult']
                                    if 'content' in tool_result:
                                        for content_item in tool_result['content']:
                                            if 'text' in content_item:
                                                try:
                                                    result_json = json.loads(content_item['text'])
                                                    tool_results.append(result_json)
                                                except:
                                                    pass
        except Exception as e:
            response_text = f"Error: {str(e)}"
        
        return {
            "reservation": response_text,
            "tool_results": tool_results
        }
