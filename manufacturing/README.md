# GenAI Production Optimizer (GPO)

Multi-agent system for manufacturing operations using Strands framework with specialized agents for inventory, delivery, BOM, and production scheduling.

## Files

- `combined_swarm.py` - Main implementation with all agents and tools
- `main_agentcore.py` - Bedrock AgentCore deployment entry point
- `run_agent.sh` - Script to start the agent service
- `run_ui.sh` - Script to start the Streamlit UI
- Streamlit UI files (app.py, session_manager.py, chat_handler.py, agent_client.py)

## Quick Start

### Option 1: Run Agent Service Only
```bash
./run_agent.sh
```
The agent will be available at http://localhost:8080

### Option 2: Run with Streamlit UI
1. In one terminal, start the agent service:
   ```bash
   ./run_agent.sh
   ```

2. In another terminal, start the UI:
   ```bash
   ./run_ui.sh
   ```

3. Access the UI at: http://localhost:8502

## Architecture

The system uses a Swarm pattern with specialized agents:

- **Supervisor Agent** - Coordinates the swarm and routes queries
- **Parts Inventory Specialist** - Handles inventory queries
- **Parts Delivery Specialist** - Handles delivery scheduling
- **Product BOM Specialist** - Handles bill of materials
- **Production Schedule Specialist** - Handles production planning

## Deployment

The agent is configured for deployment to Bedrock AgentCore. Use the standard deployment process with `main_agentcore.py` as the entry point.

## Tools

All agents have access to DynamoDB tables:

- PartsInventory
- PartsDelivery
- ProductBOM
- ProductionSchedule

## Example Prompts

Try these sample queries with the agent:

```
"What is the current inventory for PCB-ECU-001?"
"When is the next delivery for SENSOR-TEMP-001?"
"Show me the BOM for Advanced ECU Module"
"What is the production schedule for COMP-XYZ-123?"
"Check inventory levels for all temperature sensors and wire harnesses"
"Show upcoming deliveries from ElectroTech Solutions"
"I need to check inventory and delivery schedule for PCB-ECU-002"
"What's the total cost for producing 10 Transmission Control Modules?"
"Which parts are scheduled for delivery this month?"
"Show me all products scheduled for production in April 2025"
```
