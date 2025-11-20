#!/bin/bash

case "$1" in
    start)
        echo "🚀 Starting EV Concierge Dashboard..."
        cd /project/ev-concierge
        source venv/bin/activate
        nohup streamlit run app_streamlit.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
        echo "✅ Dashboard started! Visit http://localhost:8501"
        ;;
    stop)
        echo "🛑 Stopping dashboard..."
        pkill -f "streamlit run app_streamlit.py"
        echo "✅ Dashboard stopped"
        ;;
    restart)
        echo "🔄 Restarting dashboard..."
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if pgrep -f "streamlit run app_streamlit.py" > /dev/null; then
            echo "✅ Dashboard is running"
            echo "URL: http://localhost:8501"
            ps aux | grep "streamlit run app_streamlit.py" | grep -v grep
        else
            echo "❌ Dashboard is not running"
        fi
        ;;
    logs)
        echo "📋 Showing logs (Ctrl+C to exit)..."
        tail -f /project/ev-concierge/streamlit.log
        ;;
    test)
        echo "🧪 Testing agents..."
        cd /project/ev-concierge
        source venv/bin/activate
        python3 -c "
from agents.coordinator import CoordinatorAgent
print('✅ Coordinator imported successfully')
coordinator = CoordinatorAgent()
print('✅ Coordinator initialized successfully')
print('✅ All agents are working!')
"
        ;;
    *)
        echo "EV Concierge Dashboard Manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the dashboard"
        echo "  stop    - Stop the dashboard"
        echo "  restart - Restart the dashboard"
        echo "  status  - Check if dashboard is running"
        echo "  logs    - View dashboard logs"
        echo "  test    - Test agent functionality"
        exit 1
        ;;
esac
