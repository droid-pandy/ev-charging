from strands import Strands
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.charging_tools import search_chargers, reserve_charging_slot, check_charger_status

class ChargingNegotiationAgent:
    def __init__(self):
        self.strands = Strands(
            model_id=BEDROCK_MODEL_ID,
            region=AWS_REGION
        )
    
    def find_and_reserve(self, trip_plan: dict, preferences: dict = None) -> dict:
        system_prompt = """You are a charging negotiation specialist. Find the best charger 
based on price, speed, location, and availability. Reserve the optimal slot."""
        
        user_prompt = f"""
Trip Plan: {trip_plan}
User Preferences: {preferences or 'Prioritize speed and convenience'}

Find and reserve the best charging option."""
        
        response = self.strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=[search_chargers, reserve_charging_slot, check_charger_status],
            max_iterations=5
        )
        
        return {
            "reservation": response.final_response,
            "tool_results": [c.result for c in response.tool_calls] if response.tool_calls else []
        }
