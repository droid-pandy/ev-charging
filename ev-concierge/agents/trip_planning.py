from strands import Strands
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.route_tools import calculate_energy_needs, get_route_info

class TripPlanningAgent:
    def __init__(self):
        self.strands = Strands(
            model_id=BEDROCK_MODEL_ID,
            region=AWS_REGION
        )
    
    def analyze(self, vehicle_data: dict, trip_data: dict) -> dict:
        system_prompt = """You are a trip planning specialist for EVs. Analyze energy needs 
and recommend the optimal charging strategy. Be concise and actionable."""
        
        user_prompt = f"""
Vehicle: {vehicle_data['model']}, Battery: {vehicle_data['battery_percent']}%, Range: {vehicle_data['range_miles']} miles
Trip: {trip_data['origin']} to {trip_data['destination']}, Distance: {trip_data['distance_miles']} miles
Departure: {trip_data['departure']}

Analyze if charging is needed and recommend strategy."""
        
        response = self.strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=[calculate_energy_needs, get_route_info],
            max_iterations=3
        )
        
        return {
            "analysis": response.final_response,
            "tool_results": [c.result for c in response.tool_calls] if response.tool_calls else []
        }
