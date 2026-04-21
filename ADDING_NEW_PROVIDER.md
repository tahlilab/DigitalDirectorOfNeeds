# Adding a New Provider - Implementation Guide

## 📋 Overview

This guide explains how to extend the **Digital Director of Needs** system to support additional insurance providers or product lines beyond John Hancock Long Term Care. The architecture is designed to be provider-agnostic and easily scalable.

---

## 🏗️ Current Provider Configuration

### John Hancock LTC (Current Implementation)

**Product Line:** Long Term Care Insurance  
**Intents Supported:** 5 (CLAIM_STATUS, PAYMENT, COVERAGE_INQUIRY, RATE_INCREASE, AGENT_REQUEST)  
**Greeting:** "Thank you for calling John Hancock Long Term Care..."  
**Mock Data:** Phone-based lookup system  
**Deployment:** Render.com (Twilio webhook)

---

## 🆕 Adding a New Provider - Step-by-Step

### Option 1: New Product Line (Same Company)
**Example:** Adding John Hancock Life Insurance or Annuities

### Option 2: New Company
**Example:** Adding MetLife, Prudential, or Northwestern Mutual

### Option 3: Multi-Tenant System
**Example:** White-label solution for multiple insurance carriers

---

## 📝 Implementation Steps

### Step 1: Define Provider Configuration

Create a provider configuration file or database table:

```python
# providers_config.py

PROVIDERS = {
    'jh_ltc': {
        'name': 'John Hancock Long Term Care',
        'company': 'John Hancock',
        'product_line': 'Long Term Care',
        'greeting': 'Thank you for calling John Hancock Long Term Care. I\'m your digital assistant.',
        'phone_numbers': ['+19783077738'],  # Twilio numbers for this provider
        'intents': ['CLAIM_STATUS', 'PAYMENT', 'COVERAGE_INQUIRY', 'RATE_INCREASE', 'AGENT_REQUEST'],
        'transfer_number': '+18005551234',  # Agent queue
        'payment_ivr': '+18005554321',      # Payment system
        'branding': {
            'voice': 'Polly.Joanna-Neural',
            'hold_music': 'http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3'
        }
    },
    'jh_life': {
        'name': 'John Hancock Life Insurance',
        'company': 'John Hancock',
        'product_line': 'Life Insurance',
        'greeting': 'Thank you for calling John Hancock Life Insurance. How can I help you today?',
        'phone_numbers': ['+19783077739'],
        'intents': ['CLAIM_STATUS', 'PAYMENT', 'POLICY_INQUIRY', 'BENEFICIARY_CHANGE', 'AGENT_REQUEST'],
        'transfer_number': '+18005551235',
        'payment_ivr': '+18005554322',
        'branding': {
            'voice': 'Polly.Joanna-Neural',
            'hold_music': 'http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3'
        }
    },
    'metlife_dental': {
        'name': 'MetLife Dental',
        'company': 'MetLife',
        'product_line': 'Dental Insurance',
        'greeting': 'Thank you for calling MetLife Dental. What can I help you with?',
        'phone_numbers': ['+19783077740'],
        'intents': ['CLAIM_STATUS', 'PAYMENT', 'FIND_DENTIST', 'COVERAGE_INQUIRY', 'AGENT_REQUEST'],
        'transfer_number': '+18005551236',
        'payment_ivr': '+18005554323',
        'branding': {
            'voice': 'Polly.Matthew-Neural',  # Different voice for different brand
            'hold_music': 'https://example.com/metlife-hold-music.mp3'
        }
    }
}

def get_provider_by_phone(phone_number: str) -> dict:
    """Get provider config based on called phone number"""
    for provider_id, config in PROVIDERS.items():
        if phone_number in config['phone_numbers']:
            return {'id': provider_id, **config}
    return None

def get_provider_by_id(provider_id: str) -> dict:
    """Get provider config by ID"""
    return PROVIDERS.get(provider_id)
```

---

### Step 2: Update Twilio Webhook for Multi-Provider Support

Modify `twilio_webhook.py` to detect and route based on provider:

