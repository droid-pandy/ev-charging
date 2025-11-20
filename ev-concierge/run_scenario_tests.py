#!/usr/bin/env python3
"""
Run EV Concierge with different test scenarios
"""
import sys
from test_scenarios import SCENARIOS, list_scenarios
from agents.coordinator import CoordinatorAgent

def run_scenario(scenario_name: str, verbose: bool = True):
    """Run a specific scenario through the coordinator"""
    
    if scenario_name not in SCENARIOS:
        print(f"❌ Scenario '{scenario_name}' not found")
        list_scenarios()
        return False
    
    scenario = SCENARIOS[scenario_name]
    
    if verbose:
        print(f"\n{'=' * 60}")
        print(f"🧪 Testing Scenario: {scenario['name']}")
        print(f"{'=' * 60}")
        print(f"Description: {scenario['description']}")
        print(f"\n📊 Input:")
        print(f"   Battery: {scenario['vehicle']['battery_percent']}%")
        print(f"   Range: {scenario['vehicle']['range_miles']} miles")
        print(f"   Distance: {scenario['trip']['distance_miles']} miles")
        print(f"   Route: {scenario['trip']['origin']} → {scenario['trip']['destination']}")
    
    # Initialize coordinator
    coordinator = CoordinatorAgent()
    
    # Prepare preferences
    preferences = scenario.get('preferences', {
        "auto_order_coffee": True,
        "favorite_drink": "Large Latte",
        "wallet_id": "WALLET-TEST-123"
    })
    
    # Run orchestration
    try:
        if verbose:
            print(f"\n🤖 Running agents...")
        
        result = coordinator.orchestrate(
            vehicle_data=scenario['vehicle'],
            trip_data=scenario['trip'],
            user_prefs=preferences
        )
        
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"📋 RESULTS:")
            print(f"{'=' * 60}")
            print(f"\n{result['summary']}\n")
        
        # Validate against expected results
        expected = scenario.get('expected', {})
        validation_passed = True
        
        if verbose:
            print(f"🔍 Validation:")
        
        # Check if charging was correctly identified
        if 'needs_charging' in expected:
            energy_analysis = result.get('energy_analysis')
            if energy_analysis:
                actual_needs_charging = energy_analysis.get('needs_charging', False)
                expected_needs_charging = expected['needs_charging']
                
                if actual_needs_charging == expected_needs_charging:
                    if verbose:
                        print(f"   ✅ Charging need correctly identified: {actual_needs_charging}")
                else:
                    if verbose:
                        print(f"   ❌ Charging need mismatch: expected {expected_needs_charging}, got {actual_needs_charging}")
                    validation_passed = False
            else:
                # Check in trip_plan results
                trip_results = result.get('results', {}).get('trip_plan', {}).get('tool_results', [])
                for tool_result in trip_results:
                    if isinstance(tool_result, dict) and 'needs_charging' in tool_result:
                        actual_needs_charging = tool_result['needs_charging']
                        expected_needs_charging = expected['needs_charging']
                        
                        if actual_needs_charging == expected_needs_charging:
                            if verbose:
                                print(f"   ✅ Charging need correctly identified: {actual_needs_charging}")
                        else:
                            if verbose:
                                print(f"   ❌ Charging need mismatch: expected {expected_needs_charging}, got {actual_needs_charging}")
                            validation_passed = False
                        break
        
        # Check charging stops
        if 'charging_stops' in expected and result.get('results', {}).get('charging'):
            charging_results = result['results']['charging'].get('tool_results', [])
            actual_stops = len([r for r in charging_results if isinstance(r, dict) and 'reservation_id' in r])
            expected_stops = expected['charging_stops']
            
            if actual_stops >= expected_stops:
                if verbose:
                    print(f"   ✅ Charging stops: {actual_stops} (expected at least {expected_stops})")
            else:
                if verbose:
                    print(f"   ⚠️  Charging stops: {actual_stops} (expected {expected_stops})")
        
        # Check amenities
        if expected.get('amenities_ordered') and result.get('results', {}).get('amenities'):
            amenities_results = result['results']['amenities'].get('tool_results', [])
            has_orders = any(isinstance(r, dict) and 'order_id' in r for r in amenities_results)
            
            if has_orders:
                if verbose:
                    print(f"   ✅ Amenities ordered")
            else:
                if verbose:
                    print(f"   ⚠️  No amenities ordered")
        
        if verbose:
            print(f"\n{'=' * 60}")
            if validation_passed:
                print(f"✅ Scenario PASSED")
            else:
                print(f"⚠️  Scenario completed with warnings")
            print(f"{'=' * 60}\n")
        
        return validation_passed
        
    except Exception as e:
        print(f"\n❌ Error running scenario: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_all_scenarios():
    """Run all test scenarios"""
    print("\n🚀 Running All Test Scenarios")
    print("=" * 60)
    
    results = {}
    for scenario_name in SCENARIOS.keys():
        passed = run_scenario(scenario_name, verbose=True)
        results[scenario_name] = passed
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for scenario_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {scenario_name}")
    
    print(f"\n{passed_count}/{total_count} scenarios passed")
    print("=" * 60 + "\n")
    
    return passed_count == total_count

if __name__ == "__main__":
    if len(sys.argv) > 1:
        scenario_name = sys.argv[1]
        if scenario_name == "--list":
            list_scenarios()
        elif scenario_name == "--all":
            run_all_scenarios()
        else:
            run_scenario(scenario_name)
    else:
        print("\nUsage:")
        print("  python run_scenario_tests.py <scenario_name>")
        print("  python run_scenario_tests.py --list")
        print("  python run_scenario_tests.py --all")
        print("\nExample:")
        print("  python run_scenario_tests.py one_charging_stop")
        list_scenarios()
