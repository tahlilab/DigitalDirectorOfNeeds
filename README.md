# Digital Director of Needs - AI Contact Center Intelligence

## Overview

The Digital Director of Needs is an AI-powered assistant that analyzes customer messages in real-time to help contact center agents respond faster and more effectively. This hackathon project demonstrates how GPT-4o can automatically classify customer intents, recommend next-best-actions, and flag potential fraud—all within seconds of receiving a customer inquiry.

## Use Case & Objectives

**Problem:** Contact centers struggle with repeat callers, delayed resolutions, and declining customer satisfaction scores.

**Solution:** An AI "traffic cop" that processes every incoming message to:
- **Classify Intent** - Understand what the customer needs (20 categories: payments, claims, policy changes, etc.)
- **Recommend Actions** - Suggest the best next steps for agents to resolve issues quickly
- **Detect Fraud** - Flag suspicious patterns before they escalate
- **Reduce Repeat Calls** - Identify root causes of recurring customer contacts

**Target Outcomes:**
- 15-20% reduction in repeat caller rate
- 25% improvement in resolution times
- 10-15% increase in customer satisfaction scores
- Enhanced fraud detection and prevention

## Project Status

**Timeframe:** 8-Hour Hackathon Demo  
**Last Updated:** April 16, 2026

## Hackathon Demo Scope

**What We Built (8 Hours):**
- ✅ Intent Classification using GPT-4o (20 customer intent categories)
- ✅ Next-Best-Action Recommendations (AI-suggested responses)
- ✅ Fraud Detection (pattern matching + AI reasoning)
- ✅ Interactive Streamlit UI for testing
- ✅ Mock customer data (15-20 simulated profiles)

**What's Simplified:**
- Mock Salesforce data instead of live API integration
- Local execution (no cloud deployment)
- 3 core AI stages (vs. 5-stage production pipeline)

## Data Sources

**Hackathon:**
- Mock customer profiles (JSON dictionary)
- Simulated interaction history
- Predefined fraud patterns

**Production (Future):**
- Salesforce CRM (customer profiles, policies, interaction history)
- Call recordings and transcripts
- Payment transaction systems
- Historical fraud cases

## Technology Stack

**Hackathon:**
- Python 3.10+
- Streamlit (web UI)
- Azure OpenAI Service (GPT-4o models)
- Mock data (no external APIs)

**Production Vision:**
- Azure AI Foundry for orchestration
- Salesforce CRM integration
- Microsoft Copilot Studio agent interface
- Azure Cosmos DB + SQL Database
- Redis caching layer

## Key Features

**AI Pipeline:**
1. **Intent Classification** → Categorize customer requests (payment issues, claims, policy changes, fraud indicators, etc.)
2. **Next-Best-Action** → AI recommends optimal response strategies for agents
3. **Fraud Detection** → Real-time risk scoring and pattern identification

**Intent Categories (20 types):**
- Payment (Inquiry, Dispute, Setup)
- Claims (Submission, Status)
- Policy (Changes, Cancellation, Reinstatement)
- Coverage & Benefits Questions
- Provider Referrals
- Account Updates
- Fraud Indicators
- Complaints & Escalations
- Technical Support

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd DigitalDirectorOfNeeds/hackathon

# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Run demo
streamlit run app.py
```

Visit `http://localhost:8501` to test the AI assistant.

## Demo Usage

1. Select a mock customer from the dropdown
2. Enter a customer message (e.g., "I was charged twice for my premium")
3. Click "Analyze" to see AI processing results:
   - Detected intent with confidence score
   - Customer context and history
   - Recommended actions for the agent
   - Fraud risk assessment

## Expected Impact

**Customer Experience:**
- Faster issue resolution
- Reduced repeat calls
- More accurate agent responses

**Operational Efficiency:**
- 15-20% reduction in repeat contacts
- 25% faster resolution times
- Improved agent productivity

**Risk Management:**
- Real-time fraud detection
- Early warning for suspicious patterns
- Reduced fraud losses

## Project Structure

```
DigitalDirectorOfNeeds/
├── README.md              # This file
├── LICENSE                # MIT License
├── .gitignore            # Git ignore rules
└── hackathon/            # 8-hour demo implementation
    ├── README.md         # Detailed setup guide
    ├── app.py           # Streamlit UI (coming soon)
    ├── intent_classifier.py
    ├── nba_recommender.py
    ├── fraud_detector.py
    ├── mock_data.py
    ├── requirements.txt
    └── .env.example
```

## Next Steps

**Post-Hackathon Roadmap:**
1. Integrate with live Salesforce API for real customer data
2. Deploy to Azure cloud infrastructure
3. Build Microsoft Copilot Studio agent interface
4. Add repeat caller analysis and trend detection
5. Implement comprehensive monitoring and analytics
6. Conduct pilot with 10-20 contact center agents
7. Scale to full production deployment

## License

MIT License - See LICENSE file for details.

## Contact

For questions about this project, contact the Digital Platform Team.

---

**Built for 8-hour hackathon demonstration | April 2026**
