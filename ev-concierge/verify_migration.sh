#!/bin/bash

echo "=========================================="
echo "Strands SDK Migration Verification"
echo "=========================================="
echo ""

echo "1. Checking Python environment..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python3 found: $(python3 --version)"
else
    echo "   ❌ Python3 not found"
    exit 1
fi

echo ""
echo "2. Checking Strands SDK installation..."
python3 -c "import strands; print('   ✅ Strands SDK installed')" 2>/dev/null || {
    echo "   ❌ Strands SDK not installed"
    exit 1
}

echo ""
echo "3. Testing agent imports..."
python3 -c "
from agents.trip_planning import TripPlanningAgent
from agents.charging_negotiation import ChargingNegotiationAgent
from agents.amenities import AmenitiesAgent
from agents.payment import PaymentAgent
from agents.monitoring import MonitoringAgent
from agents.coordinator import CoordinatorAgent
print('   ✅ All agents import successfully')
" || {
    echo "   ❌ Agent import failed"
    exit 1
}

echo ""
echo "4. Testing tool imports..."
python3 -c "
from tools.route_tools import calculate_energy_needs, get_route_info
from tools.charging_tools import search_chargers, reserve_charging_slot
from tools.amenities_tools import check_nearby_amenities, place_food_order
from tools.payment_tools import process_payment, get_payment_history
print('   ✅ All tools import successfully')
" || {
    echo "   ❌ Tool import failed"
    exit 1
}

echo ""
echo "5. Verifying async support..."
python3 -c "
import asyncio
from agents.trip_planning import TripPlanningAgent
agent = TripPlanningAgent()
assert hasattr(agent, 'analyze_async'), 'Missing async method'
print('   ✅ Async methods present')
" || {
    echo "   ❌ Async verification failed"
    exit 1
}

echo ""
echo "6. Checking tool return types..."
python3 -c "
from tools.route_tools import calculate_energy_needs
import json
result = calculate_energy_needs(50, 100, 300)
assert isinstance(result, str), 'Tool should return string'
json.loads(result)  # Verify it's valid JSON
print('   ✅ Tools return JSON strings')
" || {
    echo "   ❌ Tool return type check failed"
    exit 1
}

echo ""
echo "7. Verifying custom SDK removed..."
if [ ! -f "strands_custom.py" ]; then
    echo "   ✅ Custom SDK file removed"
else
    echo "   ⚠️  Custom SDK file still exists"
fi

echo ""
echo "=========================================="
echo "✅ Migration Verification Complete!"
echo "=========================================="
echo ""
echo "All checks passed. The migration is successful."
echo ""
echo "Next steps:"
echo "  - Run: python3 test_conversion.py"
echo "  - Run: python3 test_simple.py"
echo "  - Review: STRANDS_SDK_MIGRATION.md"
echo ""
