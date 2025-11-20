from datetime import datetime
from strands import Tool

@Tool
def process_payment(amount: float, wallet_id: str, merchant: str, description: str) -> dict:
    """Process autonomous payment using digital wallet"""
    return {
        "transaction_id": f"TXN-{int(datetime.now().timestamp())}",
        "amount": amount,
        "wallet_id": wallet_id,
        "merchant": merchant,
        "description": description,
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }

@Tool
def get_payment_history(wallet_id: str, limit: int = 10) -> list:
    """Get recent payment history"""
    return [
        {"date": "2025-11-19", "merchant": "EVgo", "amount": 18.50},
        {"date": "2025-11-18", "merchant": "Starbucks", "amount": 6.75}
    ]
