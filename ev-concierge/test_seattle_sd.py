#!/usr/bin/env python3
"""
Test Seattle to San Diego route
"""

from tools.charging_tools import search_chargers
from utils.location_coords import get_coordinates, calculate_midpoint
import json

print("=" * 70)
print("Testing Seattle → San Diego Route")
print("=" * 70)

origin = "Seattle, WA"
destination = "San Diego, CA"

origin_coords = get_coordinates(origin)
dest_coords = get_coordinates(destination)
midpoint = calculate_midpoint(origin_coords, dest_coords)

print(f"\n🗺️  Route: {origin} → {destination}")
print(f"   Origin coords: {origin_coords}")
print(f"   Destination coords: {dest_coords}")
print(f"   Midpoint: {midpoint}")
print(f"   (Midpoint should be in Northern California)")

result = search_chargers(origin, destination, min_power_kw=150)
stations = json.loads(result)

print(f"\n✅ Found {len(stations)} charging stations:\n")

for i, station in enumerate(stations[:8], 1):
    print(f"{i}. {station['network']} - {station['location']}")
    print(f"   Lat/Lon: ({station['latitude']}, {station['longitude']})")
    print()

print("=" * 70)
print("ANALYSIS:")
print("=" * 70)

# Check if stations are reasonable for the route
# Seattle to San Diego goes through Oregon and California (I-5 corridor)
# Should NOT go through Nevada unless taking a detour

nevada_stations = [s for s in stations if ', NV' in s.get('location', '')]
california_stations = [s for s in stations if ', CA' in s.get('location', '')]
oregon_stations = [s for s in stations if ', OR' in s.get('location', '')]

print(f"\nStations by state:")
print(f"   Oregon: {len(oregon_stations)}")
print(f"   California: {len(california_stations)}")
print(f"   Nevada: {len(nevada_stations)}")

if nevada_stations:
    print(f"\n⚠️  Nevada stations found:")
    for s in nevada_stations[:3]:
        print(f"   - {s['location']}")
    print(f"\n   NOTE: Seattle → San Diego typically follows I-5 (through OR and CA)")
    print(f"   Nevada stations suggest the bounding box is too wide.")

print("\n" + "=" * 70)
