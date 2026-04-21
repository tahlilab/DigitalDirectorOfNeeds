# Amazon Connect Flow Testing Setup

## Quick Start

Test the AI-enhanced LTC Retail Entry flow locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run single test
python flow_simulator.py --utterance "I need to check my claim status"

# Run all test scenarios
python flow_simulator.py --test-all

# Run Streamlit demo
streamlit run streamlit_demo.py
```

## What This Tests

The simulator executes your `1_LTC_Retail_Entry_AI_Enhanced.json` flow locally, including:

✅ **AI Intent Classification** - GPT-4o classifier Lambda  
✅ **Self-Service Automation** - Claim status, payment, coverage lookups  
✅ **Flow Logic** - Confidence routing, error handling, auth tier determination  
✅ **Attribute Tracking** - Contact attributes set/retrieved throughout flow  

## Test Scenarios

### 1. Claim Status (High Confidence, Self-Service)
```bash
python flow_simulator.py --utterance "I need to check my claim status"
```
**Expected Path:**
1. AI greeting → Lex capture
2. GPT-4o classification (confidence: ~85%)
3. Self-service automation invokes
4. Returns claim status message
5. Disconnects (no agent needed)

**Validates:** Self-service path, high confidence routing

---

### 2. Third-Party Claim (Requires Auth)
```bash
python flow_simulator.py --utterance "I'm calling about my mother's claim"
```
**Expected Path:**
1. AI greeting → Lex capture
2. GPT-4o detects relationship: "third_party"
3. CallType set to "Other"
4. Routes to 1_LTC_Other_Auth flow
5. Simulation ends (separate flow)

**Validates:** Relationship detection, auth tier logic, flow transfer

---

### 3. Payment Inquiry
```bash
python flow_simulator.py --utterance "I want to pay my premium"
```
**Expected Path:**
1. AI greeting → Lex capture
2. Intent: PAYMENT, confidence: 90%+
3. Self-service returns payment due date
4. Offers automated payment transfer

**Validates:** Payment intent, self-service response

---

### 4. Low Confidence (Needs Clarification)
```bash
python flow_simulator.py --utterance "um I have a question about something"
```
**Expected Path:**
1. AI greeting → Lex capture
2. GPT-4o returns confidence: ~50%
3. Clarification prompt: "I want to help. Are you calling about..."
4. (In production: Get second utterance)

**Validates:** Low confidence handling, clarification loop

---

### 5. Agent Request (Immediate Transfer)
```bash
python flow_simulator.py --utterance "I need to speak to an agent"
```
**Expected Path:**
1. AI greeting → Lex capture
2. Intent: AGENT_REQUEST
3. canSelfServe: false
4. Immediate transfer to appropriate queue

**Validates:** Agent escalation, queue routing

---

## Simulator Output

The simulator shows step-by-step execution:

```
================================================================================
CONTACT FLOW SIMULATION
================================================================================
Flow: 1_LTC_Retail_Entry_AI_Enhanced
Customer says: 'I need to check my claim status'
================================================================================

Step 1: ai-greeting-start (MessageParticipant)
  🔊 Says: Thank you for calling. I'm your digital assistant...

Step 2: ai-intent-capture (GetParticipantInput)
  🤖 Lex bot 'LTC_Intent_Classifier' listening...
  🎤 Customer says: 'I need to check my claim status'

Step 3: ai-gpt4o-classifier (InvokeLambdaFunction)
  ⚡ Invoking Lambda: ltc-prod-gpt4o-intent-classifier
  ✅ Intent: CLAIM_STATUS (confidence: 85%)
     Relationship: owner, CallType: Owner
     Can self-serve: true

Step 4: ai-set-intent-attributes (UpdateContactAttributes)
  📝 Set attribute: intentName = CLAIM_STATUS
  📝 Set attribute: confidence = 85

Step 5: ai-confidence-check (Compare)
  🔀 Compare: GreaterThan '70'
     ✓ Condition matched

Step 6: ai-check-self-serve (Compare)
  🔀 Compare: Equals 'true'
     ✓ Condition matched

Step 7: ai-self-service-handler (InvokeLambdaFunction)
  ⚡ Invoking Lambda: ltc-prod-self-service-automation
  ✅ Self-service response:
     Great news! Your claim number CLM-45680 was approved on 04/10/2026...

Step 8: ai-self-serve-success (MessageParticipant)
  🔊 Says: Great news! Your claim number CLM-45680 was approved...

Step 9: ai-complete-disconnect (DisconnectParticipant)
  👋 Call disconnected

================================================================================
SIMULATION SUMMARY
================================================================================
Total steps: 9
Final Contact Attributes:
  • CallType: Owner
  • canSelfServe: true
  • claimNumber: CLM-45680
  • confidence: 85
  • entity: claim
  • intentName: CLAIM_STATUS
  • relationship: owner
  • responseMessage: Great news! Your claim number...
  • sentiment: neutral
  • transcription: I need to check my claim status
================================================================================
```

## Lambda Functions (Local Mode)

Both Lambdas run **locally** in rule-based mode:

### GPT-4o Intent Classifier
- **Mock Mode:** Uses regex patterns (no API calls)
- **Production Mode:** Set `USE_GPT4O=true` for real Azure OpenAI
- **Intents Detected:**
  - CLAIM_STATUS
  - PAYMENT
  - COVERAGE_INQUIRY
  - RATE_INCREASE
  - AGENT_REQUEST

### Self-Service Automation
- **Mock Mode:** Returns simulated Salesforce data
- **Production Mode:** Set `USE_SALESFORCE=true` for real API
- **Capabilities:**
  - Claim status lookup
  - Payment due dates
  - Coverage information

## Environment Variables (Optional)

For production testing with real APIs:

```bash
# Azure OpenAI
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com"
export AZURE_OPENAI_KEY="your-key"
export USE_GPT4O=true

# Salesforce
export SF_USERNAME="your-username"
export SF_PASSWORD="your-password"
export SF_TOKEN="your-security-token"
export USE_SALESFORCE=true
```

## What's Not Simulated

The simulator does NOT test:
- ❌ Actual Lex V2 bot (uses mock transcription)
- ❌ Real-time speech recognition
- ❌ Audio playback/prompts
- ❌ Queue wait times
- ❌ Agent transfers (stops at transfer point)

For full end-to-end testing, deploy to Amazon Connect test instance.

## Validating Before Deployment

Run all test scenarios and verify:

1. ✅ High confidence intents (>70%) proceed to self-service
2. ✅ Low confidence (<70%) triggers clarification
3. ✅ Third-party callers route to auth flow
4. ✅ Agent requests bypass self-service
5. ✅ Error handling fallback works
6. ✅ Contact attributes set correctly

If all pass, flow is ready for Amazon Connect import.

## Next Steps

After local testing succeeds:

1. **Deploy Lambdas** → Upload to AWS Lambda
2. **Create Lex Bot** → Import LTC_Intent_Classifier
3. **Import Flow** → Upload JSON to Amazon Connect
4. **Wire ARNs** → Update Lambda/Lex ARNs in flow
5. **Test in Connect** → Use test number
6. **Monitor** → CloudWatch logs, contact traces
7. **Production** → Assign to production number

## Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**Lambda errors:**
- Check `lambda/` directory exists
- Verify Python path in simulator

**Flow doesn't progress:**
- Check action Transitions in JSON
- Verify all referenced actions exist

**Want more verbose output:**
Edit `flow_simulator.py`, add debug prints in handlers
