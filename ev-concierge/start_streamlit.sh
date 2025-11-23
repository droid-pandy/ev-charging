#!/bin/bash

echo "🚗 Starting EV Concierge Dashboard..."

# Activate virtual environment if it exists (prefer .venv, fallback to venv)
if [ -d ".venv" ]; then
    echo "🔧 Using .venv virtual environment"
    source .venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copy .env.example to .env and configure AWS credentials."
fi

# Start Streamlit
echo "🚀 Launching dashboard on http://localhost:8501"
streamlit run app_streamlit.py --server.port=8501 --server.address=0.0.0.0
