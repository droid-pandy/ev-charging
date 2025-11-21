#!/usr/bin/env python3
"""
Test reachability-aware charging station search
"""

from tools.charging_tools import search_chargers
from utils.location_coords import get_coordinates, calculate_distance_km
import json

print("=" * 70)
print("Testing Reachability-Aware Station Search")
print("=" * 70)

# Scenario: Seattle to San Diego with 45% battery (135 miles range)
origin = "Seattle, WA"
destination = "San Diego, CA"
battery_percent = 45
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
    station_coords = (station['latitude'], station['longitude'])
    distance_km = calculate_distance_km(origin_coords, station_coords)
    distance_miles = distance_km / 1.60934
    
    print(f"{i}. {station['network']} - {station['location']}")
    print(f"   Distance from Seattle: {distance_miles:.0f} miles ({distance_km:.0f} km)")
    print(f"   Power: {station['power_kw']} kW")
    print()

print("=" * 70)
if stations:
    first_station = stations[0]
    first_coords = (first_station['latitude'], first_station['longitude'])
    first_distance_miles = calculate_distance_km(origin_coords, first_coords) / 1.60934
    
    print("VERIFICATION:")
    print(f"✅ First station is {first_distance_miles:.0f} miles away")
    print(f"✅ Within {current_range} mile range: {first_distance_miles <= current_range}")
    print(f"✅ Within safety buffer ({int(current_range * 0.8)} mi): {first_distance_miles <= current_range * 0.8}")
else:
    print("⚠️  No reachable stations found - may need to charge before starting trip")
print("=" * 70)
