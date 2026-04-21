# Digital Director of Needs - Local Testing

## ✅ Setup Complete!

You now have everything needed to test the AI-enhanced call flow locally:

### 📁 Files Created

```
/Users/tahliab/Repos/DigitalDirectorOfNeeds/
├── 1_LTC_Retail_Entry_AI_Enhanced.json    # AI-enhanced contact flow
├── flow_simulator.py                       # Flow execution simulator
├── streamlit_demo.py                       # Interactive demo UI
├── requirements.txt                        # Python dependencies
├── TESTING_GUIDE.md                        # Comprehensive testing docs
└── lambda/
    ├── gpt4o_intent_classifier.py         # Intent classification Lambda
    └── self_service_automation.py         # Self-service automation Lambda
```

---

## 🚀 Quick Start (3 Commands)

### 1. Test Single Utterance
```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds
python3 flow_simulator.py --utterance "I need to check my claim status"
```

**What You'll See:**
- Step-by-step flow execution
- Lambda invocations and responses
- Contact attributes set
- Final outcome (self-service, transfer, or agent)

---

### 2. Run All Test Scenarios
```bash
python3 flow_simulator.py --test-all
```

**5 Test Cases:**
1. ✅ Claim Status (Self-Service)
2. ✅ Payment Inquiry
3. ✅ Third-Party Call (Auth Flow)
4. ✅ Agent Request
5. ✅ Coverage Question

---

### 3. Launch Interactive Demo
```bash
# First time setup (macOS requires virtual environment)
python3 -m venv venv
source venv/bin/activate
pip install streamlit

# Run the demo
streamlit run streamlit_demo.py
```

**Note:** On macOS, Python packages must be installed in a virtual environment. The commands above create and activate a venv.

**Features:**
- Visual before/after comparison
- Live simulation animation
- Business impact metrics
- Technical architecture diagram

---

## 📊 What Gets Tested

| Component | Tested? | How |
|-----------|---------|-----|
| **AI Intent Classification** | ✅ Yes | GPT-4o Lambda (rule-based mock) |
| **Self-Service Automation** | ✅ Yes | Salesforce Lambda (mock data) |
| **Flow Logic** | ✅ Yes | Parses JSON, follows transitions |
| **Error Handling** | ✅ Yes | Tests retry, timeout, fallback |
| **Contact Attributes** | ✅ Yes | Tracks all attributes set/read |
| **Amazon Lex V2** | ⚠️ Mock | Uses hardcoded transcription |
| **Actual AWS APIs** | ❌ No | Local simulation only |

---

## 🎯 Expected Results

### Test Case 1: Claim Status
```
Customer: "I need to check my claim status"

Expected Flow:
  Step 1: AI greeting
  Step 2: Lex capture → transcription stored
  Step 3: GPT-4o → Intent: CLAIM_STATUS (85% confidence)
  Step 4: Confidence check → PASS (>70%)
  Step 5: Self-serve check → canSelfServe: true
  Step 6: Self-service Lambda → Claim approved $2,800
  Step 7: Play response message
  Step 8: Disconnect

Validation:
  ✅ No agent needed
  ✅ Time: ~15 seconds
  ✅ Attributes: intentName=CLAIM_STATUS, confidence=85
```

### Test Case 3: Third-Party Call
```
Customer: "I'm calling about my mother's claim"

Expected Flow:
  Step 1-3: Same as above
  Step 3: GPT-4o → relationship: third_party, CallType: Other
  Step 4: Confidence check → PASS
  Step 5: Self-serve check → canSelfServe: false (third-party)
  Step 6: Route to auth flow → Transfer to 1_LTC_Other_Auth
  Step 7: Simulation ends (separate flow)

Validation:
  ✅ Detected third-party relationship
  ✅ Routed to correct auth flow
  ✅ Passed intent context via attributes
```

---

## 🐛 Troubleshooting

### "No module named 'gpt4o_intent_classifier'"
**Fix:**
```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds
python -c "import sys; sys.path.append('lambda'); from gpt4o_intent_classifier import lambda_handler"
```

### Simulator hangs or infinite loop
**Fix:**
- Check `1_LTC_Retail_Entry_AI_Enhanced.json` for circular transitions
- Simulator has 50-step max to prevent infinite loops

### Want more verbose output
**Fix:**
Edit `flow_simulator.py`, add at line 60:
```python
print(f"DEBUG: Action {action_id} transitions: {action.get('Transitions')}")
```

---

## 📈 Next Steps After Testing

1. **Verify All Tests Pass** ✅
   - All 5 test scenarios complete successfully
   - No errors in Lambda invocations
   - Attributes set correctly

2. **Deploy to AWS** 🚀
   ```bash
   # Deploy Lambdas
   cd lambda
   zip gpt4o.zip gpt4o_intent_classifier.py
   aws lambda create-function --function-name ltc-prod-gpt4o-intent-classifier \
       --runtime python3.11 --handler gpt4o_intent_classifier.lambda_handler \
       --zip-file fileb://gpt4o.zip --role <your-role-arn>
   
   # Import flow to Amazon Connect
   # (Upload 1_LTC_Retail_Entry_AI_Enhanced.json via console)
   ```

3. **Create Lex Bot** 🤖
   - Import `LTC_Intent_Classifier` definition
   - Train bot with sample utterances
   - Assign to Amazon Connect instance

4. **Test in Amazon Connect** ☎️
   - Use test phone number
   - Call and speak actual utterances
   - Review contact traces in CloudWatch

5. **Monitor & Optimize** 📊
   - Track NPS/CSAT improvement
   - Measure self-service rate
   - Tune confidence thresholds

---

## 💡 Tips

- **Start small:** Test one utterance at a time
- **Review logs:** Check `execution_log` in simulator output
- **Compare flows:** Run old vs new flow side-by-side
- **Use Streamlit demo:** Great for presentations/demos

---

## 📞 Support

Questions? Check:
- `TESTING_GUIDE.md` - Comprehensive testing documentation
- `Docs/AI_Enhancement_Architecture_Decision.md` - Architecture decisions
- `Docs/LTC_Retail_Entry_Flow_Analysis.md` - Original flow analysis

---

**Ready to test? Run:**

```bash
python flow_simulator.py --test-all
```

🎉 **Happy Testing!**
