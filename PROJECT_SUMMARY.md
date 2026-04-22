# Digital Director of Needs - Project Summary

## 📋 Project Overview

**Digital Director of Needs** is an AI-enhanced contact center automation system for John Hancock Long Term Care Insurance. The system uses intent classification, AI-powered recommendations, and self-service automation to reduce call volume, improve customer satisfaction, and streamline agent workflows.

---

## 🏗️ Architecture

### System Components

1. **Twilio Voice Webhook** (`twilio_webhook.py`)
   - Flask-based web server handling incoming phone calls
   - Routes: `/voice`, `/process-intent`, `/self-service`, `/transfer-agent`, `/payment-options`, `/anything-else`, `/goodbye`
   - Integrates with Lambda functions for AI classification and self-service
   - Deployed on Render.com for production testing

2. **GPT-4o Intent Classifier** (`lambda/gpt4o_intent_classifier.py`)
   - Classifies customer utterances into 5 intent categories
   - Generates AI-powered recommendations for next steps
   - Detects sentiment, relationship type, and authentication requirements
   - Returns confidence scores and self-service eligibility

3. **Self-Service Automation** (`lambda/self_service_automation.py`)
   - Handles automated responses for 4 self-serviceable intents
   - Mock data lookups (replaces Salesforce in production)
   - Provides complete, proactive information to reduce repeat calls

4. **Amazon Connect Flows** (JSON files)
   - Production-ready contact center flows
   - AI-enhanced routing logic
   - Lex V2 bot integration points

---

## 🎯 Intent Categories

### 1. CLAIM_STATUS
**What it handles:**
- "Where is my claim?"
- "Has my claim been approved?"
- "When will I get my reimbursement check?"

**Response includes:**
- Claim number, status, amount, dates
- Proactive next steps (e.g., "Check should arrive in 5-7 days")
- Direct deposit option mention
- Customer portal promotion
- Transfer option for denied claims

**Patterns:** 25+ regex patterns covering claim, reimbursement, status, tracking, payment

### 2. PAYMENT
**What it handles:**
- "How do I pay my premium?"
- "When is my payment due?"
- "I want to set up autopay"

**Response includes:**
- Premium amount, due date, autopay status
- Multiple payment methods (phone, mail, online)
- Grace period warnings for overdue
- Proactive autopay enrollment mention
- **Interactive payment flow:** Option to pay immediately

**Patterns:** 25+ regex patterns covering payment, premium, bill, due, autopay, overdue

### 3. COVERAGE_INQUIRY
**What it handles:**
- "What does my policy cover?"
- "How much is my daily benefit?"
- "What's my elimination period?"

**Response includes:**
- Daily benefit amounts (nursing home, assisted living, home care)
- Benefit period and elimination period
- Inflation protection details
- Coverage examples and claim filing guidance

**Patterns:** 20+ regex patterns covering coverage, benefits, policy, nursing home, elimination period

### 4. RATE_INCREASE
**What it handles:**
- "Why did my rate go up?"
- "I got a letter about a rate increase"
- "My premium is higher"

**Response includes:**
- Current and new premium amounts
- Effective date and percentage increase
- Transparent explanation of rate changes
- Options to reduce premium (benefit reduction, longer elimination period)
- State insurance department contact info

**Patterns:** 35+ regex patterns covering rate, premium, bill increase, cost, notice, letter

### 5. AGENT_REQUEST
**What it handles:**
- "I need to speak with someone"
- "Transfer me to an agent"
- "I want a real person"

**Response includes:**
- Immediate transfer initiation
- Wait time estimate (3-5 minutes)
- **Callback option** to prevent hold abandonment
- Periodic hold updates to prevent hangups

**Patterns:** 15+ regex patterns covering agent, person, representative, human, specialist

### 6. PROVIDER_REFERRAL
**What it handles:**
- "I need to find a provider"
- "Looking for a nursing home"
- "Help me find home care"
- "Need a care facility"

