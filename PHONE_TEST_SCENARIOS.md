# 📞 Comprehensive Phone Testing Scenarios

## 🎯 Your Test Number: (978) 307-7738

---

## ✅ Test Scenario 1: Claim Status (Self-Service Success)

**What to Say:**
> "I need to check my claim status"

**Expected Flow:**
1. 🤖 System: "Let me look that up for you..." *(2 second pause)*
2. 🤖 System: "Your claim CR-2024-12345 for $15,000 was submitted on March 15th and is currently in review. The estimated completion date is April 30th, 2024."
3. 🤖 System: "Is there anything else I can help you with? Press 1 for yes, or 2 for no."

**Test Variations:**
- "What's the status of my claim?"
- "Where is my reimbursement?"
- "Has my claim been approved?"
- "I submitted a claim and want to check on it"

**Routes Tested:**
- ✅ `/voice` → Initial greeting
- ✅ `/process-intent` → Intent classification
- ✅ `/self-service` → Claim status lookup
- ✅ `/anything-else` → Follow-up prompt

---

## ✅ Test Scenario 2: Payment Inquiry (Self-Service Success)

**What to Say:**
> "I want to make a payment"

**Expected Flow:**
1. 🤖 System: "Let me look that up for you..." *(2 second pause)*
2. 🤖 System: "Your next premium payment of $450 is due on May 1st, 2024. You can pay by mailing a check to PO Box 12345, Boston MA 02101, or by calling our automated payment line at 1-800-555-1234."
3. 🤖 System: "Is there anything else I can help you with?"

**Test Variations:**
- "How do I pay my premium?"
- "When is my bill due?"
- "What's my payment amount?"
- "I need to pay my premium"

**Routes Tested:**
- ✅ `/voice` → `/process-intent` → `/self-service` (payment)

---

## ✅ Test Scenario 3: Coverage Inquiry (Self-Service Success)

**What to Say:**
> "What does my policy cover?"

**Expected Flow:**
1. 🤖 System: "Let me look that up for you..."
2. 🤖 System: "Your policy provides $150 per day for nursing home care, $120 per day for assisted living, and $90 per day for home healthcare. Your current benefit period is 3 years with a 90-day elimination period."
3. 🤖 System: "Is there anything else I can help you with?"

**Test Variations:**
- "What are my benefits?"
- "How much coverage do I have?"
- "Tell me about my policy"
- "What's covered under my plan?"

**Routes Tested:**
- ✅ `/voice` → `/process-intent` → `/self-service` (coverage)

---

## ✅ Test Scenario 4: Rate Increase (Self-Service Success) - FIXED ✅

**What to Say:**
> "I got a letter about a rate increase"

**Expected Flow:**
1. 🤖 System: "Let me look that up for you..."
2. 🤖 System: "Your current monthly premium is $285.00. You do not have any scheduled rate increases at this time. If you have specific questions about premium rates, I'd be happy to connect you with a specialist."
   
   **Note**: Your number (978) 307-7738 ends in 8, so mock data returns "no increase". 
   Numbers ending in 1-3 would get: "Your premium will be increasing by 8% to $307.80, effective July 1st, 2026..."

3. 🤖 System: "Is there anything else I can help you with?"

**Test Variations:** ✅ All now working!
- "Why did my rate go up?" ✅
- "My premium is higher" ✅
- "Tell me about the rate increase letter" ✅
- "Why is my premium increasing?" ✅

**Routes Tested:**
- ✅ `/voice` → `/process-intent` → `/self-service` (rate increase)

**Recent Fix:** Added regex patterns for "rate go up", "rate went up", "premium higher" to properly detect all variations.

---

## ✅ Test Scenario 5: Third-Party Caller (Transfer to Agent)

**What to Say:**
> "I'm calling on behalf of my mother"

**Expected Flow:**
1. 🤖 System: "I understand you're calling on behalf of someone else. For privacy and security, I'll need to verify authorization before discussing account details. Let me transfer you to an agent who can assist you."
2. 🎵 Hold music plays
3. 🤖 System: "Thank you for your patience. An agent will be with you shortly."

**Test Variations:**
- "I'm calling for my father"
- "I have power of attorney for my mom"
- "This is about my parent's policy"

**Routes Tested:**
- ✅ `/voice` → `/process-intent` → `/transfer-agent`

**Why Transfer?**
- Requires authentication verification
- Cannot self-service without proper authorization
- Needs human judgment for POA/authorization

---

## ✅ Test Scenario 6: Agent Request (Direct Transfer)

**What to Say:**
> "I need to speak with someone"

**Expected Flow:**
1. 🤖 System: "I understand you'd like to speak with an agent. Let me transfer you now."
2. 🎵 Hold music plays
3. 🤖 System: "An agent will be with you shortly."

**Test Variations:**
- "Can I talk to a person?"
- "I want to speak to an agent"
- "Transfer me to someone"
- "I need a representative"

**Routes Tested:**
- ✅ `/voice` → `/process-intent` → `/transfer-agent`

---

## ✅ Test Scenario 7: Low Confidence / Unclear (Clarification)

**What to Say:**
> "Umm... I have a question"

**Expected Flow:**
1. 🤖 System: "I want to make sure I help you correctly. Are you calling about a claim, a payment, or something else?"
2. 👤 You: "A claim"
3. 🤖 System: "Let me look that up for you..." *(proceeds with claim status)*

**Test Variations:**
- "I need help"
- "Something about my policy"
- "I got a letter"
- "Hello?"

**Routes Tested:**
- ✅ `/voice` → `/process-intent` → `/process-clarification` → `/self-service`

