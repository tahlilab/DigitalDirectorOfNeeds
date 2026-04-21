# 🚀 Render.com Deployment - Step by Step

## ✅ What You Need (Already Have)
- GitHub repo: ✅ `tahlilab/DigitalDirectorOfNeeds`
- Code files: ✅ `twilio_webhook.py`, `lambda/`, `requirements.txt`
- Branch: ✅ `main`

---

## 📋 Steps to Deploy (5 minutes)

### Step 1: Push Code to GitHub (1 min)

Run these commands:

```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds

# Add only the necessary files (NOT .md files)
git add twilio_webhook.py
git add lambda/
git add requirements.txt

# Commit
git commit -m "Add Twilio webhook for phone testing"

# Push to GitHub
git push origin main
```

### Step 2: Sign Up for Render (1 min)

1. Go to: **https://render.com**
2. Click **Get Started for Free**
3. Sign up with GitHub (easier integration)
4. Authorize Render to access your repos

### Step 3: Create Web Service (2 min)

1. Click **New +** → **Web Service**
2. **Connect Repository:**
   - Search for: `DigitalDirectorOfNeeds`
   - Click **Connect**

3. **Configure Service:**
   - **Name**: `ltc-ai-webhook`
   - **Region**: Choose closest to you (e.g., Oregon)
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python twilio_webhook.py`

4. **Instance Type:**
   - Select **Free** (plenty for testing)

5. Click **Create Web Service**

### Step 4: Wait for Deployment (~2 min)

Watch the deployment log. You'll see:
```
Installing dependencies...
flask==3.1.3
twilio==9.10.5
...
Starting server...
✓ Your service is live!
```

### Step 5: Get Your URL

Once deployed, you'll see:
```
https://ltc-ai-webhook.onrender.com
```

**Copy this URL!**

---

## 🎯 Configure Twilio (1 min)

1. Go to: **Twilio Console** → **Phone Numbers** → **Active Numbers**
2. Click your number
3. Under **Voice Configuration** → **A CALL COMES IN**:
   - Webhook: `https://ltc-ai-webhook.onrender.com/voice`
   - HTTP: **POST**
4. Click **Save**

---

## 📞 Test Your Number!

**Call your Twilio number** and say:
> "I need to check my claim status"

Expected response:
> "Let me look that up for you... Your claim CR-2024-12345..."

---

## 🐛 If Issues Occur

### Check Render Logs
- In Render dashboard → **Logs** tab
- Look for errors during startup

### Common Issues

**"Module not found"**
- Check `requirements.txt` has all dependencies
- Redeploy from Render dashboard

**"Connection timeout"**
- Free tier goes to sleep after 15 min inactivity
- First call after sleep takes ~30 seconds to wake up
- Upgrade to paid tier ($7/mo) for always-on

**"404 Not Found"**
- Make sure Twilio webhook ends with `/voice`
- Check: `https://ltc-ai-webhook.onrender.com/voice`

---

## 💡 After Testing

Once validated, you can:
1. Deploy Lambda functions to AWS
2. Create Lex bot
3. Import contact flow to Amazon Connect
4. Route production traffic

But for now, **Render gives you full phone testing capability!** 🎉

---

## 📊 Render Free Tier Limits

- ✅ 750 hours/month (enough for testing)
- ✅ Sleeps after 15 min inactivity
- ✅ Wakes on first request (~30 sec)
- ✅ Perfect for testing/demos

**Upgrade to $7/mo for always-on if needed**

---

## 🎯 Your Next Action

Run these commands:

```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds
git add twilio_webhook.py lambda/ requirements.txt
git commit -m "Add Twilio webhook for phone testing"
git push origin main
```

Then go to **render.com** and create the web service! 🚀
