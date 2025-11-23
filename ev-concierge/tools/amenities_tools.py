from datetime import datetime
from strands.tools import tool
from utils.config import USE_MOCK_DATA
from utils.mock_data import get_mock_amenities, get_mock_menu
from catalog import get_item_price
import json

@tool
def check_nearby_amenities(location: str) -> str:
    """Check available restaurants and facilities near charging location"""
    # Always return mock amenities for demo purposes
    # In production, this would query Google Places API or similar
    result = get_mock_amenities(location)
    return json.dumps(result)

@tool
def get_restaurant_menu(restaurant_name: str) -> str:
    """Get menu items with prices from a restaurant"""
    # Always return mock menu for demo purposes
    # In production, this would query restaurant APIs
    result = get_mock_menu(restaurant_name)
    return json.dumps(result)

@tool
def place_food_order(restaurant: str, items: list, pickup_time: str) -> str:
    """Place a mobile order for food/drinks with accurate pricing from catalog"""
    total = 0.0
    
    # Calculate total using catalog prices
    for item in items:
        price = get_item_price(item)
        if price:
            total += price
        else:
            # Fallback pricing for items not in catalog
            item_lower = item.lower()
            if 'latte' in item_lower or 'cappuccino' in item_lower or 'mocha' in item_lower:
                total += 5.50
            elif 'coffee' in item_lower or 'tea' in item_lower or 'espresso' in item_lower:
                total += 3.50
            elif 'sandwich' in item_lower or 'burger' in item_lower:
                total += 8.00
            elif 'croissant' in item_lower or 'pastry' in item_lower:
                total += 4.50
            elif 'cookies' in item_lower or 'cookie' in item_lower:
                total += 3.00
            else:
                total += 6.00
    
    result = {
        "order_id": f"ORD-{int(datetime.now().timestamp())}",
        "restaurant": restaurant,
        "items": items,
        "total_usd": round(total, 2),
        "pickup_time": pickup_time,
        "status": "confirmed"
    }
    return json.dumps(result)