**Response includes:**
- Partnership introduction (The Helper Bees)
- Email verification for outreach
- SLA expectation (1-2 business days)
- Automatic Salesforce Health Cloud note creation
- **Retry logic:** 2 attempts with clearer options before agent transfer

**Flow:**
1. Customer requests provider help
2. System explains Helper Bees partnership
3. Verifies email address on file
4. Creates Salesforce note
5. Sets expectation for 1-2 day response
6. Daily SFTP feed to Helper Bees
7. Email outreach with provider options

**Patterns:** 20+ regex patterns covering provider, doctor, facility, nursing home, assisted living, home care

**Voice Recognition Retries:**
- **Attempt 1:** "Sorry, didn't catch that. Is that email still good? Say yes or no."
- **Attempt 2:** "Hmm, having trouble hearing you. Say 'yes' if the email is good, or 'no' if you need to update it."
- **After 2 attempts:** Transfer to agent with friendly handoff

---

## 🤖 AI Recommendations Engine

### What It Does
The `generate_recommendations()` function creates intelligent next-step suggestions for every customer interaction, adapting based on:
- Intent type
- Confidence level
- Customer sentiment
- Relationship type (owner vs. third-party)
- Self-service eligibility

### Recommendation Structure
```json
{
  "primaryAction": "Main action to take",
  "secondaryActions": ["Proactive help 1", "Proactive help 2", "..."],
  "educationalContent": ["Helpful info 1", "Helpful info 2"],
  "escalationReason": "Why agent needed (if applicable)",
  "customerExperience": "Sentiment/tone guidance"
}
```

### Examples

**PAYMENT Intent (neutral sentiment):**
```
Primary: Provide payment amount, due date, and methods
Secondary: 
  - Offer to set up autopay
  - Explain late payment consequences
  - Provide grace period information
Educational:
  - Payment methods: online, phone, mail
  - Autopay enrollment saves 3%
  - Premium payment history access
```

**RATE_INCREASE Intent (frustrated sentiment):**
```
Primary: Explain rate increase transparently
Secondary:
  - [ADDED] Acknowledge concern and apologize for frustration
  - Offer rate stability options
  - Explain industry-wide trends
Educational:
  - Why LTC rates increase (healthcare costs)
  - Options to reduce premium
  - State insurance department contact
Customer Experience: "Customer shows frustration - use empathetic language"
```

---

## 🔄 Call Flow Examples

### Example 1: Payment Inquiry (Happy Path)
```
1. Customer calls (978) 307-7738
2. System: "Thank you for calling... How can I help you today?"
3. Customer: "How do I pay my bill?"
4. [GPT-4o Classification]
   - Intent: PAYMENT (90% confidence)
   - Sentiment: neutral
   - Can self-serve: true
5. System: "Let me look that up for you." [2 sec pause]
6. System: "Your monthly premium is $450. Your next payment is due on May 1st, 2024..."
7. [AI Recommendation: Proactive payment option]
8. System: "Would you like to make a payment now? Press 1 to pay by phone..."
9. Customer: Presses 1
10. System: "I'll transfer you to our secure payment system..."
11. [Transfer to payment IVR]
```

### Example 2: Rate Increase (Frustrated Customer)
```
1. Customer: "Why did my rate go up?!" [frustrated tone]
2. [GPT-4o Classification]
   - Intent: RATE_INCREASE (90% confidence)
   - Sentiment: frustrated
   - Can self-serve: true
3. [AI Recommendation: Empathy first]
4. System: "I understand your concern, and I apologize for any frustration."
5. System: [1 sec pause]
6. System: "Let me look that up for you."
7. System: "Your premium will increase by 8% to $307.80, effective July 1st, 2026..."
8. [AI Recommendation: Educational content]
9. System: "Here's something helpful to know: Rate increases are based on overall claims costs in your area and state regulations."
10. [AI Recommendation: Secondary action]
11. System: "Would you like to review available discounts like our 3% autopay savings?"
12. System: "Is there anything else I can help you with?"
```

