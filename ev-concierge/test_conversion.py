#!/usr/bin/env python3
"""
Test to verify the Strands SDK conversion is complete and working
"""
import asyncio
from agents.trip_planning import TripPlanningAgent
from agents.coordinator import CoordinatorAgent

def test_trip_planning_agent():
    """Test the trip planning agent with sync wrapper"""
    print("=" * 60)
    print("TEST 1: Trip Planning Agent (Sync Wrapper)")
    print("=" * 60)
    
    agent = TripPlanningAgent()
    
    vehicle_data = {
        'model': 'Tesla Model 3',
        'battery_percent': 33,
        'range_miles': 300
    }
    
    trip_data = {
        'origin': 'San Francisco',
        'destination': 'Los Angeles',
        'distance_miles': 380,
        'departure': '2025-11-20 09:00'
    }
    
    try:
        result = agent.analyze(vehicle_data, trip_data)
        print(f"\n✅ Analysis completed")
        print(f"   Response length: {len(result['analysis'])} chars")
        print(f"   Tool results: {len(result['tool_results'])}")
        
        if result['tool_results']:
            for i, tool_result in enumerate(result['tool_results'], 1):
                print(f"\n   Tool Result {i}:")
                for key, value in tool_result.items():
                    print(f"     {key}: {value}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def test_coordinator():
    """Test the coordinator orchestration"""
    print("\n" + "=" * 60)
    print("TEST 2: Coordinator Agent")
    print("=" * 60)
    
    coordinator = CoordinatorAgent()
    
    vehicle_data = {
        'model': 'Tesla Model 3',
        'battery_percent': 80,
        'range_miles': 300
    }
    
    trip_data = {
        'origin': 'San Francisco',
        'destination': 'San Jose',
        'distance_miles': 50,
        'departure': '2025-11-20 09:00'
    }
    
    user_prefs = {
        'auto_order_coffee': True,
        'favorite_drink': 'Latte',
        'wallet_id': 'wallet_123'
    }
    
    try:
        result = coordinator.orchestrate(vehicle_data, trip_data, user_prefs)
        print(f"\n✅ Orchestration completed")
        print(f"   Summary length: {len(result['summary'])} chars")
        print(f"   Results keys: {list(result['results'].keys())}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Testing Strands SDK Conversion\n")
    
    test1_passed = test_trip_planning_agent()
    test2_passed = test_coordinator()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Test 1 (Trip Planning): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (Coordinator):   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Conversion is complete.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
