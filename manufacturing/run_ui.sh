#!/bin/bash
# Start the Manufacturing Streamlit UI
# Access at: http://localhost:8502

cd "$(dirname "$0")"

echo "Starting Manufacturing Agent UI..."
echo "Access at: http://localhost:8502"
echo "Press Ctrl+C to stop"

# Kill any existing process on port 8502
sudo kill $(sudo lsof -t -i:8502) 2>/dev/null

# Start Streamlit with light theme on port 8502
python3.12 -m streamlit run app.py --server.port 8502 --theme.base light --theme.primaryColor "#1E88E5" --theme.backgroundColor "#FFFFFF" --theme.secondaryBackgroundColor "#F0F2F6" --theme.textColor "#262730"