### Example 3: Agent Transfer with Callback
```
1. Customer: "I need to speak with someone"
2. [GPT-4o Classification]
   - Intent: AGENT_REQUEST
   - Can self-serve: false
3. System: "I can connect you with a specialist now. Current wait time is 3-5 minutes."
4. System: "Press 1 to hold, or press 2 to request a callback within the next hour."
5. Customer: Presses 2
6. System: "Perfect! We'll call you back at 978-307-7738 within the next hour."
7. System: "You'll receive a confirmation text message shortly. Thank you!"
8. [Call ends - no hold abandonment]
```

### Example 4: Provider Referral (with Retry Logic)
```
1. Customer: "I need to find a nursing home"
2. [GPT-4o Classification]
   - Intent: PROVIDER_REFERRAL (88% confidence)
   - Sentiment: neutral
   - Can self-serve: true
3. System: "Let me look that up for you." [2 sec pause]
4. System: "Got it! So we partner with The Helper Bees - they're really helpful at finding providers."
5. System: "I'm gonna put in a request for them to reach out."
6. System: "Quick thing - is customer7738@example.com still the best email for you?"
7. Customer: [Background noise - system doesn't catch response]
8. [Retry Attempt 1]
9. System: "Sorry, didn't catch that. Is that email still good? Say yes or no."
10. Customer: [Still unclear]
11. [Retry Attempt 2]
12. System: "Hmm, having trouble hearing you. Say 'yes' if the email is good, or 'no' if you need to update it."
13. Customer: "Yes"
14. System: "Perfect! I've put in the request. The Helper Bees will email you within 1-2 business days with provider options."
15. System: "They're really good at finding exactly what you need. Anything else I can help with?"
```

### Example 5: DTMF Quick Menu (No Speech)
```
1. Customer calls
2. System: "Thank you for calling... Press 1 for claims, 2 for payments, 3 for coverage, or 0 for an agent."
3. Customer: Presses 2
4. [Immediate routing - no speech recognition wait]
5. System: "Let me look that up for you..."
6. [Proceeds directly to payment handler]
```

---

## 🎨 Customer Experience Enhancements

### 1. **Callback Option (Prevents Hold Abandonment)**
- Offered during agent transfers
- Reduces abandonment rate from 15-20% to 5-10%
- Respects customer time
- Confirmation via text message

### 2. **Interactive Payment Flow**
- After payment inquiry, offers 3 options:
  - Press 1: Pay by phone (immediate transfer)
  - Press 2: Hear other methods (mail, online)
  - Press 3: Return to main menu
- Completes transaction on the same call
- Increases payment completion rate

### 3. **DTMF Quick Menu**
- Press 1 = Claims
- Press 2 = Payments
- Press 3 = Coverage
- Press 0 = Agent
- Bypasses speech recognition for clear needs
- Faster routing, reduced errors

### 4. **Proactive Information**
- **Claims:** "Check arrives in 5-7 days" (prevents "where's my check?" repeat calls)
- **Payments:** Autopay benefits mentioned every time
- **Coverage:** Examples provided, not just numbers
- **Rate Increase:** Options to reduce premium offered proactively

### 5. **No Silent Holds**
- Music + periodic updates ("You're next in line")
- Realistic wait time estimates
- Reduces hangup rate during transfers

### 6. **Restart Option**
- Press 3 at "anything else?" prompt
- "Let's start fresh" - returns to greeting
- Customer can self-recover from wrong path
- Reduces frustrated hangups

### 7. **Sentiment-Aware Responses**
- Frustrated customers hear empathy first
- "I understand your concern, and I apologize for any frustration."
- Then proceeds with information
- Improves CSAT scores

### 8. **Intelligent Retry Logic (2-Attempt System)**
- **Low Confidence (<70%):** System asks for clarification
  - **Attempt 1:** "I want to make sure I help you correctly. Are you calling about a claim, payment, or something else?"
  - **Attempt 2:** "Let me try to help. Say 'claim' if it's about a claim, 'payment' for billing, or 'agent' to speak with someone."
  - **After 2 attempts:** "Let me connect you with someone who can help you better." → Transfer to agent

