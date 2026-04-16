# Hackathon Demo - Digital Director of Needs

## 8-Hour Build: AI Contact Center Assistant

This demo showcases how GPT-4o can analyze customer messages in real-time to classify intents, recommend actions, and detect fraud patterns—helping contact center agents respond faster and more effectively.

## Objectives

**Problem:** Agents need instant context and recommendations when customers contact support.

**Solution:** AI processes every message to:
- Understand what customers need (intent classification)
- Suggest the best response strategy (next-best-actions)
- Flag suspicious activity (fraud detection)

**Success Metrics:**
- Intent accuracy: 90%+ on test messages
- Response time: <5 seconds per analysis
- Fraud detection: Identify risk patterns with explanations

## What's Included

✅ **Intent Classification** - 20 customer intent categories (GPT-4o, temp=0.3)  
✅ **Next-Best-Action Engine** - AI-recommended responses (GPT-4o, temp=0.7)  
✅ **Fraud Detection** - Risk scoring with reasoning (GPT-4o, temp=0.2)  
✅ **Mock Customer Data** - 15-20 simulated profiles with history  
✅ **Streamlit UI** - Interactive demo at localhost:8501

## What's Simplified

❌ Live Salesforce integration (using mock data)  
❌ Cloud deployment (runs locally)  
❌ Repeat caller analysis (requires historical database)  
❌ Production UI (demo uses Streamlit vs. Copilot Studio)

## Data Sources

**Mock Customer Profiles:**
- 15-20 simulated insurance customers
- Policy details (type, status, coverage)
- Interaction history (recent calls, sentiment)
- Payment history and account status
- Predefined fraud indicators for testing

**Future Production Sources:**
- Salesforce CRM (customer 360° data)
- Call recordings and transcripts
- Transaction systems
- Historical fraud cases

## Quick Setup

### Prerequisites

- Python 3.10+
- Azure OpenAI access OR OpenAI API key
- 15 minutes setup time

### Install

```bash
cd hackathon

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env with your Azure OpenAI or OpenAI API key
```

### Configure API Access

Edit `.env` file:

**Option A - Azure OpenAI:**
```env
USE_AZURE=true
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_INTENT=intent-classifier
AZURE_OPENAI_DEPLOYMENT_NBA=nba-recommender
AZURE_OPENAI_DEPLOYMENT_FRAUD=fraud-analyzer
```

**Option B - OpenAI API:**
```env
USE_AZURE=false
OPENAI_API_KEY=sk-proj-...
```

### Run Demo

```bash
streamlit run app.py
```

Open browser at `http://localhost:8501`

## Demo Workflow

1. **Select Customer** - Choose from mock customer dropdown
2. **Enter Message** - Type customer inquiry or use examples
3. **Analyze** - AI processes in 3 stages (~5 seconds)
4. **Review Results:**
   - Intent detected (with confidence %)
   - Customer context (policy, history, sentiment)
   - Recommended actions (priority ranked)
   - Fraud risk score (0-100)

## Test Messages

**Payment Issues:**
- "I was charged twice for my premium this month"
- "Why did my payment fail?"

**Claims:**
- "I submitted a claim 2 weeks ago, what's the status?"
- "How do I file a long-term care claim?"

**Fraud Indicators:**
- "I need to cash out my policy urgently"
- "Change my bank account to a new one immediately"

**Complaints:**
- "This is my third call about this issue!"
- "I want to speak to a manager now"

## Architecture

```
Customer Message (Streamlit Input)
    ↓
Intent Classifier → GPT-4o (temp=0.3)
    ↓
Mock Data Lookup → customer profiles
    ↓
NBA Recommender → GPT-4o (temp=0.7)
    ↓
Fraud Detector → Pattern matching + GPT-4o (temp=0.2)
    ↓
Display Results (4-panel UI)
```

**Processing Time:** 4-6 seconds per message  
**API Calls:** 3 GPT-4o calls per analysis

## Project Files

```
hackathon/
├── app.py                # Streamlit UI
├── intent_classifier.py  # Intent classification
├── nba_recommender.py    # Recommendation engine
├── fraud_detector.py     # Fraud detection
├── mock_data.py          # Customer profiles
├── requirements.txt      # Dependencies
├── .env.example          # Config template
└── README.md             # This file
```

## Troubleshooting

**API Authentication Failed:**
- Verify API key in `.env` file
- Check Azure endpoint has no trailing slash
- Ensure deployment names match your Azure resources

**Streamlit Won't Start:**
```bash
# Check if port 8501 is in use
lsof -i :8501
# Kill process if needed
kill -9 <PID>
```

**Slow Responses:**
- Check internet connection
- Verify Azure region latency
- Consider using gpt-3.5-turbo for faster demo

## Next Steps: Production Scale

**From Hackathon to Production:**
1. Replace mock data with live Salesforce API
2. Deploy to Azure cloud infrastructure
3. Build Microsoft Copilot Studio agent UI
4. Add repeat caller analysis (Stage 5)
5. Implement caching (Redis) for performance
6. Add monitoring and analytics dashboards
7. Security hardening (HIPAA compliance)

**Timeline:** 12-16 weeks for full production deployment

---

**Built for 8-hour hackathon | Optimized for demo speed over production scale**
