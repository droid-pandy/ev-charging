from strands.tools import tool
import json

@tool
def calculate_energy_needs(battery_percent: int, trip_distance_miles: int, vehicle_range_miles: int, weather_temp_f: int = 70) -> str:
    """Calculate energy requirements for a trip considering weather"""
    temp_factor = 1.0 if 50 <= weather_temp_f <= 80 else 1.15
    required_percent = (trip_distance_miles / vehicle_range_miles) * 100 * temp_factor
    buffer = 20
    
    result = {
        "current_battery": battery_percent,
        "required_battery": round(required_percent + buffer, 1),
        "needs_charging": battery_percent < required_percent + buffer,
        "deficit_percent": max(0, round(required_percent + buffer - battery_percent, 1)),
        "charging_strategy": "en-route" if battery_percent > 30 else "pre-trip"
    }
    
    return json.dumps(result)

@tool
def get_route_info(origin: str, destination: str) -> str:
    """Get route information including distance and duration"""
    result = {
        "distance_miles": 280,
        "duration_hours": 4.5,
        "route": "I-5 South",
        "traffic_delay_min": 15
    }
    
    return json.dumps(result)