- **Provider Email Verification:** Clearer yes/no questions
  - **Attempt 1:** "Sorry, didn't catch that. Is that email still good? Say yes or no."
  - **Attempt 2:** "Hmm, having trouble hearing you. Say 'yes' if the email is good, or 'no' if you need to update it."
  - **After 2 attempts:** "Alright, let me get you to someone who can help set this up." → Transfer to agent

- **Benefits:**
  - Reduces customer frustration with progressive clarification
  - Gives system 2 chances to understand before escalating
  - Uses increasingly simple yes/no questions
  - Friendly handoff to agent if still unclear
  - Prevents infinite loops and call abandonment

---

## 📊 Technical Implementation

### Intent Classification Logic
```python
def classify_with_rules(utterance: str):
    # 100+ regex patterns across 5 intents
    # Examples:
    # RATE_INCREASE: r'rate.*go.*up', r'bill.*higher', r'why.*bill.*up'
    # PAYMENT: r'pay.*premium', r'autopay', r'bill.*due'
    # CLAIM_STATUS: r'where.*check', r'claim.*approved', r'reimbursement'
    
    # Confidence calculation
    confidence = 0.85 + (pattern_matches * 0.05)
    confidence = min(confidence, 0.98)
    
    # Self-service determination
    if confidence < 0.85:
        can_self_serve = False
    elif intent not in ['CLAIM_STATUS', 'PAYMENT', 'COVERAGE_INQUIRY', 'RATE_INCREASE']:
        can_self_serve = False
    elif relationship == 'third_party':
        can_self_serve = False  # Requires POA verification
    else:
        can_self_serve = True
    
    return result
```

### Mock Data Logic (Phone Number Based)
```python
# Claim Status
def mock_claim_lookup(phone):
    last_digit = phone[-1]
    if last_digit in ['1', '2', '3']:
        return {'status': 'Approved', 'amount': 15000, ...}
    elif last_digit in ['4', '5', '6']:
        return {'status': 'Pending', 'daysRemaining': 5, ...}
    else:
        return {'status': 'In Review', ...}

# Rate Increase
def mock_rate_lookup(phone):
    last_digit = phone[-1]
    if last_digit in ['1', '2', '3']:
        return {
            'hasUpcomingIncrease': True,
            'currentPremium': 285.00,
            'newPremium': 307.80,
            'increasePercentage': 8,
            'effectiveDate': '2026-07-01'
        }
    else:
        return {'hasUpcomingIncrease': False}
```

### Session Management
```python
sessions = {}  # In-memory (use Redis in production)

# Store session on call start
sessions[call_sid] = {
    'from': from_number,
    'step': 'greeting',
    'start_time': datetime.now().isoformat()
}

# Store GPT-4o results
sessions[call_sid].update({
    'intentName': 'PAYMENT',
    'confidence': '90',
    'recommendations': {...}
})

# Retrieve in self-service route
recommendations = sessions[call_sid].get('recommendations', {})
```

---

## 🚀 Deployment

### Current Setup (Render.com)
- **Platform:** Render Web Service
- **URL:** https://digitaldirectorofneeds.onrender.com
- **Auto-deploy:** Enabled (pushes to `main` branch auto-deploy)
- **Environment:** Python 3.11
- **Port:** 10000 (Render default)
- **Start Command:** `python twilio_webhook.py`

### Twilio Configuration
- **Phone Number:** (978) 307-7738
- **Voice Webhook:** https://digitaldirectorofneeds.onrender.com/voice
- **Method:** HTTP POST
- **Speech Recognition:** Enabled (Amazon/Google/IBM)

### Production Deployment (Future - AWS Lambda)
1. Package `lambda/gpt4o_intent_classifier.py`
2. Package `lambda/self_service_automation.py`
3. Deploy to AWS Lambda with environment variables:
   - `USE_GPT4O=true`
   - `AZURE_OPENAI_ENDPOINT=...`
   - `AZURE_OPENAI_KEY=...`
   - `USE_SALESFORCE=true`
   - `SALESFORCE_ENDPOINT=...`
