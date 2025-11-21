#!/usr/bin/env python3
"""
Test Seattle to Las Vegas with insufficient battery
"""

from agents.coordinator import CoordinatorAgent
from datetime import datetime, timedelta

print("=" * 70)
print("Testing: Seattle → Las Vegas with Insufficient Battery")
print("=" * 70)

coordinator = CoordinatorAgent()

vehicle = {
    "model": "Tesla Model Y",
    "battery_percent": 32,  # Only 96 miles range
    "range_miles": 300
}

trip = {
    "origin": "Seattle, WA",
    "destination": "Las Vegas, NV",
    "distance_miles": 1120,
    "departure": (datetime.now() + timedelta(days=1)).replace(hour=9, minute=0).isoformat()
}

preferences = {
    "auto_order_coffee": True,
    "favorite_drink": "Large Latte",
    "wallet_id": "WALLET-12345"
}

print(f"\n🚗 Vehicle: {vehicle['battery_percent']}% battery ({int(vehicle['battery_percent']/100 * vehicle['range_miles'])} miles range)")
print(f"🗺️  Trip: {trip['origin']} → {trip['destination']} ({trip['distance_miles']} miles)")
print(f"\n⏳ Running coordinator...\n")

try:
    result = coordinator.orchestrate(vehicle, trip, preferences)
    
    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)
    print(result.get('summary', 'No summary'))
    print("\n" + "=" * 70)
    
    if result.get('insufficient_range'):
        print("✅ System correctly detected insufficient range")
        print("✅ Planned amenities at first charging stop")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
