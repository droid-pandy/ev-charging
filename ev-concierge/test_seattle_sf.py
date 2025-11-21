#!/usr/bin/env python3
"""
Test Seattle to San Francisco route
"""

from tools.charging_tools import search_chargers
import json

print("=" * 70)
print("Testing Seattle → San Francisco Route")
print("=" * 70)

print("\n🗺️  Route: Seattle, WA → San Francisco, CA")

result = search_chargers("Seattle, WA", "San Francisco, CA", min_power_kw=150)
stations = json.loads(result)

print(f"\n✅ Found {len(stations)} charging stations:\n")

for i, station in enumerate(stations[:5], 1):
    print(f"{i}. {station['network']} - {station['location']}")
    print(f"   Address: {station['address']}")
    print(f"   Power: {station['power_kw']} kW")
    print(f"   ID: {station['id']}")
    print()

print("=" * 70)

# Check if any are Tejon Ranch (which is near LA, not Seattle-SF route)
tejon_found = any('Tejon' in station.get('location', '') for station in stations)
if tejon_found:
    print("⚠️  WARNING: Tejon Ranch found - this is NOT on Seattle-SF route!")
    print("   This suggests mock data is being used.")
else:
    print("✅ No Tejon Ranch - using real route-based data!")

print("=" * 70)
