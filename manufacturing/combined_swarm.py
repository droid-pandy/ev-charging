"""
Combined Strands Swarm implementation for GenAI Production Optimizer
"""
import boto3
import logging
from typing import Dict, Any
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent import Swarm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Bedrock model instance
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    temperature=0.3,
    region_name="us-west-2"
)

@tool
def query_parts_inventory(part_number: str = None, location: str = None) -> str:
    """Query parts inventory levels from DynamoDB"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('PartsInventory')
        
        if part_number:
            response = table.get_item(Key={'PartNumber': part_number})
            if 'Item' in response:
                item = response['Item']
                return f"Part {part_number}: {item.get('Quantity', 0)} units available at {item.get('Location', 'Unknown')}"
            return f"Part {part_number} not found in inventory"
        
        # Scan for all parts if no specific part requested
        response = table.scan(Limit=10)
        items = response.get('Items', [])
        if not items:
            return "No inventory data found"
        
        result = "Current inventory levels:\n"
        for item in items:
            result += f"- {item.get('PartNumber', 'Unknown')}: {item.get('Quantity', 0)} units\n"
        return result
    except Exception as e:
        return f"Error querying inventory: {str(e)}"

@tool
def query_parts_delivery(part_number: str = None, delivery_date: str = None) -> str:
    """Query parts delivery schedules from DynamoDB"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('PartsDelivery')
        
        if part_number:
            response = table.get_item(Key={'PartNumber': part_number})
            if 'Item' in response:
                item = response['Item']
                return f"Part {part_number} delivery: {item.get('DeliveryDate', 'Unknown')} from {item.get('Supplier', 'Unknown')}"
            return f"No delivery scheduled for part {part_number}"
        
        response = table.scan(Limit=10)
        items = response.get('Items', [])
        if not items:
            return "No delivery data found"
        
        result = "Upcoming deliveries:\n"
        for item in items:
            result += f"- {item.get('PartNumber', 'Unknown')}: {item.get('DeliveryDate', 'Unknown')}\n"
        return result
    except Exception as e:
        return f"Error querying deliveries: {str(e)}"

@tool
def query_product_bom(product_id: str) -> str:
    """Query bill of materials for a specific product"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('ProductBOM')
        
        response = table.get_item(Key={'ProductID': product_id})
        if 'Item' in response:
            item = response['Item']
            bom = item.get('BOM', [])
            result = f"Bill of Materials for {product_id}:\n"
            for component in bom:
                result += f"- {component.get('PartNumber', 'Unknown')}: {component.get('Quantity', 0)} units\n"
            return result
        return f"No BOM found for product {product_id}"
    except Exception as e:
        return f"Error querying BOM: {str(e)}"

@tool
def query_production_schedule(product_id: str = None, date: str = None) -> str:
    """Query production schedules"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('ProductionSchedule')
        
        if product_id:
            response = table.get_item(Key={'ProductID': product_id})
            if 'Item' in response:
                item = response['Item']
                return f"Production schedule for {product_id}: {item.get('ScheduledDate', 'Unknown')} - {item.get('Quantity', 0)} units"
            return f"No production scheduled for product {product_id}"
        
        response = table.scan(Limit=10)
        items = response.get('Items', [])
        if not items:
            return "No production schedule data found"
        
        result = "Production schedule:\n"
        for item in items:
            result += f"- {item.get('ProductID', 'Unknown')}: {item.get('ScheduledDate', 'Unknown')} - {item.get('Quantity', 0)} units\n"
        return result
    except Exception as e:
        return f"Error querying production schedule: {str(e)}"

# Create specialized agents
parts_inventory_agent = Agent(
    name="parts_inventory_specialist",
    model=bedrock_model,
    system_prompt="""You are a Parts Inventory Specialist. Your expertise is in managing and tracking parts inventory levels, stock locations, and availability. 
    
    Use the query_parts_inventory tool to get current inventory data. Provide clear, actionable information about part availability, stock levels, and locations.
    
    When you have completed your analysis, hand off to another specialist if the user needs information outside your domain.""",
    tools=[query_parts_inventory]
)

