# Digital Director of Needs - AI Contact Center Intelligence Platform

## Overview

The Digital Director of Needs is an AI-powered "traffic cop" for John Hancock's contact center that automatically classifies customer intents, enriches context from Salesforce, recommends next-best-actions to agents, detects fraud patterns, and identifies repeat caller root causes. Built on Azure AI Foundry and GPT-4o models, this platform aims to reduce repeat caller volume by 15-20%, improve SLA compliance by 25%, and increase NPS/CSAT scores by 10-15%. The system processes inbound calls and messages through a 5-stage AI pipeline: intent classification, context enrichment, intelligent routing with NBA recommendations, fraud screening, and repeat caller analysis. Agents interact with the AI insights through Microsoft Copilot Studio, receiving real-time recommendations and customer 360° views during every interaction. The platform integrates with Salesforce CRM for customer data and uses Azure Cosmos DB, Azure SQL, and Redis for multi-tier data storage and caching. This repository contains both the hackathon demo (simplified 3-stage Python app with Streamlit UI) and comprehensive technical documentation for production deployment. Expected business outcomes include faster resolution times, proactive fraud detection, and data-driven insights into why customers repeatedly contact support. The technology stack leverages Azure OpenAI Service, Azure AI Foundry Prompt Flow orchestration, and enterprise-grade security with HIPAA compliance.

## Project Status

**Phase:** Hackathon Development → Production Planning  
**Last Updated:** April 16, 2026

## Quick Start

See `/hackathon/README.md` for demo setup instructions.

## Documentation

Comprehensive internal documentation available separately (executive summary, technical specification, architecture overview, and project context).

## Repository Structure

```
DigitalDirectorOfNeeds/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore patterns
└── hackathon/                         # Demo implementation (coming soon)
    ├── README.md
    ├── app.py
    ├── intent_classifier.py
    ├── nba_recommender.py
    ├── fraud_detector.py
    ├── mock_data.py
    ├── requirements.txt
    └── .env.example
```

## Technology Stack

### Hackathon Demo
- **Python 3.10+**
- **Streamlit** - Interactive UI
- **Azure OpenAI SDK** - GPT-4o models
- **Mock Data** - Simulated Salesforce customer profiles

### Production Architecture
- **Azure AI Foundry** - Prompt Flow orchestration
- **Azure OpenAI Service** - GPT-4o deployments
- **Microsoft Copilot Studio** - Agent interface
- **Salesforce CRM** - Customer data source
- **Azure Cosmos DB** - NoSQL interaction logs
- **Azure SQL Database** - Structured analytics
- **Azure Redis Cache** - Customer context caching
- **Azure Blob Storage** - Call recordings and transcripts

## Key Features

### 5-Stage AI Pipeline

1. **Intent Classification** - Categorizes customer requests into 20 predefined intents
2. **Context Enrichment** - Retrieves customer 360° data from Salesforce
3. **Intelligent Routing + NBA** - Routes to appropriate agent and recommends next-best-actions
4. **Fraud Detection** - Multi-layer fraud screening (rules, ML models, LLM reasoning)
5. **Repeat Caller Analysis** - Identifies patterns and root causes of recurring contacts

### Intent Taxonomy (20 Categories)

Payment (Inquiry, Dispute, Setup) | Policy (Change, Cancellation) | Claims (Submission, Status) | Coverage Questions | Benefits | Provider Referrals | Account Updates | Document Requests | Premium Questions | Fraud Indicators | Complaints/Escalations | General Inquiries | Lapse Warnings | Reinstatements | Beneficiary Changes | Technical Support

## Expected Business Outcomes

- **15-20% reduction** in repeat caller rate
- **25% improvement** in SLA compliance
- **10-15% increase** in NPS/CSAT scores
- **30% improvement** in fraud detection accuracy
- **20% increase** in provider referral conversions
- **85%+ first contact resolution rate**

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Azure OpenAI API access (or OpenAI API key)
- Git
- VS Code (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/DigitalDirectorOfNeeds.git
cd DigitalDirectorOfNeeds

# Set up hackathon demo
cd hackathon
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run Streamlit demo
streamlit run app.py
```

Visit http://localhost:8501 to interact with the demo.

## Security & Compliance

- **HIPAA Compliant** - Protected Health Information (PHI) encrypted and access-controlled
- **SOC 2 Type II** - Annual third-party audits
- **Data Encryption** - AES-256 at rest, TLS 1.3 in transit
- **RBAC** - Role-based access control (Agent, Supervisor, Fraud Analyst, Admin)
- **Audit Logging** - 7-year retention for all data access
- **PII Protection** - Data masking, tokenization, and redaction

## Contributing

This is an internal John Hancock project. For questions or contributions, contact the project team.

## License

MIT License - See LICENSE file for details.

## Support

For technical support or questions:
- **Documentation:** See `/Docs` folder
- **Issues:** GitHub Issues (internal)
- **Project Owner:** John Hancock Digital Platform Team

---

**Built with ❤️ by the John Hancock Digital Transformation Team**
