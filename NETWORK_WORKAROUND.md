# 🚀 SIMPLE SOLUTION: Test Without Tunnel

Since ngrok/cloudflare are having network issues (likely corporate firewall/VPN), here's the **easiest way to test right now**:

---

## ✅ OPTION 1: Twilio Studio Visual Flow (5 min - NO WEBHOOK NEEDED)

This lets you test the AI logic using Twilio's visual builder!

### Steps:

1. **Go to Twilio Console** → **Studio** → **Create new Flow**
2. **Name it:** "LTC AI Test Flow"
3. **Drag these widgets:**

**Widget 1: Gather Input**
- Widget Name: `gather_intent`
- Text to Say: "Thank you for calling. How can I help you today?"
- Input Type: **Speech**
- Speech Timeout: 5 seconds
- Gather Timeout: 10 seconds
- Connect to → Widget 2

**Widget 2: Make HTTP Request**
- Widget Name: `call_lambda`
- Method: POST
- URL: `https://YOUR_LAMBDA_URL/intent` (we'll create this)
- Body: `{"utterance": "{{widgets.gather_intent.SpeechResult}}"}`
- Connect SUCCESS → Widget 3
- Connect FAIL → Say "Sorry, error occurred"

**Widget 3: Say/Play**
- Widget Name: `speak_response`
- Text to Say: `{{widgets.call_lambda.parsed.response}}`
- Connect → Widget 1 (loop)

4. **Publish the flow**
5. **Assign your Twilio number** to this flow

### Now test by calling your number!

**Pros:** No webhooks, no tunnels, tests AI logic directly

---

## ✅ OPTION 2: Deploy Lambda to AWS with Function URL (10 min)

Instead of running locally, let's deploy your Lambda and get a public URL!

### Quick Deploy:

```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds

# Package the Lambda
cd lambda
zip -r function.zip gpt4o_intent_classifier.py self_service_automation.py

# Create Lambda (you need AWS CLI configured)
aws lambda create-function \
  --function-name ltc-twilio-webhook \
  --runtime python3.11 \
  --handler gpt4o_intent_classifier.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role

# Create Function URL (public endpoint)
aws lambda create-function-url-config \
  --function-name ltc-twilio-webhook \
  --auth-type NONE

# You'll get a URL like:
# https://abc123.lambda-url.us-east-1.on.aws/
```

### Then use that URL in Twilio!

---

## ✅ OPTION 3: Use Render.com (Free, 5 min)

Deploy to Render for a permanent free URL:

### Steps:

1. **Push code to GitHub** (if not already):
```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds
git add .
git commit -m "Add Twilio webhook"
git push origin main
```

2. **Go to**: https://render.com
3. **Sign up** (free account)
4. **New Web Service** → Connect your GitHub repo
5. **Configure:**
   - Name: `ltc-ai-webhook`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python twilio_webhook.py`
6. **Deploy** (takes ~2 min)

7. **You'll get a URL:** `https://ltc-ai-webhook.onrender.com`

### Use in Twilio:
- Webhook: `https://ltc-ai-webhook.onrender.com/voice`

**Pros:** Free, permanent URL, works immediately, no local server needed!

---

## ✅ OPTION 4: Test on Your Phone's Hotspot Network

If you're on corporate network causing issues:

1. **Connect Mac to your phone's hotspot** (not corporate WiFi)
2. **Find your phone hotspot IP:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```
3. **Try ngrok again:**
```bash
ngrok http 5000
```

Often works when switching off corporate network!

---

## 🎯 RECOMMENDED RIGHT NOW: Render.com

**Fastest path forward:**

1. Make sure code is in GitHub
2. Deploy to Render.com (5 minutes)
3. Get permanent URL
4. Test with Twilio immediately

**Or if you have AWS CLI configured:**
Deploy Lambda with Function URL (10 minutes)

---

## 💡 Why Network Issues?

The errors suggest:
- ✗ Corporate firewall blocking tunnel services
- ✗ VPN interference
- ✗ Proxy settings blocking outbound connections

**Solutions bypass this:**
- ☑️ Render.com: Cloud deployment
- ☑️ AWS Lambda URL: Native AWS
- ☑️ Twilio Studio: No webhook needed
- ☑️ Phone hotspot: Different network

---

## 🚀 Next Action

**Choose one:**

### A. Render.com (Recommended - 5 min):
```bash
# Already in GitHub? Just go to render.com and deploy!
```

### B. AWS Lambda (if AWS configured - 10 min):
```bash
cd lambda
zip -r function.zip *.py
# Then deploy via AWS CLI or Console
```

### C. Twilio Studio (No code deploy - 5 min):
- Go to Twilio Studio
- Build visual flow
- Test immediately

### D. Phone Hotspot (Try ngrok on different network):
- Connect to phone's hotspot
- Run: `ngrok http 5000`

Pick whichever you prefer! 🎯
