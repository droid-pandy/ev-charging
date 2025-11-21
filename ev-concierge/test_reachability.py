#!/usr/bin/env python3
"""
Test if recommended stations are reachable with current battery
"""

from utils.location_coords import get_coordinates, calculate_distance_km

print("=" * 70)
print("Testing Station Reachability")
print("=" * 70)

# Scenario: Seattle to San Diego with 45% battery (135 miles range)
origin = "Seattle, WA"
current_range_miles = 135  # 45% of 300 miles
current_range_km = current_range_miles * 1.60934

origin_coords = get_coordinates(origin)

# Stations that were recommended
stations = [
    ("Lovelock, NV", (40.179476, -118.472135)),
    ("Reno, NV", (39.529389, -119.815842)),
    ("Susanville, CA", (40.43043670245319, -120.6578957019019)),
]

print(f"\n🚗 Starting from: {origin}")
print(f"   Current range: {current_range_miles} miles ({current_range_km:.0f} km)")
print(f"\n📍 Checking if stations are reachable:\n")

for name, coords in stations:
    distance_km = calculate_distance_km(origin_coords, coords)
    distance_miles = distance_km / 1.60934
    reachable = distance_km <= current_range_km
    
    status = "✅ REACHABLE" if reachable else "❌ TOO FAR"
    print(f"{name}:")
    print(f"   Distance: {distance_miles:.0f} miles ({distance_km:.0f} km)")
    print(f"   {status}")
    print()

print("=" * 70)
print("PROBLEM IDENTIFIED:")
print("=" * 70)
print("The system is recommending stations that are UNREACHABLE with")
print("the current battery level. It should recommend stations within")
print("the current range, or calculate where you need to stop first.")
print("=" * 70)
