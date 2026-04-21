# 🎯 Quick Reference - Digital Director of Needs

## ✅ FIXED: Streamlit Installation

**Problem:** `pip install streamlit` failed with "externally-managed-environment" error  
**Solution:** Use Python virtual environment (required on macOS)

### ✅ Streamlit is now installed and working!

---

## 🚀 How to Run

### Option 1: Flow Simulator (No setup needed)
```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds

# Single test
python3 flow_simulator.py --utterance "I need to check my claim status"

# All scenarios
python3 flow_simulator.py --test-all
```

### Option 2: Streamlit Demo (First time)
```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds

# Create virtual environment (one time only)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install Streamlit (one time only)
pip install streamlit

# Run demo
streamlit run streamlit_demo.py
```

### Option 3: Streamlit Demo (After first time)
```bash
cd /Users/tahliab/Repos/DigitalDirectorOfNeeds
source venv/bin/activate
streamlit run streamlit_demo.py
```

---

## 📊 What You Can Demo

### 1. Flow Simulator
- Shows step-by-step execution
- Displays Lambda responses
- Tracks all contact attributes
- Validates flow logic

**Best for:** Technical demos, debugging, validation

### 2. Streamlit UI
- Interactive before/after comparison
- Live simulation animation
- Business metrics visualization
- Architecture diagrams

**Best for:** Stakeholder presentations, hackathon demos

---

## 🎯 Test Scenarios

All scenarios work in both simulator and Streamlit:

### ✅ Self-Service (Fast)
```bash
"I need to check my claim status"
"I want to pay my premium"
"What's covered under my policy?"
```
**Expected:** ~15-20 seconds, no agent needed

### 🟡 Auth Required (Medium)
```bash
"I'm calling about my mother's claim"
"I need power of attorney verification"
```
**Expected:** Transfer to auth flow with context

### 🔴 Agent Request (Immediate)
```bash
"I need to speak to an agent"
"Let me talk to a person"
```
**Expected:** Immediate transfer, skip self-service

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `flow_simulator.py` | Test flow locally |
| `streamlit_demo.py` | Interactive UI demo |
| `1_LTC_Retail_Entry_AI_Enhanced.json` | AI-enhanced flow |
| `lambda/gpt4o_intent_classifier.py` | Intent classification |
| `lambda/self_service_automation.py` | Self-service automation |

---

## 💡 Pro Tips

### Virtual Environment
- ✅ **Created:** `venv/` folder exists
- ✅ **Streamlit installed:** Ready to use
- 🔄 **Activate each session:** `source venv/bin/activate`

### Streamlit Demo
- Press **Enter** at email prompt (skip registration)
- Opens in browser automatically
- Press **Ctrl+C** to stop server

### Flow Simulator
- No virtual environment needed
- Uses Python standard library only
- Works immediately

---

## 🎉 You're Ready!

**Streamlit is installed and working.**  
**Flow simulator validated successfully.**  
**All 13 steps executed correctly.**

Choose your demo style:
- 🔧 **Technical?** → Use flow simulator
- 📊 **Business?** → Use Streamlit demo
- 🎯 **Both?** → Run both!

---

## 📞 Need Help?

Check these files:
- `TESTING_GUIDE.md` - Comprehensive testing docs
- `TESTING_COMPLETE.md` - Success report
- `README_TESTING.md` - Setup instructions

---

**Ready to demo? Run this:**
```bash
source venv/bin/activate && streamlit run streamlit_demo.py
```

🚀 **Your Digital Director of Needs is ready for the hackathon!**
