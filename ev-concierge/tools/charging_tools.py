from datetime import datetime
from strands import Tool
from utils.config import USE_MOCK_DATA
from utils.mock_data import get_mock_chargers

@Tool
def search_chargers(route: str, destination: str, min_power_kw: int = 150) -> list:
    """Search for available EV chargers along route"""
    if USE_MOCK_DATA:
        return get_mock_chargers(route, destination)
    # Real API integration here
    return []

@Tool
def reserve_charging_slot(charger_id: str, time_slot: str, duration_min: int = 30) -> dict:
    """Reserve a specific charging slot at a charger"""
    return {
        "reservation_id": f"RES-{charger_id}-{int(datetime.now().timestamp())}",
        "charger_id": charger_id,
        "time_slot": time_slot,
        "duration_min": duration_min,
        "status": "confirmed",
        "cancellation_deadline": "15 minutes before slot"
    }

@Tool
def check_charger_status(charger_id: str) -> dict:
    """Check real-time status of a charger"""
    return {
        "charger_id": charger_id,
        "status": "online",
        "available_ports": 4,
        "current_wait_time_min": 0
    }

@Tool
def cancel_reservation(reservation_id: str) -> dict:
    """Cancel a charging reservation"""
    return {
        "reservation_id": reservation_id,
        "status": "cancelled",
        "refund_status": "full_refund"
    }
