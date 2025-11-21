#!/usr/bin/env python3
"""
Test insufficient range scenario
"""

from tools.charging_tools import search_chargers
import json

print("=" * 70)
print("Testing Insufficient Range Scenario")
print("=" * 70)

# Scenario: LA to SF with 35% battery (105 miles range) - NOT ENOUGH
origin = "Los Angeles, CA"
destination = "San Francisco, CA"
battery_percent = 35
vehicle_range = 300
current_range = int((battery_percent / 100) * vehicle_range)

print(f"\n🚗 Trip: {origin} → {destination}")
print(f"   Battery: {battery_percent}% ({current_range} miles range)")

# Search for stations
result_json = search_chargers(origin, destination, min_power_kw=150, current_range_miles=current_range)
result = json.loads(result_json)

print(f"\n📊 Result:\n")

if isinstance(result, dict) and 'error' in result:
    print(f"❌ Error: {result['error']}")
    print(f"\n💡 Message:")
    print(f"   {result['message']}")
    print(f"\n🔌 Recommended Action:")
    print(f"   {result['recommended_action']}")
    
    if result.get('stations_if_fully_charged'):
        print(f"\n✅ Stations you COULD reach if fully charged:")
        for i, station in enumerate(result['stations_if_fully_charged'], 1):
            print(f"\n   {i}. {station['network']} - {station['location']}")
            print(f"      Power: {station['power_kw']} kW")
            print(f"      Address: {station['address']}")
else:
    print(f"✅ Found {len(result)} reachable stations")
    for i, station in enumerate(result[:3], 1):
        print(f"\n   {i}. {station['network']} - {station['location']}")

print("\n" + "=" * 70)
