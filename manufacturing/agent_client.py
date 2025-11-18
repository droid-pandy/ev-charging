"""
Agent client for communicating with agent service
"""
import json
import httpx
import random
import string
import logging

logger = logging.getLogger(__name__)

def generate_session_id():
    """Generate a random session ID"""
    return ''.join(random.choices(string.ascii_lowercase, k=40))

class AgentClient:
    """Client for interacting with the agent service"""
    
    def __init__(self, url: str, jwt_token: str = "dummy-token"):
        self.url = url
        self.user_token = jwt_token
        self.session_id = generate_session_id()

    def normalize_event(self, raw: str) -> dict:
        """Normalize event data from server"""
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, str):
                return {"raw": parsed}
        except:
            return {"raw": raw}
        return {"raw": raw}

    async def stream_async(self, prompt: str):
        """Stream responses from the agent"""
        headers = {
            "Authorization": f"Bearer {self.user_token}",
            "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": self.session_id,
            "Content-Type": "application/json"
        }
        payload = {"prompt": prompt}
        
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                async with client.stream("POST", self.url, headers=headers, json=payload) as response:
                    # Handle both SSE format and regular JSON response
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            # SSE format
                            data = line[6:]
                            yield self.normalize_event(data)
                        elif line.startswith("{\"error\""):
                            # Error response
                            yield self.normalize_event(line)
                        elif line.strip():
                            # Regular JSON response or plain text
                            yield self.normalize_event(line)
        except Exception as e:
            logger.exception("Error in async streaming")
            yield {"error": str(e)}
