#!/usr/bin/env python3
"""
Test script to verify Strands SDK tool calling is working
"""
from strands import Strands, Tool
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.route_tools import calculate_energy_needs

def test_basic_tool_calling():
    """Test that tools are actually being called"""
    print("🧪 Testing Strands SDK Tool Calling")
    print("=" * 60)
    
    # Initialize Strands
    strands = Strands(
        model_id=BEDROCK_MODEL_ID,
        region=AWS_REGION
    )
    
    # Test scenario: Low battery, long trip
    system_prompt = """You are a trip planning assistant. Use the calculate_energy_needs 
tool to determine if charging is needed for this trip."""
    
    user_prompt = """
Vehicle has 30% battery and 300 mile range.
Trip is 280 miles.
Weather is 70°F.

Calculate if charging is needed.
"""
    
    print("\n📋 Test Scenario:")
    print("   Battery: 30%")
    print("   Range: 300 miles")
    print("   Trip: 280 miles")
    print("   Expected: Charging NEEDED\n")
    
    # Run the agent
    print("🤖 Running agent with tool calling...\n")
    response = strands.run(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        tools=[calculate_energy_needs],
        max_iterations=3
    )
    
    # Check results
    print("=" * 60)
    print("📊 RESULTS:")
    print("=" * 60)
    
    print(f"\n✅ Tool Calls Made: {len(response.tool_calls)}")
    
    if response.tool_calls:
        for i, call in enumerate(response.tool_calls, 1):
            print(f"\n🔧 Tool Call #{i}:")
            print(f"   Name: {call.tool_name}")
            print(f"   Input: {call.input}")
            print(f"   Result: {call.result}")
            
            # Verify the tool was actually called
            if call.tool_name == "calculate_energy_needs":
                result = call.result
                if isinstance(result, dict):
                    needs_charging = result.get('needs_charging', False)
                    print(f"\n   ✅ Needs Charging: {needs_charging}")
                    print(f"   ✅ Deficit: {result.get('deficit_percent', 0)}%")
                    
                    if needs_charging:
                        print("\n   ✅ SUCCESS: Tool correctly identified charging needed!")
                    else:
                        print("\n   ❌ FAIL: Tool should have identified charging needed!")
    else:
        print("\n❌ FAIL: No tools were called!")
        print("   The Strands SDK is not executing tools properly.")
    
    print(f"\n💬 Final Response from Claude:")
    print(f"   {response.final_response}\n")
    
    print("=" * 60)
    
    return len(response.tool_calls) > 0

def test_multiple_scenarios():
    """Test different battery/distance scenarios"""
    print("\n\n🧪 Testing Multiple Scenarios")
    print("=" * 60)
    
    strands = Strands(
        model_id=BEDROCK_MODEL_ID,
        region=AWS_REGION
    )
    
    scenarios = [
        {
            "name": "High battery, short trip",
            "battery": 80,
            "range": 300,
            "distance": 100,
            "expected_charging": False
        },
        {
            "name": "Low battery, long trip",
            "battery": 25,
            "range": 300,
            "distance": 280,
            "expected_charging": True
        },
        {
            "name": "Medium battery, medium trip",
            "battery": 50,
            "range": 300,
            "distance": 150,
            "expected_charging": False
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"   Battery: {scenario['battery']}%")
        print(f"   Distance: {scenario['distance']} miles")
        print(f"   Expected: {'Charging needed' if scenario['expected_charging'] else 'No charging'}")
        
        system_prompt = "You are a trip planner. Use calculate_energy_needs to check if charging is needed."
        user_prompt = f"""
Battery: {scenario['battery']}%
Vehicle range: {scenario['range']} miles
Trip distance: {scenario['distance']} miles
Weather: 70°F

Should we charge?
"""
        
        response = strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=[calculate_energy_needs],
            max_iterations=2
        )
        
        if response.tool_calls:
            result = response.tool_calls[0].result
            actual_charging = result.get('needs_charging', False)
            
            if actual_charging == scenario['expected_charging']:
                print(f"   ✅ PASS: Got expected result")
                results.append(True)
            else:
                print(f"   ❌ FAIL: Expected {scenario['expected_charging']}, got {actual_charging}")
                results.append(False)
        else:
            print(f"   ❌ FAIL: No tool was called")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"📊 Overall: {sum(results)}/{len(results)} scenarios passed")
    print("=" * 60)
    
    return all(results)

if __name__ == "__main__":
    print("\n🚀 Starting Strands SDK Tool Calling Tests\n")
    
    # Test 1: Basic tool calling
    test1_passed = test_basic_tool_calling()
    
    # Test 2: Multiple scenarios
    if test1_passed:
        test2_passed = test_multiple_scenarios()
        
        if test1_passed and test2_passed:
            print("\n\n✅ ALL TESTS PASSED! Tool calling is working correctly.")
            print("   You can now run the full EV Concierge app.\n")
        else:
            print("\n\n⚠️  Some tests failed. Check the output above.\n")
    else:
        print("\n\n❌ Basic tool calling failed. Fix strands.py before proceeding.\n")