```python
# twilio_webhook.py

from providers_config import get_provider_by_phone, PROVIDERS

@app.route("/voice", methods=['POST'])
def voice_greeting():
    """
    Initial greeting - now provider-aware
    """
    call_sid = request.values.get('CallSid', '')
    from_number = request.values.get('From', '')
    to_number = request.values.get('To', '')  # Which Twilio number was called
    
    print(f"\n📞 New call from {from_number} to {to_number}")
    
    # Determine provider based on called number
    provider = get_provider_by_phone(to_number)
    
    if not provider:
        # Fallback to default (JH LTC)
        provider = get_provider_by_id('jh_ltc')
    
    # Initialize session with provider context
    sessions[call_sid] = {
        'from': from_number,
        'to': to_number,
        'provider_id': provider['id'],
        'provider_name': provider['name'],
        'step': 'greeting',
        'start_time': datetime.now().isoformat()
    }
    
    resp = VoiceResponse()
    
    # Provider-specific greeting
    gather = resp.gather(
        input='speech dtmf',
        action='/process-intent',
        timeout=3,
        speech_timeout='auto',
        language='en-US',
        num_digits=1
    )
    
    # Use provider's greeting and voice
    gather.say(
        provider['greeting'] + " You can also press 1 for claims, 2 for payments, 3 for coverage, or 0 for an agent.",
        voice=provider['branding']['voice']
    )
    
    resp.redirect('/no-input-handler')
    
    return str(resp)
```

---

### Step 3: Add Provider-Specific Intents

Create new intent handlers for provider-specific needs:

```python
# lambda/gpt4o_intent_classifier.py

# Add to intent_patterns dictionary

intent_patterns = {
    # Existing intents...
    'CLAIM_STATUS': [...],
    'PAYMENT': [...],
    
    # Life Insurance specific intents
    'BENEFICIARY_CHANGE': [
        r'change.*beneficiary',
        r'update.*beneficiary',
        r'beneficiary.*form',
        r'add.*beneficiary',
        r'remove.*beneficiary'
    ],
    
    'POLICY_INQUIRY': [
        r'cash.*value',
        r'surrender.*value',
        r'policy.*loan',
        r'borrow.*against.*policy',
        r'death.*benefit',
        r'face.*amount'
    ],
    
    # Dental Insurance specific intents
    'FIND_DENTIST': [
        r'find.*dentist',
        r'dentist.*near.*me',
        r'in.*network.*dentist',
        r'provider.*search',
        r'dental.*office'
    ],
    
    'PRE_AUTHORIZATION': [
        r'pre.*auth',
        r'prior.*authorization',
        r'approval.*needed',
        r'pre.*approval'
    ]
}

# Add provider-specific intent routing
def get_provider_intents(provider_id: str) -> list:
    """Get supported intents for a provider"""
    return PROVIDERS[provider_id]['intents']

def classify_with_rules(utterance: str, provider_id: str = 'jh_ltc') -> Dict[str, Any]:
    """
    Enhanced classifier with provider context
    """
    utterance_lower = utterance.lower()
    
    # Get supported intents for this provider
    supported_intents = get_provider_intents(provider_id)
    
    # Only check patterns for supported intents
    for intent in supported_intents:
        patterns = intent_patterns.get(intent, [])
        for pattern in patterns:
            if re.search(pattern, utterance_lower):
                intent_name = intent
                confidence = 0.85 + (len(re.findall(pattern, utterance_lower)) * 0.05)
                confidence = min(confidence, 0.98)
                break
        if intent_name != 'UNKNOWN':
            break
    
    # Rest of classification logic...
    return result
```

---

### Step 4: Create Provider-Specific Self-Service Handlers

Add new handlers in `lambda/self_service_automation.py`:

