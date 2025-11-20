from datetime import datetime
from strands import Tool
from utils.config import USE_MOCK_DATA
from utils.mock_data import get_mock_amenities, get_mock_menu

@Tool
def check_nearby_amenities(location: str) -> dict:
    """Check available restaurants and facilities near charging location"""
    if USE_MOCK_DATA:
        return get_mock_amenities(location)
    return {}

@Tool
def get_restaurant_menu(restaurant_name: str) -> list:
    """Get menu items from a restaurant"""
    if USE_MOCK_DATA:
        return get_mock_menu(restaurant_name)
    return []

@Tool
def place_food_order(restaurant: str, items: list, pickup_time: str) -> dict:
    """Place a mobile order for food/drinks"""
    total = 0
    for item in items:
        item_lower = item.lower()
        if 'cappuccino' in item_lower:
            total += 6.50
        elif 'croissant' in item_lower:
            total += 10.00
        elif 'coffee' in item_lower or 'latte' in item_lower:
            total += 5.50
        else:
            total += 8.00
    
    return {
        "order_id": f"ORD-{int(datetime.now().timestamp())}",
        "restaurant": restaurant,
        "items": items,
        "total_usd": round(total, 2),
        "pickup_time": pickup_time,
        "status": "confirmed"
    }