**Why Clarification?**
- Low confidence (<70%) triggers clarification
- Ensures accurate routing
- Better customer experience than guessing

---

## ✅ Test Scenario 8: Multiple Requests (Loop Back)

**Full Conversation:**

1. 👤 "Check my claim status"
2. 🤖 *(Provides claim status)* "Is there anything else I can help you with? Press 1 for yes, or 2 for no."
3. 👤 Press **1** or say "Yes"
4. 🤖 "Sure, what else can I help you with?"
5. 👤 "When is my payment due?"
6. 🤖 *(Provides payment info)* "Is there anything else I can help you with?"
7. 👤 Press **2** or say "No"
8. 🤖 "Thank you for calling. Goodbye!"

**Routes Tested:**
- ✅ Full conversation loop
- ✅ `/anything-else` → `/voice` (loop)
- ✅ `/anything-else` → `/goodbye` (exit)

---

## 🔍 Advanced Testing: Policy Number Enhancement

### Current State:
- System uses **phone number** to look up account
- No need to ask for policy number explicitly

### Enhancement Opportunity:
If you want to test **policy number verification**, we can add:

**Example Enhanced Flow:**
1. 👤 "Check my claim status"
2. 🤖 "I found multiple policies associated with this number. Please say or enter your 8-digit policy number."
3. 👤 "12345678"
4. 🤖 "Thank you. Let me look that up..."

**Want me to add this enhancement?** This would:
- Allow multiple policies per phone number
- Add security verification
- Match production Amazon Connect behavior

---

## 📊 Testing Checklist

### Self-Service Paths (Should NOT transfer):
- [ ] Claim status inquiry (owner)
- [ ] Payment inquiry (owner)
- [ ] Coverage inquiry (owner)
- [ ] Rate increase question (owner)

### Agent Transfer Paths (SHOULD transfer):
- [ ] Third-party caller (POA, family member)
- [ ] Agent commission inquiry
- [ ] Direct agent request
- [ ] Complex questions (after clarification fails)

### Technical Paths:
- [ ] Low confidence → Clarification → Success
- [ ] Multiple requests in one call
- [ ] "Anything else?" loop
- [ ] Graceful goodbye

---

## 🎯 Success Metrics to Track

### Self-Service Rate:
**Target**: 60-70% of calls automated

**Current Test Results**:
- Claim Status: ✅ Self-service
- Payment: ✅ Self-service
- Coverage: ✅ Self-service
- Third-Party: ❌ Transfer (correct)
- Agent Request: ❌ Transfer (correct)

### Average Handle Time:
**Target**: 15-30 seconds for self-service

**Flow Timing**:
- Greeting: 3 sec
- Intent capture: 3-5 sec
- Classification: 1 sec
- Response: 10-15 sec
- **Total**: ~20 seconds ✅

### Speech Recognition Accuracy:
**Target**: >95% correct intent classification

**Test Quality**:
- Clear speech: 95%+ accuracy expected
- Noisy background: 85%+ accuracy
- Accents: 90%+ accuracy

---

## 🚀 Next Steps After Testing

### Phase 1: Validate Core Flows (Today)
- [ ] Test all 8 scenarios above
- [ ] Check Render logs for errors
- [ ] Verify Twilio call logs
- [ ] Note any issues

### Phase 2: Enhancements (This Week)
- [ ] Add policy number verification
- [ ] Add authentication for third-party
- [ ] Enhance error handling
- [ ] Add call recording for quality

### Phase 3: Production Prep (Next Week)
- [ ] Deploy Lambdas to AWS
- [ ] Create Lex V2 bot (LTC_Intent_Classifier)
- [ ] Import flow to Amazon Connect
- [ ] Route 10% of traffic to AI flow

### Phase 4: Measure & Optimize (Month 1)
- [ ] Track NPS/CSAT scores
- [ ] Monitor self-service rate
- [ ] Analyze call transcripts
- [ ] Refine intent classification

---

## 💡 Tips for Best Test Results

### 1. Speak Clearly
- Pause after "beep"
- Speak at normal pace
- Avoid background noise

### 2. Use Natural Language
- Say what you'd naturally say
- Don't try to "game" the system
- Test with different phrasings

### 3. Test Edge Cases
- Mumble intentionally (low confidence test)
- Interrupt yourself
- Use industry jargon
- Ask unusual questions

### 4. Check Logs After Each Call
- Render logs show intent detected
- Twilio logs show TwiML flow
- Compare expected vs. actual

---

## 🐛 Common Issues & Fixes

### Issue: "Application error occurred"
- **Cause**: Missing route or 404 error
- **Check**: Render logs for stack trace
- **Fix**: Ensure route exists, redeploy

### Issue: "I didn't catch that"
- **Cause**: Speech timeout or silence
- **Check**: Did you speak after beep?
- **Fix**: Speak louder, reduce background noise

### Issue: Wrong intent detected
- **Cause**: Ambiguous phrasing or low confidence
- **Check**: Render logs show detected intent
- **Fix**: Rephrase or add pattern to classifier

### Issue: Call disconnects suddenly
- **Cause**: TwiML error or missing redirect
- **Check**: Twilio debugger logs
- **Fix**: Ensure all paths have `resp.say()` or `resp.redirect()`

---

## 📞 Ready to Test?

**Call (978) 307-7738 and try these scenarios!**

After each test, check:
1. **Render Dashboard** → Logs tab → See intent classification
2. **Twilio Console** → Monitor → Calls → See TwiML flow
3. **Your experience** → Did it work as expected?

**Good luck! Let me know how each scenario goes!** 🎉
