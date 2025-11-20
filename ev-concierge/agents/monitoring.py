from strands.models import BedrockModel
from strands import Agent
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.charging_tools import check_charger_status, cancel_reservation, search_chargers, reserve_charging_slot
import json
import asyncio

class MonitoringAgent:
    def __init__(self):
        self.model = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            temperature=0.7
        )
    
    def monitor_and_alert(self, reservation_id: str, charger_id: str, route: str) -> dict:
        """Synchronous wrapper for async monitor_and_alert"""
        return asyncio.run(self.monitor_and_alert_async(reservation_id, charger_id, route))
    
    async def monitor_and_alert_async(self, reservation_id: str, charger_id: str, route: str) -> dict:
        system_prompt = """You are a monitoring specialist. Check charger status and handle 
issues proactively. If charger is offline, find alternative and rebook."""
        
        user_prompt = f"""
Reservation ID: {reservation_id}
Charger ID: {charger_id}
Route: {route}

Check status and alert if issues detected."""
        
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=[check_charger_status, cancel_reservation, search_chargers, reserve_charging_slot]
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
            "status": response_text,
            "tool_results": tool_results
        }
