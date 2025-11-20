from utils.config import AWS_REGION, BEDROCK_MODEL_ID, USE_MOCK_DATA
from agents.trip_planning import TripPlanningAgent
from agents.charging_negotiation import ChargingNegotiationAgent
from agents.amenities import AmenitiesAgent
from agents.payment import PaymentAgent
from agents.monitoring import MonitoringAgent

class CoordinatorAgent:
    def __init__(self):
        self.use_mock = USE_MOCK_DATA
        self.trip_agent = TripPlanningAgent()
        self.charging_agent = ChargingNegotiationAgent()
        self.amenities_agent = AmenitiesAgent()
        self.payment_agent = PaymentAgent()
        self.monitoring_agent = MonitoringAgent()
    
    def orchestrate(self, vehicle_data: dict, trip_data: dict, user_prefs: dict) -> dict:
        results = {}
        
        # Step 1: Trip Planning
        trip_plan = self.trip_agent.analyze(vehicle_data, trip_data)
        results['trip_plan'] = trip_plan
        
        # Check if charging needed
        needs_charging = any('needs_charging' in str(r) and 'true' in str(r).lower() 
                            for r in trip_plan.get('tool_results', []))
        
        if not needs_charging:
            return {
                "summary": "✅ No charging needed for this trip. You have sufficient range!",
                "results": results
            }
        
        # Step 2: Charging Negotiation
        charging_result = self.charging_agent.find_and_reserve(trip_plan, user_prefs)
        results['charging'] = charging_result
        
        # Extract charger location and duration
        charger_location = "charging location"
        charging_duration = 30
        for r in charging_result.get('tool_results', []):
            if isinstance(r, dict):
                if 'location' in r:
                    charger_location = r['location']
                if 'duration_min' in r:
                    charging_duration = r['duration_min']
        
        # Step 3: Amenities
        amenities_result = self.amenities_agent.order_amenities(
            charger_location, user_prefs, charging_duration
        )
        results['amenities'] = amenities_result
        
        # Step 4: Payment
        transactions = []
        for r in amenities_result.get('tool_results', []):
            if isinstance(r, dict) and 'total_usd' in r:
                transactions.append({
                    "amount": r['total_usd'],
                    "merchant": r.get('restaurant', 'Food vendor'),
                    "description": f"Pre-order: {', '.join(r.get('items', []))}"
                })
        
        payment_result = self.payment_agent.process_payments(
            transactions, user_prefs.get('wallet_id', 'default')
        )
        results['payments'] = payment_result
        
        # Step 5: Generate Summary
        summary = self._generate_summary(results)
        
        return {
            "summary": summary,
            "results": results
        }
    
    def _generate_summary(self, results: dict) -> str:
        system_prompt = """You are the coordinator. Create a concise, friendly summary 
for the driver with all key information: charging location, time, amenities ordered, 
and total cost."""
        
        user_prompt = f"""
Trip Plan: {results.get('trip_plan', {}).get('analysis', '')}
Charging: {results.get('charging', {}).get('reservation', '')}
Amenities: {results.get('amenities', {}).get('order', '')}
Payments: {results.get('payments', {}).get('payments', '')}

Create a clear summary notification for the driver."""
        
        response = self.strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=[],
            max_iterations=1
        )
        
        return response.final_response
