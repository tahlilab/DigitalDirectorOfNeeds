# Hackathon Demo - Digital Director of Needs

## Quick Start (8-Hour Build)

This simplified demo showcases the core AI capabilities of the Digital Director of Needs platform using a local Streamlit UI and mock Salesforce data.

## What's Included

- ✅ **Stage 1:** Intent Classification (GPT-4o)
- ✅ **Stage 3:** Next-Best-Action Recommendations (GPT-4o)
- ✅ **Stage 4:** Fraud Detection (Pattern matching + LLM reasoning)
- ✅ **Mock Data:** 15-20 simulated customer profiles
- ✅ **Streamlit UI:** Interactive demo interface

## What's NOT Included (Production Features)

- ❌ Stage 2: Live Salesforce API integration (using mock data instead)
- ❌ Stage 5: Repeat caller analysis (requires historical database)
- ❌ Azure resource provisioning (local execution only)
- ❌ Copilot Studio UI (using Streamlit instead)

## Prerequisites

- Python 3.10 or higher
- Azure OpenAI API access OR OpenAI API key
- 8GB RAM minimum
- Internet connection for API calls

## Installation

```bash
# Navigate to hackathon folder
cd hackathon

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your API credentials:

**Option A: Azure OpenAI (Preferred)**
```env
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_INTENT=intent-classifier
AZURE_OPENAI_DEPLOYMENT_NBA=nba-recommender
AZURE_OPENAI_DEPLOYMENT_FRAUD=fraud-analyzer
USE_AZURE=true
```

**Option B: OpenAI API (Fallback)**
```env
OPENAI_API_KEY=sk-proj-...
USE_AZURE=false
```

## Running the Demo

```bash
# Make sure virtual environment is activated
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Using the Demo

1. **Select a Customer** - Choose from dropdown (15-20 mock profiles)
2. **Enter Message** - Type a customer inquiry (or use examples)
3. **Click Analyze** - AI processes through 3 stages
4. **View Results:**
   - Intent classification with confidence score
   - Customer context (policy, history, sentiment)
   - Next-best-action recommendations (ranked)
   - Fraud risk assessment

## Example Test Messages

Try these sample customer messages:

**Payment Issues:**
- "I was charged twice for my premium this month"
- "Why did my payment fail? I have money in my account"
- "I need to update my bank account for auto-pay"

**Claims:**
- "I submitted a claim 2 weeks ago and haven't heard back"
- "How do I file a long-term care claim?"

**Policy Changes:**
- "I want to add my newborn baby to my policy"
- "Can I increase my coverage amount?"

**Suspicious (Fraud):**
- "I need to cash out my policy immediately, it's urgent"
- "I want to change the bank account on file to a new one"

**Complaints:**
- "This is the third time I've called about this! I want a manager"
- "Your service is terrible, I'm canceling my policy"

## Demo Architecture

```
User Input (Streamlit UI)
    ↓
[Stage 1: Intent Classification]
    GPT-4o Model (temp=0.3)
    20-intent taxonomy
    ↓
[Mock Data Lookup]
    Retrieve customer from MOCK_CUSTOMERS dict
    ↓
[Stage 3: NBA Recommendations]
    GPT-4o Model (temp=0.7)
    Context-aware suggestions
    ↓
[Stage 4: Fraud Detection]
    Pattern matching + GPT-4o reasoning (temp=0.2)
    Risk scoring (0-100)
    ↓
Display Results (4 sections in UI)
```

## File Structure

```
hackathon/
├── app.py                    # Streamlit UI (main entry point)
├── intent_classifier.py      # Stage 1: Intent classification
├── nba_recommender.py        # Stage 3: Next-best-action engine
├── fraud_detector.py         # Stage 4: Fraud detection
├── mock_data.py              # Mock customer profiles
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # This file
```

## Troubleshooting

**Issue: Import errors**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**Issue: API authentication failed**
- Check your API key is correct in `.env`
- Verify Azure endpoint URL has no trailing slash
- Test API access: `curl -H "api-key: YOUR_KEY" YOUR_ENDPOINT/openai/deployments`

**Issue: Streamlit won't start**
```bash
# Check port 8501 is not in use
lsof -i :8501
# Kill existing process if needed
kill -9 <PID>
```

**Issue: Slow API responses**
- Check internet connection
- Verify Azure region latency
- Consider using lighter model for demo (gpt-3.5-turbo)

## Performance Expectations

- **Intent Classification:** <1 second
- **NBA Recommendations:** 2-3 seconds
- **Fraud Detection:** 1-2 seconds
- **Total Processing:** 4-6 seconds per message

## Next Steps: From Demo to Production

1. **Azure Resource Provisioning** - Deploy Cosmos DB, SQL, Redis, AI Foundry
2. **Salesforce Integration** - Replace mock data with live API calls
3. **Copilot Studio UI** - Build agent-facing dashboard
4. **Stage 2 & 5 Implementation** - Add context enrichment and repeat caller analysis
5. **Security Hardening** - HIPAA compliance, encryption, RBAC
6. **Performance Optimization** - Caching, batch processing, async operations
7. **Monitoring & Alerting** - Application Insights, custom dashboards

## Cost Estimate (Demo)

**OpenAI API:**
- ~1,000 tokens per analysis
- $0.01 per 1K tokens (GPT-4)
- ~$0.01 per customer interaction
- 100 demo interactions = ~$1.00

**Azure OpenAI:**
- Pay-as-you-go or provisioned throughput
- Similar costs to OpenAI API

## Support

For issues or questions, refer to internal project documentation or contact the project team.

---

**Demo built for 8-hour hackathon constraint. Production implementation documented in `/Docs`.**
