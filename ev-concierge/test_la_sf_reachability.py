#!/usr/bin/env python3
"""
Test LA to SF with reachability
"""

from tools.charging_tools import search_chargers
from utils.location_coords import get_coordinates, calculate_distance_km
import json

print("=" * 70)
print("Testing LA → SF with Reachability")
print("=" * 70)

# Scenario: LA to SF with 35% battery (105 miles range)
origin = "Los Angeles, CA"
destination = "San Francisco, CA"
battery_percent = 35
vehicle_range = 300
current_range = int((battery_percent / 100) * vehicle_range)

print(f"\n🚗 Trip: {origin} → {destination}")
print(f"   Battery: {battery_percent}% ({current_range} miles range)")
print(f"   Safety buffer: 80% of range = {int(current_range * 0.8)} miles")

# Search for stations
result = search_chargers(origin, destination, min_power_kw=150, current_range_miles=current_range)
stations = json.loads(result)

print(f"\n✅ Found {len(stations)} REACHABLE charging stations:\n")

origin_coords = get_coordinates(origin)

for i, station in enumerate(stations[:5], 1):
    if 'latitude' in station:
        station_coords = (station['latitude'], station['longitude'])
        distance_km = calculate_distance_km(origin_coords, station_coords)
        distance_miles = distance_km / 1.60934
        
        print(f"{i}. {station['network']} - {station['location']}")
        print(f"   Distance from LA: {distance_miles:.0f} miles ({distance_km:.0f} km)")
        print(f"   Power: {station['power_kw']} kW")
        print()
    else:
        # Mock data
        print(f"{i}. {station['network']} - {station['location']}")
        print(f"   Power: {station['power_kw']} kW")
        print(f"   (Mock data - no coordinates)")
        print()

print("=" * 70)
