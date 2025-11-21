#!/usr/bin/env python3
"""
Simple test to verify tool calling with real Strands SDK
"""
import sys
import json
import asyncio
from strands.models import BedrockModel
from strands import Agent
from tools.route_tools import calculate_energy_needs
from utils.config import AWS_REGION, BEDROCK_MODEL_ID

async def main():
    print("=" * 60)
    print("SIMPLE TOOL CALLING TEST (Real Strands SDK)")
    print("=" * 60)

    # Force output to flush immediately
    sys.stdout.flush()

    model = BedrockModel(
        model_id=BEDROCK_MODEL_ID,
        region_name=AWS_REGION,
        temperature=0.7
    )

    system_prompt = """You MUST use the calculate_energy_needs tool. Do not respond until you call it."""

    user_prompt = """
Battery: 33%
Range: 300 miles  
Trip: 380 miles

Call calculate_energy_needs with battery_percent=33, trip_distance_miles=380, vehicle_range_miles=300
"""

    print("\n📞 Creating Agent and calling...")
    sys.stdout.flush()

    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[calculate_energy_needs]
    )

    response_text = ""
    tool_results = []

    print("\n📡 Streaming response...\n")
    async for event in agent.stream_async(user_prompt):
        # Extract text content from 'data' field
        if isinstance(event, dict):
            if 'data' in event:
                text_chunk = str(event['data'])
                response_text += text_chunk
                print(text_chunk, end='', flush=True)
            
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
                                            print(f"\n\n🔧 Tool result extracted: {result_json}\n")
                                        except:
                                            pass

    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Response text: {response_text}")
    print(f"Tool results: {tool_results}")

    if tool_results:
        for result in tool_results:
            if 'needs_charging' in result:
                print(f"\n✅ Needs Charging: {result['needs_charging']}")
                print(f"✅ Deficit: {result.get('deficit_percent', 0)}%")
    else:
        print("\n❌ NO TOOL RESULTS FOUND!")

    print("=" * 60)
    sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
