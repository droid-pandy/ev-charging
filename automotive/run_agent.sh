#!/bin/bash
# Start the Agent Service
# This service handles Bedrock + Strands SDK on port 8080

cd "$(dirname "$0")"
python3.12 agent_service.py --dev
