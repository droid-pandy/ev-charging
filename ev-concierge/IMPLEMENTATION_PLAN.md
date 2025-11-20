# EV Concierge - Implementation Plan

## Current Status ✅
- ✅ AWS Bedrock integration working
- ✅ Streamlit UI functional
- ✅ Basic agent structure in place
- ✅ Mock data utilities created
- ✅ Tool definitions exist

## Problem 🔴
The Strands SDK is **not actually calling the tools**. It's just returning text responses from Claude without executing any tool functions. This is why you always see "No charging needed" regardless of the scenario.

---

## What Needs to Be Fixed

### 1. **Fix Strands SDK Tool Calling** (CRITICAL)
**Priority: HIGH**

The current `strands.py` doesn't implement proper tool calling with Claude. It needs to:
- Parse Claude's tool use requests from the response
- Execute the actual Python tool functions
- Send results back to Claude
- Continue the conversation loop

**Files to modify:**
- `ev-concierge/strands.py` - Implement proper tool calling loop

**What's broken:**
```python
# Current: Just sends tools as text, doesn't execute them
response = self.bedrock.invoke_model(...)
result = json.loads(response['body'].read())
final_response = result['content'][0]['text']  # ❌ Ignores tool calls
```

**What it should do:**
```python
# Should: Parse tool_use blocks, execute tools, send results back
while has_tool_calls and iterations < max_iterations:
    1. Call Bedrock
    2. Check if response has tool_use blocks
    3. Execute each tool function
    4. Send tool results back to Claude
    5. Get final response
```

---

### 2. **Improve Trip Planning Logic** (HIGH)
**Priority: HIGH**

Make the trip planning agent actually use the tools to calculate energy needs.

**Files to modify:**
- `ev-concierge/agents/trip_planning.py`
- `ev-concierge/tools/route_tools.py`

**Scenarios to handle:**
- ✅ Sufficient battery (no charging needed)
- ❌ Low battery (needs charging)
- ❌ Long trip (multiple charging stops)
- ❌ Cold weather (reduced range)

---

### 3. **Add Realistic Mock Scenarios** (MEDIUM)
**Priority: MEDIUM**

Create different test scenarios that trigger different agent behaviors.

**Files to create/modify:**
- `ev-concierge/utils/mock_data.py` - Add more scenarios
- `ev-concierge/test_scenarios.py` - New file for testing

**Scenarios needed:**
1. **Short trip, high battery** → No charging needed
2. **Long trip, low battery** → Needs 1 charging stop
3. **Very long trip** → Needs multiple stops
4. **Low battery + cold weather** → Emergency charging
5. **Specific preferences** → Cheapest vs fastest charging

---

### 4. **Fix Coordinator Logic** (MEDIUM)
**Priority: MEDIUM**

The coordinator needs better logic to determine when to call each agent.

**Files to modify:**
- `ev-concierge/agents/coordinator.py`

**Current issue:**
```python
# This check doesn't work because tools aren't being called
needs_charging = any('needs_charging' in str(r) and 'true' in str(r).lower() 
                    for r in trip_plan.get('tool_results', []))
```

**Should be:**
```python
# Parse actual tool results from calculate_energy_needs
energy_result = trip_plan.get('tool_results', [{}])[0]
needs_charging = energy_result.get('needs_charging', False)
```

---

### 5. **Add Better UI Feedback** (LOW)
**Priority: LOW**

Show what each agent is actually doing in real-time.

**Files to modify:**
- `ev-concierge/app_streamlit.py`

**Improvements:**
- Show tool calls as they happen
- Display charging calculations
- Show charger search results
- Display food orders in detail

---

## Implementation Order

### Phase 1: Core Functionality (Do First) 🔥
1. **Fix Strands SDK tool calling** - Without this, nothing works
2. **Test with simple scenario** - Verify tools are being called
3. **Fix coordinator logic** - Parse tool results correctly

### Phase 2: Rich Scenarios (Do Second) 📊
4. **Add diverse mock scenarios** - Different battery/distance combinations
5. **Improve trip planning** - Better energy calculations
6. **Test all scenarios** - Verify each path works

### Phase 3: Polish (Do Last) ✨
7. **Improve UI feedback** - Show agent activity
8. **Add error handling** - Graceful failures
9. **Add logging** - Debug agent decisions

---

## Quick Start: Fix Tool Calling Now

Here's what you need to do RIGHT NOW to make it work:

### Step 1: Fix `strands.py`
The Strands SDK needs to implement Claude's tool calling protocol:
- Parse `tool_use` content blocks
- Execute Python functions
- Send `tool_result` messages back

### Step 2: Test with a simple scenario
```python
# Test that calculate_energy_needs is actually called
battery = 30  # Low battery
distance = 280  # Long trip
# Should trigger: needs_charging = True
```

### Step 3: Verify in UI
You should see:
- "Charging needed: 2 stops recommended"
- Actual charger locations
- Food orders placed
- Payment processed

---

## Files That Need Work

### Critical (Fix First):
- [ ] `ev-concierge/strands.py` - Implement tool calling
- [ ] `ev-concierge/agents/coordinator.py` - Fix result parsing

### Important (Fix Second):
- [ ] `ev-concierge/utils/mock_data.py` - Add scenarios
- [ ] `ev-concierge/agents/trip_planning.py` - Better logic
- [ ] `ev-concierge/test_scenarios.py` - Create test file

### Nice to Have (Fix Later):
- [ ] `ev-concierge/app_streamlit.py` - Better UI feedback
- [ ] `ev-concierge/agents/*.py` - Add logging
- [ ] Error handling throughout

---

## Testing Checklist

Once tool calling is fixed, test these scenarios:

- [ ] Battery 80%, Distance 100mi → No charging
- [ ] Battery 30%, Distance 280mi → 1 charging stop
- [ ] Battery 20%, Distance 380mi → 2 charging stops
- [ ] Battery 15%, Distance 280mi → Emergency charging
- [ ] Cold weather (30°F) → Reduced range calculation
- [ ] User preference: "cheapest" → Select lowest price charger
- [ ] User preference: "fastest" → Select highest power charger
- [ ] Auto-order coffee → Food order placed
- [ ] Payment processing → Transaction confirmed

---

## Next Steps

**Want me to:**
1. ✅ Fix the Strands SDK tool calling implementation?
2. ✅ Create test scenarios for different battery/distance combinations?
3. ✅ Improve the coordinator logic?
4. ✅ Add better UI feedback?

**Or all of the above?** Let me know and I'll start implementing!
