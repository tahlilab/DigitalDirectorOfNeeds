# 📞 Twilio Setup - Your Specific Steps

## ✅ What's Already Done
- ✅ Flask and Twilio SDK installed
- ✅ ngrok installed
- ✅ Webhook server created (`twilio_webhook.py`)
- ✅ Lambda functions ready (GPT-4o classifier + self-service)

## 🎯 Next Steps (10 minutes)

### Step 1: Get a Twilio Phone Number (2 min)

Since you already have Twilio console access:

1. Go to: https://console.twilio.com/
2. Navigate: **Phone Numbers** → **Manage** → **Buy a Number**
3. Search for a number in your area
4. Click **Buy** (Cost: ~$1/month)
5. **SAVE THIS NUMBER** - you'll call it to test!

### Step 2: Start the Webhook Server (30 sec)

Open Terminal 1:
```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds
source venv/bin/activate
python3 twilio_webhook.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

**Keep this terminal running!**

### Step 3: Expose with ngrok (30 sec)

Open a NEW Terminal 2:
```bash
ngrok http 5000
```

You'll see something like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:5000
```

**Copy the https URL** (e.g., `https://abc123.ngrok-free.app`)

**Keep this terminal running too!**

### Step 4: Configure Your Twilio Number (2 min)

1. In Twilio Console, go to: **Phone Numbers** → **Manage** → **Active Numbers**
2. Click on the number you just bought
3. Scroll to **Voice Configuration**
4. Under **A CALL COMES IN**, set:
   - **Webhook**: Paste your ngrok URL + `/voice`
   - Example: `https://abc123.ngrok-free.app/voice`
   - **HTTP**: POST
5. Click **Save**

### Step 5: Test It! 🎉 (2 min)

**Call your Twilio number** from your phone.

You should hear:
> "Thank you for calling. How can I help you today?"

**Try saying:**
- "I need to check my claim status"
- "I want to make a payment"
- "I need to speak with an agent"

---

## 🧪 What to Expect

### Self-Service Success Path
**You say:** "I need to check my claim status"

**System responds:**
1. "Let me look that up for you..." (pause)
2. "Your claim CR-2024-12345 for $15,000 was submitted on March 15th and is currently in review. The estimated completion date is April 30th, 2024. Is there anything else I can help you with?"

### Agent Transfer Path
**You say:** "I need to speak with someone"

**System responds:**
1. "I understand you'd like to speak with an agent. Let me transfer you now."
2. (Hold music plays)

### Low Confidence Path
**You say:** Something unclear like "umm... stuff"

**System responds:**
1. "I want to make sure I understand. Could you tell me what you're calling about today?"

---

## 🔍 Monitoring Your Test

Watch **Terminal 1** (Flask server) for logs:
```
Received call from: +1234567890
User said: "I need to check my claim status"
Intent: CLAIM_STATUS (confidence: 92%)
Self-service response sent
Call completed
```

---

## 🐛 Troubleshooting

### "The number you dialed is not available"
- Check: Did you save the Twilio number configuration?
- Check: Is ngrok still running? Copy the NEW URL if it changed

### "No response from webhook"
- Check: Is Flask server running in Terminal 1?
- Check: Did you add `/voice` to the end of the ngrok URL?
- Test: Visit `https://your-ngrok-url.ngrok-free.app/` in browser - should show status page

### "Call connects but silence"
- Check: Flask terminal for errors
- Check: ngrok terminal shows incoming requests
- Refresh: Restart Flask server (Ctrl+C, then `python3 twilio_webhook.py`)

---

## 💡 Testing Scenarios

Once working, test these scenarios:

### 1. Claim Status (Self-Service)
- Say: "What's the status of my claim?"
- Expected: System looks up claim and responds with details

### 2. Payment (Self-Service)
- Say: "I need to make a payment"
- Expected: System provides payment info and confirmation

### 3. Third-Party Caller (Requires Agent)
- Say: "I'm calling on behalf of my mother"
- Expected: System explains auth needed, transfers to agent

### 4. Agent Request (Direct Transfer)
- Say: "I need to speak with someone"
- Expected: Immediate transfer to agent queue

### 5. Low Confidence (Clarification)
- Say: Something vague like "I have a question"
- Expected: System asks for clarification

---

## 📊 Cost Estimate

- **Phone Number**: $1.00/month
- **Incoming Calls**: $0.0085/minute
- **Testing (30 calls, 2 min avg)**: ~$0.51
- **Total for testing**: ~$1.51

---

## 🚀 When You're Ready for Production

After validating with Twilio:

1. Deploy Lambdas to AWS (see `Real_Time_Testing_Guide.md`)
2. Create Lex bot: `LTC_Intent_Classifier`
3. Import flow to Amazon Connect
4. Route 10% of production calls to AI flow
5. Monitor NPS/CSAT improvement

---

## 📝 Current Status

**Right now, you need to:**
1. ⬜ Buy Twilio phone number
2. ⬜ Start Flask webhook server (Terminal 1)
3. ⬜ Start ngrok (Terminal 2)
4. ⬜ Configure Twilio number with ngrok URL
5. ⬜ Call and test!

**Commands ready to run:**

Terminal 1:
```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds
source venv/bin/activate
python3 twilio_webhook.py
```

Terminal 2:
```bash
ngrok http 5000
```

Let's do this! 🎉
