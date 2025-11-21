# Route Verification Guide

## The Fix

**Problem**: Charging stations weren't matching the route (e.g., showing Tejon Ranch for Seattle → SF)

**Root Cause**: The coordinator was passing `trip_plan` (which doesn't contain origin/destination) instead of `trip_data` to the charging agent.

**Solution**: 
1. Updated coordinator to pass `trip_data` to charging agent
2. Updated charging agent to extract origin and destination from `trip_data`
3. Updated agent prompt to explicitly use origin and destination when calling `search_chargers`

## How It Works Now

### Data Flow:
```
User Input (Seattle → San Francisco)
    ↓
Coordinator receives trip_data: {origin: "Seattle, WA", destination: "San Francisco, CA"}
    ↓
Charging Agent receives trip_data
    ↓
Agent calls: search_chargers(route="Seattle, WA", destination="San Francisco, CA")
    ↓
OpenChargeMap API queries midpoint between Seattle and SF
    ↓
Returns stations in Oregon (Crescent, Sutherlin, Roseburg)
    ↓
Agent reserves best station
    ↓
UI shows real station on the route
```

## Test Different Routes

### Route 1: Los Angeles → San Francisco (380 mi)
**Expected Stations**: Central California (Kettleman City, Lost Hills, San Luis Obispo)

```bash
python test_charging_search.py
# Should show stations in Central CA, NOT Tejon Ranch
```

### Route 2: Seattle → San Francisco (800 mi)
**Expected Stations**: Oregon (Crescent, Sutherlin, Roseburg, Grants Pass)

```bash
python test_seattle_sf.py
# Should show stations in Oregon
```

### Route 3: Los Angeles → San Diego (120 mi)
**Expected Stations**: Orange County (Laguna Hills, Mission Viejo, San Clemente)

```bash
# In Python:
from tools.charging_tools import search_chargers
import json
result = search_chargers("Los Angeles, CA", "San Diego, CA", min_power_kw=100)
stations = json.loads(result)
for s in stations[:3]:
    print(f"{s['network']} - {s['location']}")
```

## Verification Checklist

✅ **Charging stations match the route**
- LA → SF shows Central CA stations
- Seattle → SF shows Oregon stations
- LA → SD shows Orange County stations

✅ **No hardcoded locations**
- Tejon Ranch only appears for routes that actually pass through it
- Each route gets unique, relevant stations

✅ **Real network names**
- Tesla Supercharger
- Electrify America
- EVgo
- ChargePoint
- Rivian Adventure Network

✅ **Reservation includes real data**
- Network name from search results
- Location from search results
- Power rating from search results

## Running the Full App

```bash
cd ev-concierge
streamlit run app_streamlit.py
```

**Test Scenarios:**

1. **Seattle → San Francisco** (35% battery)
   - Should show Oregon stations
   - Reservation should be for Oregon location

2. **Los Angeles → San Francisco** (35% battery)
   - Should show Central CA stations
   - Reservation should be for Kettleman City or Lost Hills

3. **San Diego → Los Angeles** (35% battery)
   - Should show Orange County stations
   - Reservation should be for Laguna Hills or Mission Viejo

## Console Output to Watch For

When the app runs, you should see:
```
🔍 Querying OpenChargeMap API...
   Midpoint: (42.69055, -122.37575)  ← Should match route
   Search radius: 575.6 km
   Min power: 150 kW
   Found 20 stations from API
```

The **midpoint coordinates** should be between your origin and destination!

## If You Still See Wrong Stations

1. **Check .env file**: `USE_MOCK_DATA=false`
2. **Restart the app**: Old data might be cached
3. **Check console output**: Look for "Querying OpenChargeMap API..."
4. **Verify coordinates**: Midpoint should be between origin and destination

---

**The system now dynamically pulls charging stations based on the actual route!** 🎉