```python
# lambda/self_service_automation.py

# Add to handlers dictionary
handlers = {
    'CLAIM_STATUS': handle_claim_status,
    'PAYMENT': handle_payment,
    'COVERAGE_INQUIRY': handle_coverage,
    'RATE_INCREASE': handle_rate_increase,
    
    # Life Insurance handlers
    'BENEFICIARY_CHANGE': handle_beneficiary_change,
    'POLICY_INQUIRY': handle_policy_inquiry,
    
    # Dental Insurance handlers
    'FIND_DENTIST': handle_find_dentist,
    'PRE_AUTHORIZATION': handle_pre_authorization
}

def handle_beneficiary_change(phone: str, params: Dict) -> Dict[str, Any]:
    """
    Life Insurance - Beneficiary change request
    """
    message = (
        "To change your beneficiary, you'll need to complete a Beneficiary Change Form. "
        "I can email you the form, or you can download it from our website at johnhancocklife.com. "
        "The form requires your signature and must be mailed to our processing center. "
        "Once received, changes are typically processed within 5 to 7 business days. "
        "Would you like me to email you the form now, or would you prefer to speak with an agent?"
    )
    
    return {
        'responseMessage': message,
        'success': True,
        'requiresAgent': True  # Follow-up needed
    }

def handle_find_dentist(phone: str, params: Dict) -> Dict[str, Any]:
    """
    Dental Insurance - Find in-network dentist
    """
    # In production: integrate with provider search API
    message = (
        "To find an in-network dentist near you, visit our provider search tool at metlifedental.com/find-a-dentist. "
        "You can search by zip code, dentist name, or specialty. "
        "You can also call our automated provider line at 1-800-555-DENT, available 24/7. "
        "Would you like me to text you a link to the provider search tool?"
    )
    
    return {
        'responseMessage': message,
        'success': True,
        'smsLink': 'https://metlifedental.com/find-a-dentist'
    }

def handle_policy_inquiry(phone: str, params: Dict) -> Dict[str, Any]:
    """
    Life Insurance - Cash value / policy loan inquiry
    """
    # Mock data - replace with real policy lookup
    policy_data = mock_policy_lookup(phone)
    
    message = (
        f"Your whole life policy number {policy_data['policyNumber']} has a current cash value of ${policy_data['cashValue']:,.2f}. "
        f"Your death benefit is ${policy_data['deathBenefit']:,.2f}. "
        f"You can borrow up to 90% of your cash value, which is ${policy_data['maxLoan']:,.2f}. "
        f"Policy loans have an annual interest rate of {policy_data['loanRate']}%. "
        f"Would you like to speak with a specialist about taking a policy loan?"
    )
    
    return {
        'responseMessage': message,
        'success': True
    }
```

---

### Step 5: Update Mock Data System for New Providers

Extend mock data functions to support multiple providers:

```python
# lambda/self_service_automation.py

def mock_claim_lookup(phone: str, provider_id: str = 'jh_ltc') -> Dict:
    """
    Provider-specific mock claim data
    """
    last_digit = phone[-1]
    
    if provider_id == 'jh_ltc':
        # Long Term Care claims
        if last_digit in ['1', '2', '3']:
            return {
                'claimNumber': 'CR-2024-12345',
                'claimType': 'Nursing Home Care',
                'status': 'Approved',
                'amount': 15000,
                'submittedDate': 'March 15, 2024',
                'approvedDate': 'April 10, 2024',
                'checkMailed': True,
                'checkMailedDate': 'April 18, 2024'
            }
    
    elif provider_id == 'jh_life':
        # Life Insurance claims (death benefit)
        if last_digit in ['1', '2', '3']:
            return {
                'claimNumber': 'LC-2024-98765',
                'claimType': 'Death Benefit',
                'status': 'In Review',
                'amount': 500000,
                'submittedDate': 'April 1, 2024',
                'documentsNeeded': ['Death Certificate', 'Claim Form']
            }
    
    elif provider_id == 'metlife_dental':
        # Dental claims
        if last_digit in ['1', '2', '3']:
            return {
                'claimNumber': 'DC-2024-54321',
                'claimType': 'Dental Cleaning',
                'status': 'Approved',
                'amount': 120,
                'submittedDate': 'April 15, 2024',
                'approvedDate': 'April 17, 2024',
                'paidToProvider': True
            }
    
    return None

def mock_payment_lookup(phone: str, provider_id: str = 'jh_ltc') -> Dict:
    """
    Provider-specific payment data
    """
    if provider_id == 'jh_ltc':
        return {
            'premiumAmount': 450.00,
            'dueDate': '2024-05-01',
            'lastPaymentDate': '2024-04-01',
            'autopay': False,
            'productType': 'Long Term Care'
        }
    
    elif provider_id == 'jh_life':
        return {
            'premiumAmount': 125.00,
            'dueDate': '2024-05-15',
            'lastPaymentDate': '2024-04-15',
            'autopay': True,
            'productType': 'Whole Life',
            'dividendOption': 'Paid Up Additions'
        }
    
    elif provider_id == 'metlife_dental':
        return {
            'premiumAmount': 45.00,
            'dueDate': '2024-05-01',
            'lastPaymentDate': '2024-04-01',
            'autopay': True,
            'productType': 'Dental PPO',
            'employerPaid': True,
            'employeeContribution': 15.00
        }
```

