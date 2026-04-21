# Rate Increase Intent Fix

## Issue
When testing "Why is my premium increasing?" the system was routing to an agent instead of providing self-service response.

## Root Cause
**File:** `lambda/gpt4o_intent_classifier.py`

**Line 255:** The `can_self_service()` function had:
```python
self_serve_intents = ['CLAIM_STATUS', 'PAYMENT', 'COVERAGE_INQUIRY']
```

❌ **Missing:** `'RATE_INCREASE'` was not in the self-serviceable intents list!

Even though we created the handler in `self_service_automation.py`, the intent classifier was marking `canSelfServe: 'false'`, causing the webhook to route to agent transfer instead of self-service.

## Fix Applied

### 1. Added RATE_INCREASE to Self-Serviceable Intents
**Line 255:**
```python
self_serve_intents = ['CLAIM_STATUS', 'PAYMENT', 'COVERAGE_INQUIRY', 'RATE_INCREASE']
```

### 2. Improved Regex Patterns for Better Detection
**Lines 93-101:** Added more patterns to catch variations:
```python
'RATE_INCREASE': [
    r'rate.*increase',
    r'premium.*went up',
    r'premium.*increase',      # NEW
    r'premium.*increasing',    # NEW - catches "Why is my premium increasing?"
    r'letter.*rate',
    r'why.*higher',
    r'why.*premium',           # NEW
    r'cost.*more',             # NEW
    r'price.*increase'         # NEW
],
```

## Testing Results ✅

All rate increase queries now correctly classified as self-serviceable:

| Query | Intent | Confidence | Can Self-Serve |
|-------|--------|------------|----------------|
| "Why is my premium increasing?" | RATE_INCREASE | 90% | ✅ true |
| "I got a letter about a rate increase" | RATE_INCREASE | 90% | ✅ true |
| "Why did my premium go up?" | RATE_INCREASE | 90% | ✅ true |
| "My policy costs more now" | RATE_INCREASE | 90% | ✅ true |

## Expected Call Flow Now

```
1. User: "Why is my premium increasing?"
2. /voice → Greeting
3. /process-intent → GPT-4o classifies as RATE_INCREASE (90% confidence, canSelfServe: true)
4. /self-service → handle_rate_increase()
5. Response: "Your current monthly premium is $285.00. Your premium will be increasing 
   by 8% to $307.80, effective July 1st, 2026. A detailed explanation was mailed to you..."
6. /anything-else → Continue or end
7. /goodbye → End call
```

## Mock Data Behavior

**Phone numbers ending in 1-3:** Have rate increase
- Current: $285.00
- New: $307.80 (8% increase)
- Effective: July 1st, 2026

**Phone numbers ending in 4-9, 0:** No rate increase
- Current: $285.00
- Response: "You do not have any scheduled rate increases at this time."

## Deployment

✅ **Committed:** 101c355  
✅ **Pushed:** to GitHub main branch  
⏳ **Render:** Auto-deploying now

## Testing Next Steps

Your test number **(978) 307-7738** ends in **8**, so you'll get:
- **Response:** "Your current monthly premium is $285.00. You do not have any scheduled rate increases at this time. If you have specific questions about premium rates, I'd be happy to connect you with a specialist."

**To test the rate increase scenario:**
- You can use a test number ending in 1, 2, or 3
- Or we can modify the mock data to trigger the increase for your number

## Status

🟢 **FIXED** - Rate increase queries now properly self-serve instead of routing to agent!