parts_delivery_agent = Agent(
    name="parts_delivery_specialist", 
    model=bedrock_model,
    system_prompt="""You are a Parts Delivery Specialist. Your expertise is in tracking delivery schedules, supplier information, and logistics coordination.
    
    Use the query_parts_delivery tool to get delivery schedule data. Provide clear information about delivery dates, suppliers, and logistics status.
    
    When you have completed your analysis, hand off to another specialist if the user needs information outside your domain.""",
    tools=[query_parts_delivery]
)

product_bom_agent = Agent(
    name="product_bom_specialist",
    model=bedrock_model, 
    system_prompt="""You are a Product BOM (Bill of Materials) Specialist. Your expertise is in product composition, component requirements, and material specifications.
    
    Use the query_product_bom tool to get bill of materials data. Provide detailed information about product components, quantities, and specifications.
    
    When you have completed your analysis, hand off to another specialist if the user needs information outside your domain.""",
    tools=[query_product_bom]
)

production_schedule_agent = Agent(
    name="production_schedule_specialist",
    model=bedrock_model,
    system_prompt="""You are a Production Schedule Specialist. Your expertise is in manufacturing schedules, production planning, and capacity management.
    
    Use the query_production_schedule tool to get production schedule data. Provide clear information about production dates, quantities, and scheduling.
    
    When you have completed your analysis, hand off to another specialist if the user needs information outside your domain.""",
    tools=[query_production_schedule]
)

supervisor_agent = Agent(
    name="supervisor",
    model=bedrock_model,
    system_prompt="""You are the Production Supervisor coordinating a team of manufacturing specialists. Your role is to:

1. Analyze user queries and determine which specialists can help
2. Coordinate between specialists when complex queries require multiple domains
3. Synthesize information from multiple specialists into comprehensive responses
4. Provide final answers that integrate insights from the specialist team

Available specialists:
- parts_inventory_specialist: Inventory levels and stock information
- parts_delivery_specialist: Delivery schedules and logistics
- product_bom_specialist: Bill of materials and product composition  
- production_schedule_specialist: Production planning and scheduling

Start by analyzing the user's query and hand off to the most appropriate specialist. If multiple domains are involved, coordinate between specialists to gather all needed information before providing your final response.""",
    tools=[]  # Supervisor doesn't need tools, just coordinates
)

# Create the swarm with supervisor as entry point
production_swarm = Swarm(
    [supervisor_agent, parts_inventory_agent, parts_delivery_agent, product_bom_agent, production_schedule_agent],
    entry_point=supervisor_agent,
    max_handoffs=15,
    max_iterations=20,
    execution_timeout=300.0,
    node_timeout=60.0
)

# For Bedrock AgentCore integration
from bedrock_agentcore.runtime import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.entrypoint
def agent_invocation(payload, context):
    """Handler for agent invocation from Bedrock AgentCore"""
    user_message = payload.get("prompt", "How can I help optimize your production?")
    
    try:
        # Process the query through the swarm
        result = production_swarm(user_message)
        
        # Extract the final response
        response_text = str(result.result) if hasattr(result, 'result') else str(result)
        
        return {
            "result": response_text
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {
            "result": f"Error processing query: {str(e)}"
        }

async def process_query(query: str) -> Dict[str, Any]:
    """Process a user query through the production swarm"""
    try:
        result = await production_swarm.invoke_async(query)
        
        # Get the final response from the last agent's result
        response_text = ""
        if result.node_history:
            last_node_id = result.node_history[-1].node_id
            if last_node_id in result.results:
                response_text = str(result.results[last_node_id].result)
            else:
                response_text = "No response available"
        else:
            response_text = "No agents executed"
        
        return {
            "status": result.status,
            "response": response_text,
            "agents_involved": [node.node_id for node in result.node_history],
            "execution_time": result.execution_time,
            "token_usage": result.accumulated_usage
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {
            "status": "FAILED",
            "response": f"Error processing query: {str(e)}",
            "agents_involved": [],
            "execution_time": 0,
            "token_usage": {}
        }

if __name__ == "__main__":
    app.run()
