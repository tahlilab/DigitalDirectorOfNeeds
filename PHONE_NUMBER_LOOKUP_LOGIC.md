# 📱 Phone Number Lookup Logic - How It Works

## 🔍 Current System Behavior

### **Yes, the system assumes data exists for testing!**

For the **mock/demo version**, the system uses **phone number patterns** to simulate different scenarios:

---

## 📞 Phone Number Testing Matrix

### Your Test Number: **(978) 307-7738**

**Last Digit: 8** → This will return a **DENIED CLAIM** scenario

Here's what happens with different numbers:

| Last Digit | Scenario | What You'll Hear |
|------------|----------|------------------|
| **0** | ❌ No claim found | "I don't see any active claims on file. If you recently submitted a claim, it may take 24 to 48 hours to appear in our system. Would you like to speak with an agent?" |
| **1-4** | ✅ Approved claim | "Your claim CLM-45679 was approved on 04/10/2026 for $2,800. Your reimbursement check was mailed on 04/18/2026..." |
| **5-7** | ⏳ Pending claim | "Your claim CLM-45680 is currently pending review. We received it on 04/15/2026 and you should receive a decision within 5 business days." |
| **8** | ❌ Denied claim | *Currently returns approved - needs enhancement* |
| **9** | ✅ Multiple claims | *Currently returns pending - needs enhancement* |

---

## 🎯 Your Number (978) 307-7738 Behavior

**Last Digit: 8** → Currently returns **APPROVED** claim

**Current Response:**
> "Your claim CLM-45686 was approved on 04/10/2026 for $2,800..."

---

## 💡 Enhancement Recommendation

Want me to add **proper scenarios** for all digits? Here's what I can add:

### Enhanced Scenarios:

**0 - No Account Found:**
> "I'm unable to locate an account associated with this phone number. For privacy and security, I'll need to verify your information. Let me transfer you to an agent."

**8 - Denied Claim:**
> "I see that claim number CLM-45686 was not approved. A detailed explanation was mailed to you on April 5th. If you have questions about this decision, I can connect you with a claims specialist. Would you like me to do that?"

**9 - Recent Claim (VIP scenario):**
> "Your claim CR-2024-12345 for $15,000 was submitted on March 15th and is currently in review. The estimated completion date is April 30th, 2024."

---

## 🔧 Production vs. Testing Behavior

### **Testing Mode (Current):**
- ✅ Uses phone number patterns
- ✅ Always returns mock data (except digit 0)
- ✅ No real Salesforce lookup
- ✅ Perfect for demos and testing

### **Production Mode (Future):**
```python
if os.getenv('USE_SALESFORCE') == 'true':
    claim_data = lookup_salesforce_claim(phone)
else:
    claim_data = mock_claim_lookup(phone)
```

When `USE_SALESFORCE=true`:
- 🔍 Real Salesforce API lookup
- 🔒 Actual customer data
- ⚠️ Returns None if phone not found
- 🔐 Requires authentication

---

## 📋 Test Scenarios for "Not Found"

### Scenario 1: Call from Unknown Number

**Phone ending in 0** (e.g., change Twilio number to end in 0)

**Expected Flow:**
1. 👤 "Check my claim status"
2. 🤖 "Let me look that up for you..."
3. 🤖 "I don't see any active claims on file. If you recently submitted a claim, it may take 24 to 48 hours to appear in our system. Would you like to speak with an agent?"
4. 👤 Say "Yes" → Transfers to agent
5. 👤 Say "No" → "Is there anything else I can help you with?"

**Routes Tested:**
- ✅ Claim lookup returns None
- ✅ Graceful "not found" handling
- ✅ Option to transfer or continue

### Scenario 2: Account Lookup (All Intents)

**For testing, you can:**

1. **Use Twilio "From" override** (if testing via API)
2. **Change your Twilio number** to end in different digits
3. **Or** I can add a feature where you **say your phone number**

---

## 🚀 Quick Enhancement Option

### Add Phone Number Capture

**New Flow:**
1. 👤 "Check my claim status"
2. 🤖 "To look that up, please say or enter the phone number on your account, starting with area code."
3. 👤 "555-123-4560" (ending in 0)
4. 🤖 "I don't see any active claims..."

**Benefits:**
- ✅ Test all scenarios without changing Twilio number
- ✅ Matches production behavior
- ✅ Adds security layer
- ✅ Supports multiple policies per number

**Want me to add this?**

---

## 🎯 Recommended Testing Approach

### Option A: Test with Current Number (Quick)

Your number **(978) 307-7738** ends in **8**:
- ✅ Returns approved claim
- ✅ Tests self-service success path
- ✅ Quick validation

### Option B: Add Phone Capture (Better)

**I can enhance the webhook to ask:**
> "To look that up, please say the phone number on your account."

Then you can test:
- 555-123-4560 → No claim found
- 555-123-4561 → Approved claim
- 555-123-4565 → Pending claim

### Option C: Buy Multiple Test Numbers (Overkill)

Buy Twilio numbers ending in different digits - **NOT recommended**, too expensive for testing!

---

## 💰 Production Salesforce Lookup

When deployed to production with Salesforce enabled:

```python
def lookup_salesforce_claim(phone: str):
    """Real Salesforce lookup"""
    query = f"SELECT ClaimNumber__c, Status__c, Amount__c 
             FROM Claim__c 
             WHERE Phone__c = '{phone}' 
             AND Status__c != 'Closed' 
             ORDER BY CreatedDate DESC 
             LIMIT 1"
    
    result = sf.query(query)
    
    if not result['records']:
        return None  # No claim found
    
    return format_claim_data(result['records'][0])
```

**Returns None when:**
- Phone number not in Salesforce
- No active claims (all closed)
- Invalid phone format

**Triggers transfer to agent:**
- Account verification needed
- Multiple policies require selection
- Complex claim situations

---

## 🎯 Recommendation

**For your testing today:**

1. ✅ **Use current setup** - Your number returns approved claim
2. ✅ **Test happy path** - Claim status, payment, coverage
3. ✅ **Test agent transfers** - Third-party, agent request

**For enhanced testing:**

Let me add **phone number capture** so you can test:
- ✅ Not found scenario (say 555-123-4560)
- ✅ Denied claim (say 555-123-4568)
- ✅ Pending claim (say 555-123-4565)

**Want me to add the phone number capture enhancement?** It's a 5-minute change! 🚀
