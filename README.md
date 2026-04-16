# Digital Director of Needs - AI Contact Center Intelligence

## Overview

An 8-hour hackathon demo showcasing how GPT-4o analyzes customer messages in real-time to classify intents (20 categories), recommend next-best-actions, and detect fraud patterns. Built with Python and Streamlit, this AI assistant helps contact center agents respond faster by processing mock customer data through a 3-stage pipeline: intent classification, action recommendations, and fraud screening. Target outcomes include 15-20% reduction in repeat calls, 25% faster resolution times, and improved fraud detection. Uses Azure OpenAI Service with mock Salesforce data for local testing, designed to scale to production with live CRM integration. See `/hackathon/README.md` for setup instructions.

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

## License

MIT License - See LICENSE file for details.

---

**8-hour hackathon demo | April 2026**
