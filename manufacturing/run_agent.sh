#!/bin/bash
# Start the Manufacturing Agent Service
# Access at: http://localhost:8080

cd "$(dirname "$0")"

echo "Starting Manufacturing Agent Service..."
echo "Access at: http://localhost:8080"
echo "Press Ctrl+C to stop"

# Kill any existing process on port 8080
sudo kill $(sudo lsof -t -i:8080) 2>/dev/null

# Start the agent service
python3.12 main_agentcore.py