---

### Step 6: Update Transfer Agent Route for Provider-Specific Queues

```python
# twilio_webhook.py

@app.route("/transfer-agent", methods=['GET', 'POST'])
def transfer_agent():
    """
    Transfer to agent - now provider-aware
    """
    call_sid = request.values.get('CallSid', '')
    
    # Get provider context from session
    provider_id = sessions[call_sid].get('provider_id', 'jh_ltc')
    provider = get_provider_by_id(provider_id)
    
    resp = VoiceResponse()
    
    gather = resp.gather(
        input='speech dtmf',
        action='/process-transfer-choice',
        timeout=5,
        num_digits=1,
        speech_timeout='auto'
    )
    
    gather.say(
        f"I can connect you with a {provider['name']} specialist now. "
        "Current wait time is approximately 3 to 5 minutes. "
        "Press 1 to hold, or press 2 to request a callback within the next hour.",
        voice=provider['branding']['voice']
    )
    
    resp.redirect('/process-transfer-choice?Digits=1')
    
    return str(resp)

@app.route("/process-transfer-choice", methods=['GET', 'POST'])
def process_transfer_choice():
    """
    Handle transfer with provider-specific routing
    """
    response = request.values.get('Digits', '1')
    call_sid = request.values.get('CallSid', '')
    
    provider_id = sessions[call_sid].get('provider_id', 'jh_ltc')
    provider = get_provider_by_id(provider_id)
    
    resp = VoiceResponse()
    
    if '2' in response:
        # Callback option
        resp.say(
            f"Perfect! A {provider['name']} specialist will call you back within the next hour.",
            voice=provider['branding']['voice']
        )
        resp.hangup()
        return str(resp)
    else:
        # Transfer to provider-specific agent queue
        resp.say(
            "Thank you for holding. Let me connect you now.",
            voice=provider['branding']['voice']
        )
        
        # In production: dial provider's actual transfer number
        # resp.dial(provider['transfer_number'])
        
        # For demo: play provider-specific hold music
        resp.play(provider['branding']['hold_music'])
        resp.pause(length=5)
        resp.say("An agent will be with you shortly.", voice=provider['branding']['voice'])
        resp.redirect('/goodbye')
        
        return str(resp)
```

---

### Step 7: Database Schema for Multi-Provider (Production)

For production, use a database instead of config files:

