from strands import Strands
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.charging_tools import check_charger_status, cancel_reservation, search_chargers, reserve_charging_slot

class MonitoringAgent:
    def __init__(self):
        self.strands = Strands(
            model_id=BEDROCK_MODEL_ID,
            region=AWS_REGION
        )
    
    def monitor_and_alert(self, reservation_id: str, charger_id: str, route: str) -> dict:
        system_prompt = """You are a monitoring specialist. Check charger status and handle 
issues proactively. If charger is offline, find alternative and rebook."""
        
        user_prompt = f"""
Reservation ID: {reservation_id}
Charger ID: {charger_id}
Route: {route}

Check status and alert if issues detected."""
        
        response = self.strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=[check_charger_status, cancel_reservation, search_chargers, reserve_charging_slot],
            max_iterations=6
        )
        
        return {
            "status": response.final_response,
            "tool_results": [c.result for c in response.tool_calls] if response.tool_calls else []
        }
