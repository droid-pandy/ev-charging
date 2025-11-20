# 🔌 API Integration Guide

This guide explains how to integrate real external APIs into the EV Concierge system.

## Current Status

The system currently uses **mock data** for demonstration. To enable real functionality, you need to:
1. Sign up for API keys from various providers
2. Update the `.env` file with your keys
3. Implement real API calls in the tool files

## Required APIs by Category

### 1. Charging Network APIs

#### EVgo API
- **Website**: https://developer.evgo.com
- **Purpose**: Search chargers, check availability, make reservations
- **Cost**: Contact EVgo for pricing
- **Implementation**: Update `tools/charging_tools.py`

```python
# Example implementation
import requests

def search_chargers_evgo(lat, lon, radius_miles):
    headers = {"Authorization": f"Bearer {EVGO_API_KEY}"}
    response = requests.get(
        "https://api.evgo.com/v1/stations",
        headers=headers,
        params={"lat": lat, "lon": lon, "radius": radius_miles}
    )
    return response.json()
```

#### ChargePoint API
- **Website**: https://developer.chargepoint.com
- **Purpose**: Access ChargePoint network
- **Cost**: Free tier available

#### Electrify America API
- **Website**: https://developer.electrifyamerica.com
- **Purpose**: Access Electrify America network
- **Cost**: Contact for pricing

#### Tesla Supercharger API
- **Website**: https://developer.tesla.com
- **Purpose**: Access Tesla Supercharger network (for Tesla vehicles)
- **Cost**: Included with Tesla account

### 2. Food & Amenities APIs

#### Starbucks Mobile Order API
- **Access**: Requires partnership agreement
- **Alternative**: Use Uber Eats or DoorDash APIs

#### Uber Eats API
- **Website**: https://developer.uber.com/docs/eats
- **Purpose**: Pre-order food at charging locations
- **Cost**: Commission-based

#### DoorDash Drive API
- **Website**: https://developer.doordash.com
- **Purpose**: Food delivery and pickup
- **Cost**: Per-order fee

### 3. Payment APIs

#### Stripe API (Recommended)
- **Website**: https://stripe.com/docs/api
- **Purpose**: Process payments for charging and food
- **Cost**: 2.9% + $0.30 per transaction
- **Free tier**: Yes (test mode)

```python
# Example Stripe integration
import stripe

stripe.api_key = STRIPE_API_KEY

def process_payment_stripe(amount, customer_id, description):
    charge = stripe.Charge.create(
        amount=int(amount * 100),  # Convert to cents
        currency="usd",
        customer=customer_id,
        description=description
    )
    return charge
```

#### Apple Pay / Google Pay
- **Integration**: Through Stripe or direct SDK
- **Purpose**: Mobile wallet payments

### 4. Maps & Route APIs

#### Google Maps API (Recommended)
- **Website**: https://developers.google.com/maps
- **APIs needed**:
  - Directions API (routing)
  - Places API (find amenities)
  - Distance Matrix API (calculate distances)
- **Cost**: $5 per 1,000 requests (with $200 free credit/month)

```python
# Example Google Maps integration
import googlemaps

gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def get_route(origin, destination):
    directions = gmaps.directions(origin, destination)
    return directions[0]
```

#### OpenWeatherMap API
- **Website**: https://openweathermap.org/api
- **Purpose**: Weather data for energy calculations
- **Cost**: Free tier (60 calls/min)

## Implementation Priority

### Phase 1: Essential (MVP)
1. ✅ **Mock Data** (Current - for demo)
2. **Stripe API** - Payment processing
3. **Google Maps API** - Route and distance

### Phase 2: Core Functionality
4. **EVgo API** - Primary charging network
5. **ChargePoint API** - Secondary charging network
6. **OpenWeatherMap API** - Weather data

### Phase 3: Enhanced Features
7. **Electrify America API** - Additional charging network
8. **Uber Eats API** - Food ordering
9. **Tesla API** - For Tesla vehicles

## Step-by-Step Integration

### Example: Integrating Stripe

1. **Sign up for Stripe**
```bash
# Visit https://stripe.com and create account
# Get API keys from Dashboard > Developers > API keys
```

2. **Install Stripe SDK**
```bash
pip install stripe
```

3. **Update .env**
```env
STRIPE_API_KEY=sk_test_your_key_here
USE_MOCK_DATA=false
```

4. **Update tools/payment_tools.py**
```python
import stripe
from utils.config import STRIPE_API_KEY, USE_MOCK_DATA

stripe.api_key = STRIPE_API_KEY

@Tool
def process_payment(amount: float, wallet_id: str, merchant: str, description: str) -> dict:
    if USE_MOCK_DATA:
        # Return mock data
        return {...}
    
    # Real Stripe integration
    try:
        charge = stripe.Charge.create(
            amount=int(amount * 100),
            currency="usd",
            customer=wallet_id,
            description=f"{merchant}: {description}"
        )
        return {
            "transaction_id": charge.id,
            "amount": amount,
            "status": "completed",
            "timestamp": charge.created
        }
    except stripe.error.StripeError as e:
        return {
            "status": "failed",
            "error": str(e)
        }
```

## API Cost Estimates

### Monthly costs for 1,000 trips:

| Service | Cost | Notes |
|---------|------|-------|
| Google Maps | $25 | ~5 API calls per trip |
| Stripe | $29 | 2.9% + $0.30 per transaction |
| OpenWeatherMap | Free | Under 60 calls/min |
| EVgo API | Varies | Contact provider |
| ChargePoint API | Free tier | Limited calls |
| **Total** | ~$54+ | Plus charging network fees |

## Testing APIs

### Test Mode
Most APIs offer test/sandbox modes:
- **Stripe**: Use test keys (sk_test_...)
- **Google Maps**: Use development key with restrictions
- **EVgo/ChargePoint**: Request sandbox access

### Gradual Rollout
1. Start with mock data
2. Add one API at a time
3. Test thoroughly before adding next
4. Monitor costs and usage

## Security Best Practices

1. **Never commit API keys to git**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

2. **Use AWS Secrets Manager (Production)**
```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']
```

3. **Rotate keys regularly**
4. **Use least-privilege IAM roles**
5. **Monitor API usage and costs**

## Support & Resources

- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock
- **Strands SDK**: https://github.com/aws/strands-sdk
- **Stripe Docs**: https://stripe.com/docs
- **Google Maps**: https://developers.google.com/maps/documentation

## Next Steps

1. Choose which APIs to integrate first
2. Sign up and get API keys
3. Update `.env` file
4. Implement real API calls in tool files
5. Test with small dataset
6. Monitor costs and performance
7. Scale gradually