4. Create Amazon Lex V2 bot: `LTC_Intent_Classifier`
5. Import flow: `1_LTC_Retail_Entry_AI_Enhanced.json`
6. Update Lambda ARNs in Connect flow
7. Route 10% of production traffic for A/B testing

---

## 📈 Business Impact

### Projected Metrics

**Self-Service Rate:**
- **Before:** 40-50% (basic IVR)
- **After:** 65-75% (AI-enhanced)
- **Impact:** 25-35% increase in automation

**Repeat Call Reduction:**
- **Root Cause:** Missing information (e.g., "when will check arrive?")
- **Solution:** Proactive complete information
- **Impact:** 15-20% reduction in repeat calls

**Call Abandonment:**
- **Before:** 15-20% (long silent holds)
- **After:** 5-10% (callback option + hold updates)
- **Impact:** 50% reduction in abandonment

**Average Handle Time:**
- **Self-Service:** 20-30 seconds (vs. 5-7 min agent call)
- **Savings:** $15-20 per automated call
- **Annual Impact:** $1.5M+ (assuming 100K calls/year at 25% increase in automation)

**Customer Satisfaction (CSAT):**
- **Drivers:** Empathy, transparency, proactive help, callback option
- **Impact:** 10-15 point increase in CSAT scores

**Autopay Enrollment:**
- **Mechanism:** Mentioned in every payment inquiry
- **Impact:** 5-10% increase in autopay adoption
- **Benefit:** Reduced late payments, improved cash flow

---

## 🧪 Testing

### Test Phone Number: (978) 307-7738

### Test Scenarios

**1. Claim Status:**
- Say: "I need to check my claim status"
- Expected: Claim info + proactive next steps
- Phone ending 1-3: Approved claim
- Phone ending 4-6: Pending claim

**2. Payment Inquiry:**
- Say: "How do I pay my bill?"
- Expected: Payment info + interactive payment options
- Hear: "Would you like to make a payment now? Press 1..."

**3. Coverage Question:**
- Say: "What does my policy cover?"
- Expected: Benefits breakdown + examples

**4. Rate Increase:**
- Say: "Why did my rate go up?"
- Expected: Empathy + explanation + educational content
- Phone ending 1-3: 8% increase to $307.80
- Phone ending 4-9: No increase scheduled

**5. Agent Request:**
- Say: "I need to speak with someone"
- Expected: Wait time + callback option
- Hear: "Press 1 to hold, or 2 for callback"

**6. Quick Menu:**
- Call and wait for greeting
- Press 2 (for payments)
- Expected: Immediate payment flow (no speech wait)

**7. Restart Flow:**
- Complete any inquiry
- At "anything else?" prompt, press 3
- Expected: "Let's start fresh" + return to greeting

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (for testing without Twilio)
python lambda/gpt4o_intent_classifier.py

# Test specific utterance
>>> event = {'Details': {'Parameters': {'transcription': 'Why did my rate go up?'}}}
>>> result = lambda_handler(event, None)
>>> print(result['intentName'])  # RATE_INCREASE
>>> print(result['confidence'])  # 90
>>> print(result['canSelfServe'])  # true
```

---

## 📁 File Structure

```
DigitalDirectorOfNeeds/
├── twilio_webhook.py           # Main Flask webhook server (756 lines)
├── lambda/
│   ├── gpt4o_intent_classifier.py  # Intent classification + AI recs (478 lines)
│   └── self_service_automation.py  # Self-service handlers (392 lines)
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview
├── PROJECT_SUMMARY.md          # This file
├── Docs/                       # Technical specs (Executive Summary, Architecture)
├── 1_LTC_Retail_Entry_AI_Enhanced.json  # Amazon Connect flow
├── 3_LTC_Claims_Selfservice.json        # Claims flow
└── .gitignore

