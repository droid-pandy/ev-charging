#!/bin/bash
# Start the Streamlit UI
# Access at: http://localhost:8501 (click "Open in Browser" in VS Code)

cd "$(dirname "$0")"

# Kill any existing process on port 8501
sudo kill $(sudo lsof -t -i:8501) 2>/dev/null

# Start Streamlit with light theme
python3.12 -m streamlit run app.py --server.port 8501 --theme.base light --theme.primaryColor "#1E88E5" --theme.backgroundColor "#FFFFFF" --theme.secondaryBackgroundColor "#F0F2F6" --theme.textColor "#262730"
