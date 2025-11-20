from datetime import datetime
from strands.tools import tool
from utils.config import USE_MOCK_DATA
from utils.mock_data import get_mock_chargers
import json

@tool
def search_chargers(route: str, destination: str, min_power_kw: int = 150) -> str:
    """Search for available EV chargers along route"""
    if USE_MOCK_DATA:
        result = get_mock_chargers(route, destination)
    else:
        result = []
    return json.dumps(result)

@tool
def reserve_charging_slot(charger_id: str, time_slot: str, duration_min: int = 30) -> str:
    """Reserve a specific charging slot at a charger"""
    result = {
        "reservation_id": f"RES-{charger_id}-{int(datetime.now().timestamp())}",
        "charger_id": charger_id,
        "time_slot": time_slot,
        "duration_min": duration_min,
        "status": "confirmed",
        "cancellation_deadline": "15 minutes before slot"
    }
    return json.dumps(result)

@tool
def check_charger_status(charger_id: str) -> str:
    """Check real-time status of a charger"""
    result = {
        "charger_id": charger_id,
        "status": "online",
        "available_ports": 4,
        "current_wait_time_min": 0
    }
    return json.dumps(result)

@tool
def cancel_reservation(reservation_id: str) -> str:
    """Cancel a charging reservation"""
    result = {
        "reservation_id": reservation_id,
        "status": "cancelled",
        "refund_status": "full_refund"
    }
    return json.dumps(result)
