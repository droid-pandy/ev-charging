# 🚀 Setup Guide - EV Concierge

## Prerequisites

### 1. AWS Account Setup
- AWS Account with Bedrock access
- IAM user with permissions for:
  - Amazon Bedrock (model invocation)
  - Optionally: DynamoDB, Secrets Manager

### 2. Enable Amazon Bedrock Models
```bash
# Go to AWS Console > Bedrock > Model access
# Request access to: Claude 3.5 Sonnet
```

### 3. AWS CLI Configuration
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-west-2
# Default output format: json
```

## Installation Steps

### Step 1: Clone/Navigate to Project
```bash
cd ev-concierge
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env
```

Minimal `.env` configuration:
```env
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
USE_MOCK_DATA=true
```

### Step 5: Verify AWS Access
```bash
# Test Bedrock access
aws bedrock list-foundation-models --region us-west-2 --query 'modelSummaries[?contains(modelId, `claude-3-5-sonnet`)].modelId'
```

### Step 6: Run the Application
```bash
python app.py
```

Access at: http://localhost:7860

## Troubleshooting

### Issue: "Access Denied" to Bedrock
**Solution**: 
1. Go to AWS Console > Bedrock > Model access
2. Request access to Claude 3.5 Sonnet
3. Wait for approval (usually instant)

### Issue: "Module 'strands' not found"
**Solution**:
```bash
pip install strands-sdk --upgrade
```

### Issue: "No AWS credentials found"
**Solution**:
```bash
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2
```

### Issue: Gradio not loading
**Solution**:
```bash
pip install gradio --upgrade
python app.py
```

## Production Deployment

### Option 1: AWS EC2
```bash
# Launch EC2 instance (t3.medium recommended)
# Install dependencies
# Run with nohup
nohup python app.py > app.log 2>&1 &
```

### Option 2: AWS ECS/Fargate
```dockerfile
# Create Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### Option 3: AWS App Runner
```bash
# Push to ECR and deploy via App Runner console
```

## API Integration (Production)

To integrate real APIs, update `.env`:
```env
USE_MOCK_DATA=false
EVGO_API_KEY=your_evgo_key
CHARGEPOINT_API_KEY=your_chargepoint_key
GOOGLE_MAPS_API_KEY=your_maps_key
STRIPE_API_KEY=your_stripe_key
```

Then update the tool files in `tools/` to call real APIs instead of mocks.

## Cost Estimation

### AWS Bedrock Costs (Claude 3.5 Sonnet)
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens
- Typical conversation: ~5,000 tokens = $0.10

### Monthly Estimate (100 trips/month)
- Bedrock: ~$10-20
- DynamoDB (optional): ~$1
- **Total: ~$11-21/month**

## Support

For issues, check:
1. AWS Bedrock model access
2. AWS credentials configuration
3. Python version (3.9+)
4. Dependencies installed correctly

## Next Steps

1. Test with example prompts
2. Customize vehicle settings
3. Integrate real APIs for production
4. Add authentication for multi-user deployment
