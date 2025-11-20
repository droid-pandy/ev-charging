from strands.models import BedrockModel
from strands import Agent
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.payment_tools import process_payment, get_payment_history
import json
import asyncio

class PaymentAgent:
    def __init__(self):
        self.model = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            temperature=0.7
        )
    
    def process_payments(self, transactions: list, wallet_id: str) -> dict:
        """Synchronous wrapper for async process_payments"""
        if not transactions:
            return {"payments": None, "message": "No payments to process"}
        
        return asyncio.run(self.process_payments_async(transactions, wallet_id))
    
    async def process_payments_async(self, transactions: list, wallet_id: str) -> dict:
        system_prompt = """You are a payment specialist. Process all transactions securely 
and provide a summary."""
        
        user_prompt = f"""
Transactions to process: {transactions}
Wallet ID: {wallet_id}

Process all payments and provide confirmation."""
        
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=[process_payment, get_payment_history]
        )
        
        response_text = ""
        tool_results = []
        
        try:
            async for event in agent.stream_async(user_prompt):
                if isinstance(event, dict):
                    if 'data' in event:
                        response_text += str(event['data'])
                    
                    # Extract tool results from message
                    if 'message' in event:
                        message = event['message']
                        if isinstance(message, dict) and 'content' in message:
                            for content_block in message['content']:
                                if isinstance(content_block, dict) and 'toolResult' in content_block:
                                    tool_result = content_block['toolResult']
                                    if 'content' in tool_result:
                                        for content_item in tool_result['content']:
                                            if 'text' in content_item:
                                                try:
                                                    result_json = json.loads(content_item['text'])
                                                    tool_results.append(result_json)
                                                except:
                                                    pass
        except Exception as e:
            response_text = f"Error: {str(e)}"
        
        return {
            "payments": response_text,
            "tool_results": tool_results
        }
