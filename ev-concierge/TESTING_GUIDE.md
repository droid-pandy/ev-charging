# EV Concierge Testing Guide

## Quick Start

### 1. Test Tool Calling (Critical First Step)
```bash
cd ev-concierge
python3 test_tool_calling.py
```

This verifies that the Strands SDK is properly calling tools. You should see:
- ✅ Tools being executed
- ✅ Energy calculations happening
- ✅ Correct charging decisions

### 2. Test Individual Scenarios
```bash
# List all available scenarios
python3 run_scenario_tests.py --list

# Test a specific scenario
python3 run_scenario_tests.py one_charging_stop

# Test all scenarios
python3 run_scenario_tests.py --all
```

### 3. Run the Full App
```bash
bash start.sh
```

Then open http://localhost:8501 in your browser.

---

## Test Scenarios Explained

### Scenario 1: No Charging Needed
- **Battery:** 80%
- **Distance:** 120 miles
- **Expected:** No charging stops
- **Tests:** Basic range calculation

### Scenario 2: One Charging Stop
- **Battery:** 30%
- **Distance:** 380 miles
- **Expected:** 1 charging stop, food order, payment
- **Tests:** Full agent orchestration

### Scenario 3: Emergency Charging
- **Battery:** 15%
- **Distance:** 120 miles
- **Expected:** Immediate pre-trip charging
- **Tests:** Low battery handling

### Scenario 4: Multiple Stops
- **Battery:** 50%
- **Distance:** 1150 miles (LA to Seattle)
- **Expected:** 3+ charging stops
- **Tests:** Long-distance trip planning

### Scenario 5: Cold Weather
- **Battery:** 60%
- **Distance:** 270 miles
- **Weather:** 30°F
- **Expected:** Charging needed (reduced range)
- **Tests:** Weather impact on range

### Scenario 6: Cheapest Preference
- **Battery:** 35%
- **Distance:** 380 miles
- **Preference:** Cheapest charging
- **Expected:** Selects lowest price charger
- **Tests:** User preference handling

### Scenario 7: Fastest Preference
- **Battery:** 35%
- **Distance:** 380 miles
- **Preference:** Fastest charging + auto-order coffee
- **Expected:** Highest power charger + food order
- **Tests:** Speed priority + amenities

### Scenario 8: Borderline Case
- **Battery:** 55%
- **Distance:** 120 miles
- **Expected:** Just enough range (edge case)
- **Tests:** Buffer calculation (20% safety margin)

---

## What Each Test Validates

### Tool Calling Test (`test_tool_calling.py`)
✅ Strands SDK executes Python functions  
✅ Claude's tool_use blocks are parsed  
✅ Tool results are sent back to Claude  
✅ Agentic loop continues until final answer  

### Scenario Tests (`run_scenario_tests.py`)
✅ Energy calculations are accurate  
✅ Charging decisions are correct  
✅ Chargers are found and reserved  
✅ Food is ordered when appropriate  
✅ Payments are processed  
✅ Summary is generated correctly  

### UI Test (Manual in Browser)
✅ Agent status updates in real-time  
✅ Progress bar shows completion  
✅ Notifications appear for each action  
✅ Results are formatted nicely  
✅ Error handling works gracefully  

---

## Debugging Tips

### If tools aren't being called:
1. Check `test_tool_calling.py` output
2. Look for "Tool Calls Made: 0" - this means Strands SDK isn't working
3. Verify AWS credentials are valid
4. Check Bedrock model access

### If charging is always/never needed:
1. Check the energy calculation in tool results
2. Verify `calculate_energy_needs` is being called
3. Look at the `needs_charging` field in results
4. Check the 20% buffer is being applied

### If agents aren't running:
1. Check coordinator logic in `agents/coordinator.py`
2. Verify tool results are being parsed correctly
3. Look for exceptions in the console
4. Check that all agents are initialized

### If UI doesn't update:
1. Check browser console for errors
2. Verify Streamlit is running (port 8501)
3. Refresh the page
4. Check that session state is being updated

---

## Expected Output Examples

### Successful Tool Calling:
```
🧪 Testing Strands SDK Tool Calling
============================================================

📋 Test Scenario:
   Battery: 30%
   Range: 300 miles
   Trip: 280 miles
   Expected: Charging NEEDED

🤖 Running agent with tool calling...

============================================================
📊 RESULTS:
============================================================

✅ Tool Calls Made: 1

🔧 Tool Call #1:
   Name: calculate_energy_needs
   Input: {'battery_percent': 30, 'trip_distance_miles': 280, ...}
   Result: {'needs_charging': True, 'deficit_percent': 63.3, ...}

   ✅ Needs Charging: True
   ✅ Deficit: 63.3%

   ✅ SUCCESS: Tool correctly identified charging needed!
```

### Successful Scenario:
```
🧪 Testing Scenario: Low Battery, Long Trip
============================================================
Description: Need one charging stop en route

📊 Input:
   Battery: 30%
   Range: 300 miles
   Distance: 380 miles
   Route: Los Angeles, CA → San Francisco, CA

🤖 Running agents...

============================================================
📋 RESULTS:
============================================================

**Trip Analysis:**
Based on your 30% battery and 380-mile trip, you'll need to charge...

**⚡ Charging Plan:**
- Reserved at Tejon Ranch, CA
  Time: 10:30, Duration: 30 min
  Confirmation: `RES-CHG-101-1234567890`

**🍽️ Amenities:**
- Pre-ordered from Starbucks
  Items: Large Latte, Breakfast Sandwich
  Total: $13.50
  Pickup: 10:30
  Order: `ORD-1234567890`

**💳 Payments:**
- $13.50 to Starbucks

**Total Charged: $13.50**

🔍 Validation:
   ✅ Charging need correctly identified: True
   ✅ Charging stops: 1 (expected at least 1)
   ✅ Amenities ordered

============================================================
✅ Scenario PASSED
============================================================
```

---

## Continuous Testing

### Before Committing Code:
```bash
# Run all tests
python3 test_tool_calling.py
python3 run_scenario_tests.py --all
```

### After Changing Agents:
```bash
# Test specific scenarios affected
python3 run_scenario_tests.py one_charging_stop
python3 run_scenario_tests.py emergency_charging
```

### After Changing Tools:
```bash
# Test tool calling first
python3 test_tool_calling.py

# Then test scenarios
python3 run_scenario_tests.py --all
```

---

## Adding New Scenarios

Edit `test_scenarios.py` and add a new entry:

```python
"my_new_scenario": {
    "name": "My Test Case",
    "description": "What this tests",
    "vehicle": {
        "model": "Tesla Model Y",
        "battery_percent": 50,
        "range_miles": 300
    },
    "trip": {
        "origin": "City A",
        "destination": "City B",
        "distance_miles": 200,
        "departure": "2024-01-15T09:00:00"
    },
    "expected": {
        "needs_charging": True,
        "charging_stops": 1
    }
}
```

Then test it:
```bash
python3 run_scenario_tests.py my_new_scenario
```

---

## Success Criteria

✅ All tool calling tests pass  
✅ At least 7/8 scenarios pass  
✅ UI shows agent activity correctly  
✅ Notifications appear for each action  
✅ No Python exceptions in console  
✅ Bedrock API calls succeed  

If all these pass, your EV Concierge is working correctly!
