from strands import Strands
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.payment_tools import process_payment, get_payment_history

class PaymentAgent:
    def __init__(self):
        self.strands = Strands(
            model_id=BEDROCK_MODEL_ID,
            region=AWS_REGION
        )
    
    def process_payments(self, transactions: list, wallet_id: str) -> dict:
        if not transactions:
            return {"payments": None, "message": "No payments to process"}
        
        system_prompt = """You are a payment specialist. Process all transactions securely 
and provide a summary."""
        
        user_prompt = f"""
Transactions to process: {transactions}
Wallet ID: {wallet_id}

Process all payments and provide confirmation."""
        
        response = self.strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=[process_payment, get_payment_history],
            max_iterations=5
        )
        
        return {
            "payments": response.final_response,
            "tool_results": [c.result for c in response.tool_calls] if response.tool_calls else []
        }