Total Code: ~1,626 lines of production Python
```

---

## 🔧 Configuration

### Environment Variables

**For Production (AWS Lambda):**
```bash
USE_GPT4O=true                    # Enable real GPT-4o classification
AZURE_OPENAI_ENDPOINT=https://...  # Azure OpenAI endpoint
AZURE_OPENAI_KEY=sk-...           # Azure OpenAI API key
USE_SALESFORCE=true               # Enable Salesforce integration
SALESFORCE_ENDPOINT=https://...   # Salesforce API endpoint
```

**For Local/Testing (Render):**
```bash
PORT=10000                        # Port for Render deployment
# (No API keys needed - uses mock data and rule-based classification)
```

### Dependencies (requirements.txt)
```
flask==3.0.0
twilio==8.10.0
```

**Future Production Dependencies:**
```
openai==1.3.0                     # Azure OpenAI SDK
simple-salesforce==1.12.4         # Salesforce API
redis==5.0.0                      # Session storage
```

---

## 🎯 Key Features Summary

1. ✅ **120+ Intent Patterns** - Comprehensive natural language coverage across 6 intents
2. ✅ **AI-Powered Recommendations** - Proactive next steps for every interaction
3. ✅ **Sentiment Detection** - Empathy-first responses for frustrated customers
4. ✅ **Interactive Payment** - Complete transactions on the same call
5. ✅ **Callback Option** - Prevents hold abandonment
6. ✅ **DTMF Quick Menu** - Faster routing for clear needs
7. ✅ **Restart Option** - Customer self-recovery from wrong path
8. ✅ **Proactive Information** - Complete details reduce repeat calls
9. ✅ **Educational Content** - Customers learn, reducing future calls
10. ✅ **No Silent Holds** - Periodic updates prevent hangups
11. ✅ **Third-Party Detection** - POA verification required
12. ✅ **Mock Data System** - Phone-based testing without live APIs
13. ✅ **Provider Referral Flow** - Helper Bees partnership with email verification
14. ✅ **Intelligent Retry Logic** - 2-attempt system with progressive clarification before agent transfer

---

## 🚦 Next Steps

### Phase 1: Optimization (Current)
- [x] Intent pattern expansion (120+ patterns across 6 intents)
- [x] AI recommendations engine
- [x] Callback option implementation
- [x] Interactive payment flow
- [x] Provider referral flow with Helper Bees integration
- [x] Intelligent retry logic (2-attempt system)
- [ ] A/B testing on live calls
- [ ] Analyze call transcripts for missed patterns

### Phase 2: Production Deployment
- [ ] Deploy Lambda functions to AWS
- [ ] Enable GPT-4o real-time classification
- [ ] Integrate Salesforce API
- [ ] Create Lex V2 bot with 5 intents
- [ ] Import Connect flow with Lambda ARNs
- [ ] Route 10% traffic to AI flow

### Phase 3: Advanced Features
- [ ] Multi-language support (Spanish)
- [ ] Voice biometrics for authentication
- [ ] Predictive call routing (next intent prediction)
- [ ] Real-time agent assist (recommendations during live calls)
- [ ] Analytics dashboard (self-service rate, CSAT, top intents)

### Phase 4: Scale
- [ ] Expand to other product lines (life insurance, annuities)
- [ ] Cross-sell recommendations
- [ ] Proactive outbound calling (premium reminders)
- [ ] SMS/Email integration for follow-ups

---

## 📞 Support & Contact

**Test Number:** (978) 307-7738  
**Deployment:** https://digitaldirectorofneeds.onrender.com  
**Repository:** https://github.com/tahlilab/DigitalDirectorOfNeeds  

**Project Lead:** Tahlia B.  
**Company:** John Hancock / Manulife  
**Purpose:** Contact Center AI Enhancement Hackathon  

---

## 📄 License

See LICENSE file for details.

---

**Last Updated:** April 21, 2026  
**Version:** 1.0  
**Status:** Production Testing (Render) / Pending AWS Lambda Deployment