```sql
-- providers table
CREATE TABLE providers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    company VARCHAR(200) NOT NULL,
    product_line VARCHAR(100) NOT NULL,
    greeting TEXT NOT NULL,
    transfer_number VARCHAR(20),
    payment_ivr VARCHAR(20),
    voice_name VARCHAR(50) DEFAULT 'Polly.Joanna-Neural',
    hold_music_url TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- provider_phone_numbers table
CREATE TABLE provider_phone_numbers (
    id SERIAL PRIMARY KEY,
    provider_id VARCHAR(50) REFERENCES providers(id),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

-- provider_intents table
CREATE TABLE provider_intents (
    id SERIAL PRIMARY KEY,
    provider_id VARCHAR(50) REFERENCES providers(id),
    intent_name VARCHAR(50) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    UNIQUE(provider_id, intent_name)
);

-- Insert example data
INSERT INTO providers (id, name, company, product_line, greeting, transfer_number) VALUES
('jh_ltc', 'John Hancock Long Term Care', 'John Hancock', 'Long Term Care', 
 'Thank you for calling John Hancock Long Term Care...', '+18005551234'),
('jh_life', 'John Hancock Life Insurance', 'John Hancock', 'Life Insurance',
 'Thank you for calling John Hancock Life Insurance...', '+18005551235'),
('metlife_dental', 'MetLife Dental', 'MetLife', 'Dental Insurance',
 'Thank you for calling MetLife Dental...', '+18005551236');

INSERT INTO provider_phone_numbers (provider_id, phone_number) VALUES
('jh_ltc', '+19783077738'),
('jh_life', '+19783077739'),
('metlife_dental', '+19783077740');

INSERT INTO provider_intents (provider_id, intent_name) VALUES
('jh_ltc', 'CLAIM_STATUS'),
('jh_ltc', 'PAYMENT'),
('jh_ltc', 'COVERAGE_INQUIRY'),
('jh_ltc', 'RATE_INCREASE'),
('jh_life', 'CLAIM_STATUS'),
('jh_life', 'PAYMENT'),
('jh_life', 'BENEFICIARY_CHANGE'),
('jh_life', 'POLICY_INQUIRY'),
('metlife_dental', 'CLAIM_STATUS'),
('metlife_dental', 'FIND_DENTIST'),
('metlife_dental', 'PRE_AUTHORIZATION');
```

---

## 🔧 Configuration Checklist

### Adding a New Provider - Complete Checklist

- [ ] **1. Provider Configuration**
  - [ ] Add to `PROVIDERS` dict in `providers_config.py`
  - [ ] Define name, company, product line
  - [ ] Set greeting message
  - [ ] Configure phone numbers
  - [ ] List supported intents
  - [ ] Set transfer numbers (agent queue, payment IVR)
  - [ ] Configure branding (voice, hold music)

- [ ] **2. Twilio Setup**
  - [ ] Purchase Twilio phone number(s)
  - [ ] Configure webhook URL
  - [ ] Test phone number routing

- [ ] **3. Intent Definitions**
  - [ ] Add provider-specific intent patterns
  - [ ] Update `intent_patterns` dict
  - [ ] Test pattern matching
  - [ ] Document new intents

- [ ] **4. Self-Service Handlers**
  - [ ] Create handler functions
  - [ ] Add to `handlers` dict
  - [ ] Implement mock data
  - [ ] Test responses

- [ ] **5. Mock Data**
  - [ ] Create provider-specific lookup functions
  - [ ] Add phone-based test scenarios
  - [ ] Document test phone numbers

- [ ] **6. AI Recommendations**
  - [ ] Add intent-specific recommendations
  - [ ] Test sentiment detection
  - [ ] Validate educational content

- [ ] **7. Testing**
  - [ ] Test each intent via phone
  - [ ] Verify routing works correctly
  - [ ] Check greeting is correct
  - [ ] Test agent transfer
  - [ ] Test payment flow
  - [ ] Verify callback option

- [ ] **8. Production Integration**
  - [ ] Replace mock data with real API calls
  - [ ] Configure Salesforce/CRM integration
  - [ ] Set up database (if using multi-tenant)
  - [ ] Configure environment variables
  - [ ] Deploy to production

---

## 📊 Example: Adding MetLife Dental

### Complete Implementation

**File: `providers_config.py`**
```python
'metlife_dental': {
    'name': 'MetLife Dental',
    'company': 'MetLife',
    'product_line': 'Dental Insurance',
    'greeting': 'Thank you for calling MetLife Dental. What can I help you with?',
    'phone_numbers': ['+19783077740'],
    'intents': ['CLAIM_STATUS', 'PAYMENT', 'FIND_DENTIST', 'PRE_AUTHORIZATION', 'AGENT_REQUEST'],
    'transfer_number': '+18005551236',
    'payment_ivr': '+18005554323',
    'branding': {
        'voice': 'Polly.Matthew-Neural',
        'hold_music': 'https://example.com/metlife-hold.mp3'
    }
}
```

