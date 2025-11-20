from datetime import datetime
from strands.tools import tool
import json

@tool
def process_payment(amount: float, wallet_id: str, merchant: str, description: str) -> str:
    """Process autonomous payment using digital wallet"""
    result = {
        "transaction_id": f"TXN-{int(datetime.now().timestamp())}",
        "amount": amount,
        "wallet_id": wallet_id,
        "merchant": merchant,
        "description": description,
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }
    return json.dumps(result)

@tool
def get_payment_history(wallet_id: str, limit: int = 10) -> str:
    """Get recent payment history"""
    result = [
        {"date": "2025-11-19", "merchant": "EVgo", "amount": 18.50},
        {"date": "2025-11-18", "merchant": "Starbucks", "amount": 6.75}
    ]
    return json.dumps(result)
