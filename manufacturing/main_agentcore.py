"""
Amazon Bedrock AgentCore deployment for GenAI Production Optimizer
"""
import os
import logging
from combined_swarm import production_swarm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agentcore")

# Integrate with Bedrock AgentCore
from bedrock_agentcore.runtime import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.entrypoint
def agent_invocation(payload, context):
    """Handler for agent invocation"""
    user_message = payload.get("prompt", "How can I help optimize your production?")

    # Pass the message to the swarm
    result = production_swarm(user_message)

    # Extract the final response from the swarm result
    response_text = ""
    if hasattr(result, 'node_history') and result.node_history:
        # Get the last agent that executed
        last_node_id = result.node_history[-1].node_id
        if hasattr(result, 'results') and last_node_id in result.results:
            agent_result = result.results[last_node_id].result
            if hasattr(agent_result, 'message') and agent_result.message:
                # Extract text content from the message
                content_parts = []
                for item in agent_result.message.get('content', []):
                    if isinstance(item, dict) and 'text' in item:
                        content_parts.append(item['text'])
                response_text = "".join(content_parts)
    
    return {
        "result": {
            "message": {
                "content": [{"text": response_text}]
            }
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Manufacturing Agent Service on port {port}")
    logger.info("Agent service ready to accept requests")
    app.run(host="0.0.0.0", port=port)