**File: `lambda/gpt4o_intent_classifier.py`**
```python
# Add MetLife-specific intents
'FIND_DENTIST': [
    r'find.*dentist',
    r'dentist.*near.*me',
    r'in.*network.*dentist',
    r'provider.*search',
    r'dental.*office',
    r'accept.*my.*insurance'
],
'PRE_AUTHORIZATION': [
    r'pre.*auth',
    r'prior.*authorization',
    r'approval.*needed',
    r'get.*approved',
    r'pre.*approval'
]
```

**File: `lambda/self_service_automation.py`**
```python
def handle_find_dentist(phone: str, params: Dict) -> Dict[str, Any]:
    message = (
        "To find an in-network dentist, visit metlifedental.com/find-a-dentist or "
        "call our automated line at 1-800-555-DENT. "
        "Would you like me to text you the provider search link?"
    )
    return {'responseMessage': message, 'success': True}
```

**Test:**
```bash
# Call +19783077740
# Say: "I need to find a dentist"
# Expected: Provider search instructions
```

---

## 🚀 Deployment for Multiple Providers

### Render.com (Current)
- Deploy single webhook handling all providers
- Route based on `To` number (which Twilio number was called)
- Environment variables for provider-specific settings

### AWS Lambda (Production)
- Option 1: Single Lambda with provider routing
- Option 2: Separate Lambda per provider (isolated deployments)
- Option 3: API Gateway routing to provider-specific Lambdas

### Amazon Connect (Enterprise)
- Separate Connect instances per provider
- Or single instance with DID-based routing
- Provider context passed to Lambdas

---

## 🎯 Best Practices

1. **Separation of Concerns**
   - Keep provider config separate from business logic
   - Use dependency injection for provider context
   - Make handlers provider-agnostic where possible

2. **Consistent Patterns**
   - Use same intent names across providers when possible
   - Standardize response formats
   - Reuse existing handlers before creating new ones

3. **Branding Flexibility**
   - Allow custom greetings, voices, hold music
   - Provider-specific terminology
   - Logo/colors for future web/SMS integrations

4. **Testing**
   - Create provider-specific test suites
   - Mock data for each provider
   - Regression testing when adding new providers

5. **Documentation**
   - Document each provider's intents
   - Maintain provider contact info
   - Track deployment dates and versions

---

## 📞 Testing New Providers

### Test Call Script
```
1. Call provider's phone number
2. Verify correct greeting plays
3. Test quick menu (press 1, 2, 3, 0)
4. Test speech recognition for each intent
5. Verify agent transfer routes to correct queue
6. Test callback option
7. Confirm hold music is provider-specific
8. Test payment flow (if applicable)
```

### Validation Checklist
- [ ] Correct greeting
- [ ] Correct voice
- [ ] All intents working
- [ ] Mock data returns provider-specific info
- [ ] Transfer number is correct
- [ ] Payment IVR is correct (if applicable)
- [ ] Branding elements correct (music, terminology)

---

## 🔮 Future Enhancements

### Multi-Language Support
```python
'provider_config': {
    'languages': ['en', 'es'],
    'greetings': {
        'en': 'Thank you for calling...',
        'es': 'Gracias por llamar...'
    }
}
```

### Provider Analytics
- Track calls by provider
- Intent distribution per provider
- Self-service rate by provider
- CSAT scores by provider

### White-Label Platform
- Provider admin portal
- Self-service provider configuration
- Usage-based billing
- Custom domain support

---

## 📄 Summary

Adding a new provider requires:
1. **Configuration:** Define provider in `providers_config.py`
2. **Routing:** Update webhook to detect provider via phone number
3. **Intents:** Add provider-specific intent patterns
4. **Handlers:** Create self-service automation functions
5. **Testing:** Validate all flows work correctly
6. **Deployment:** Deploy to production environment

**Time Estimate:** 4-8 hours per provider (depending on complexity)

**Effort Breakdown:**
- Configuration: 1 hour
- Intent patterns: 2 hours
- Self-service handlers: 2-3 hours
- Testing: 1-2 hours
- Documentation: 1 hour

---

**Last Updated:** April 21, 2026  
**Related Documents:** PROJECT_SUMMARY.md, README.md
