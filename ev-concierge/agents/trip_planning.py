from strands.models import BedrockModel
from strands import Agent
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.route_tools import calculate_energy_needs, get_route_info
import json
import asyncio

class TripPlanningAgent:
    def __init__(self):
        self.model = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            temperature=0.7
        )
    
    def analyze(self, vehicle_data: dict, trip_data: dict) -> dict:
        """Synchronous wrapper for async analyze"""
        return asyncio.run(self.analyze_async(vehicle_data, trip_data))
    
    async def analyze_async(self, vehicle_data: dict, trip_data: dict) -> dict:
        system_prompt = """You are a trip planning specialist for EVs.

You have access to tools that you MUST use. Never make calculations yourself.

CRITICAL: You MUST call the calculate_energy_needs tool first before providing any analysis.
Do NOT respond with text until you have called the tool and received the results."""
        
        user_prompt = f"""
Vehicle Information:
- Model: {vehicle_data['model']}
- Current Battery: {vehicle_data['battery_percent']}%
- Vehicle Range: {vehicle_data['range_miles']} miles

Trip Information:
- From: {trip_data['origin']}
- To: {trip_data['destination']}
- Distance: {trip_data['distance_miles']} miles
- Departure: {trip_data['departure']}

Use the calculate_energy_needs tool to analyze if charging is needed for this trip.
Call it with: battery_percent={vehicle_data['battery_percent']}, trip_distance_miles={trip_data['distance_miles']}, vehicle_range_miles={vehicle_data['range_miles']}"""
        
        # Create agent with tools
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=[calculate_energy_needs, get_route_info]
        )
        
        # Stream response and collect results
        response_text = ""
        tool_results = []
        
        print(f"\n🔍 DEBUG - Trip Planning Agent:")
        
        try:
            async for event in agent.stream_async(user_prompt):
                # Extract text from events
                if isinstance(event, dict):
                    if 'data' in event:
                        response_text += str(event['data'])
                    
                    # Look for tool results in the message
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
                                                    print(f"   - Tool result: {result_json}")
                                                except:
                                                    pass
            
            print(f"   Tool calls made: {len(tool_results)}")
            
        except Exception as e:
            print(f"   ⚠️  Error: {str(e)}")
            response_text = f"Error: {str(e)}"
        
        return {
            "analysis": response_text,
            "tool_results": tool_results
        }
