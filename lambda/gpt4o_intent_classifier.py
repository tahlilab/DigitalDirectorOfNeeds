"""
GPT-4o Intent Classifier Lambda Function
Simulates Azure OpenAI GPT-4o call for intent classification

For local testing, set:
export AZURE_OPENAI_ENDPOINT="your-endpoint"
export AZURE_OPENAI_KEY="your-key"
"""

import json
import os
import re
from typing import Dict, Any

# For production: use Azure OpenAI SDK
# from openai import AzureOpenAI

def lambda_handler(event, context):
    """
    Main Lambda handler for intent classification
    
    Input (from Amazon Connect):
    {
        "utterance": "I need to check my claim status",
        "transcription": "I need to check my claim status",
        "phoneNumber": "+15551234567"
    }
    
    Output (to Amazon Connect):
    {
        "intentName": "CLAIM_STATUS",
        "confidence": 0.95,
        "relationship": "owner",
        "callType": "Owner",
        "authTier": "2",
        "entity": "claim",
        "sentiment": "neutral",
        "canSelfServe": "true"
    }
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # Extract parameters from Amazon Connect
    params = event.get('Details', {}).get('Parameters', {})
    utterance = params.get('transcription', params.get('utterance', ''))
    
    if not utterance:
        return error_response("No utterance provided")
    
    # For demo/testing: Use rule-based classification
    # For production: Replace with actual GPT-4o call
    if os.getenv('USE_GPT4O') == 'true':
        result = classify_with_gpt4o(utterance)
    else:
        result = classify_with_rules(utterance)
    
    print(f"Classification result: {json.dumps(result)}")
    return result


def classify_with_rules(utterance: str) -> Dict[str, Any]:
    """
    Rule-based classifier for local testing
    Simulates GPT-4o responses
    """
    utterance_lower = utterance.lower().strip().rstrip('.!?,')
    
    # Intent patterns
    intent_patterns = {
        'CLAIM_STATUS': [
            # Single-word match (for clarification responses)
            r'^(a |my |the )?claims?$',
            # Core patterns
            r'claim\s+status',
            r'check.*claim',
            r'where.*claim',
            r'claim.*approved',
            r'claim.*paid',
            r'reimbursement',
            # Adjacent wordings - submission/tracking
            r'submit.*claim',
            r'filed.*claim',
            r'claim.*processing',
            r'claim.*pending',
            r'claim.*denied',
            r'claim.*rejected',
            # Adjacent wordings - payments
            r'where.*money',
            r'where.*check',
            r'reimbursement.*status',
            r'payment.*claim',
            r'claim.*payment',
            # Adjacent wordings - timeframes
            r'how long.*claim',
            r'when.*claim',
            r'claim.*take',
            # Natural language variations
            r'submitted.*claim.*status',
            r'claim.*number',
            r'track.*claim',
            r'follow.*claim'
        ],
        'PAYMENT': [
            # Single-word match (for clarification responses)
            r'^(a |my |the )?payments?$',
            r'^billing$',
            r'^(my )?premium$',
            # Core patterns
            r'pay.*premium',
            r'make.*payment',
            r'how.*pay',
            r'bill.*due',
            r'payment.*due',
            # Adjacent wordings - due dates
            r'when.*due',
            r'due.*date',
            r'next.*payment',
            r'upcoming.*payment',
            # Adjacent wordings - amounts
            r'how much.*owe',
            r'amount.*due',
            r'premium.*amount',
            r'bill.*amount',
            r'monthly.*premium',
            # Adjacent wordings - payment methods
            r'pay.*online',
            r'pay.*phone',
            r'autopay',
            r'automatic.*payment',
            r'set.*up.*payment',
            # Adjacent wordings - late/overdue
            r'late.*payment',
            r'overdue',
            r'missed.*payment',
            r'past.*due',
            # Natural language variations
            r'need.*pay',
            r'want.*pay',
            r'payment.*options',
            r'pay.*bill'
        ],
        'COVERAGE_INQUIRY': [
            # Core patterns
            r'coverage',
            r'what.*covered',
            r'benefits',
            r'policy.*details',
            r'how much.*cover',
            # Adjacent wordings - policy details
            r'my.*policy',
            r'policy.*information',
            r'what.*does.*policy',
            r'explain.*policy',
            r'understand.*policy',
            # Adjacent wordings - benefits
            r'daily.*benefit',
            r'lifetime.*benefit',
            r'maximum.*benefit',
            r'benefit.*amount',
            r'benefit.*period',
            # Adjacent wordings - care types
            r'nursing.*home.*cover',
            r'home.*care.*cover',
            r'assisted.*living.*cover',
            r'what.*care.*covered',
            # Adjacent wordings - specifics
            r'elimination.*period',
            r'waiting.*period',
            r'inflation.*protection',
            r'compound.*inflation',
            # Natural language variations
            r'tell.*about.*policy',
            r'policy.*pay',
            r'coverage.*details',
            r'what.*am.*i.*covered'
        ],
        'RATE_INCREASE': [
            # Single-word match (for clarification responses)
            r'^(a |my |the )?rates?$',
            r'^rate (increase|change|hike)$',
            # Core patterns
            r'rate.*increase',
            r'rate.*go.*up',
            r'rate.*went.*up',
            r'rate.*higher',
            r'premium.*went up',
            r'premium.*increase',
            r'premium.*increasing',
            r'premium.*go.*up',
            r'premium.*higher',
            r'letter.*rate',
            r'why.*higher',
            r'why.*premium',
            r'cost.*more',
            r'price.*increase',
            # Adjacent wordings - rate changes
            r'rate.*change',
            r'premium.*change',
            r'rate.*adjustment',
            r'premium.*adjustment',
            r'rate.*hike',
            # Adjacent wordings - cost concerns
            r'cost.*went.*up',
            r'price.*went.*up',
            r'more.*expensive',
            r'paying.*more',
            r'charged.*more',
            # Adjacent wordings - notifications
            r'letter.*premium',
            r'notice.*rate',
            r'notice.*premium',
            r'notice.*increase',
            r'received.*letter.*rate',
            # Adjacent wordings - questions
            r'why.*cost',
            r'why.*increase',
            r'explain.*increase',
            r'reason.*increase',
            # Natural language variations
            r'premium.*more',
            r'bill.*higher',
            r'bill.*went.*up',
            r'bill.*go.*up',
            r'bill.*increase',
            r'why.*bill.*up',
            r'why.*bill.*more'
        ],
        'PROVIDER_REFERRAL': [
            # Single-word match (for clarification responses)
            r'^(a |my |the )?providers?$',
            # Core patterns
            r'find.*provider',
            r'need.*provider',
            r'looking.*provider',
            r'search.*provider',
            r'provider.*referral',
            # Adjacent wordings - finding care
            r'find.*doctor',
            r'find.*facility',
            r'find.*nursing.*home',
            r'find.*home.*care',
            r'find.*assisted.*living',
            r'find.*care.*facility',
            # Adjacent wordings - need help finding
            r'need.*help.*finding',
            r'looking.*for.*care',
            r'search.*for.*care',
            r'where.*can.*i.*find',
            # Adjacent wordings - specific providers
            r'recommend.*provider',
            r'suggest.*provider',
            r'list.*of.*providers',
            r'approved.*providers',
            r'in.*network.*providers',
            # Natural language variations
            r'who.*can.*help.*me',
            r'where.*to.*go',
            r'need.*care.*provider',
            r'looking.*for.*help',
            # Care facility / nursing home mentions (without "find")
            r'care.*facility',
            r'nursing.*home',
            r'assisted.*living',
            r'home.*care',
            r'home.*health',
            r'adult.*day.*care',
            r'respite.*care',
            r'long.*term.*care.*facility',
            r'rehab.*facility',
            r'skilled.*nursing',
            # Need-based patterns
            r'need.*facility',
            r'need.*nursing',
            r'need.*care',
            r'need.*home.*care',
            r'need.*assisted',
            r'looking.*facility',
            r'looking.*nursing',
            r'looking.*assisted',
            # Help with care
            r'help.*finding.*care',
            r'help.*finding.*provider',
            r'help.*find.*care',
            r'help.*find.*provider',
            r'help.*with.*care',
            r'where.*do.*i.*go',
            r'how.*do.*i.*find',
            # Add/get a provider
            r'add.*provider',
            r'get.*provider',
            r'add.*a.*provider',
            r'get.*a.*provider',
            # Helper Bees specific
            r'helper.*bees',
            r'referral',
            r'provider.*network'
        ],
        'AGENT_REQUEST': [
            # Single-word match (for clarification responses)
            r'^(an )?agent$',
            r'^(a )?(real |live )?person$',
            # Core patterns
            r'speak.*agent',
            r'talk.*person',
            r'representative',
            r'speak.*someone',
            # Adjacent wordings - direct requests
            r'talk.*agent',
            r'speak.*rep',
            r'human',
            r'real.*person',
            r'live.*person',
            # Adjacent wordings - transfers
            r'transfer.*agent',
            r'connect.*agent',
            r'transfer.*person',
            r'connect.*person',
            # Adjacent wordings - specialists
            r'specialist',
            r'supervisor',
            r'manager',
            r'customer.*service',
            # Natural language variations
            r'need.*help.*person',
            r'talk.*someone',
            r'speak.*representative',
            r'get.*agent'
        ]
    }
    
    # Relationship patterns
    relationship_patterns = {
        'third_party': [
            r'my\s+(mother|father|mom|dad|parent)',
            r'calling\s+for',
            r'on\s+behalf',
            r'power\s+of\s+attorney',
            r'POA'
        ],
        'agent': [
            r'i\'m\s+an?\s+agent',
            r'agent\s+commission',
            r'my\s+client'
        ]
    }
    
    # Detect intent
    intent_name = 'UNKNOWN'
    confidence = 0.50
    
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if re.search(pattern, utterance_lower):
                intent_name = intent
                confidence = 0.85 + (len(re.findall(pattern, utterance_lower)) * 0.05)
                confidence = min(confidence, 0.98)
                break
        if intent_name != 'UNKNOWN':
            break
    
    # Detect relationship
    relationship = 'owner'  # default
    call_type = 'Owner'
    
    for rel, patterns in relationship_patterns.items():
        for pattern in patterns:
            if re.search(pattern, utterance_lower):
                relationship = rel
                if rel == 'third_party':
                    call_type = 'Other'
                elif rel == 'agent':
                    call_type = 'Agent'
                break
    
    # Detect provider sub-type (add vs find)
    provider_sub_type = 'find'
    if intent_name == 'PROVIDER_REFERRAL':
        add_patterns = [r'add.*provider', r'add.*a.*provider']
        for pattern in add_patterns:
            if re.search(pattern, utterance_lower):
                provider_sub_type = 'add'
                break

    # Determine auth tier needed
    auth_tier = determine_auth_tier(intent_name, relationship)
    
    # Determine if can self-serve
    can_self_serve = can_self_service(intent_name, confidence, relationship)
    
    # Extract entities
    entity = extract_entity(utterance_lower, intent_name)
    
    # Detect sentiment
    sentiment = detect_sentiment(utterance_lower)
    
    # Generate AI recommendations for next steps
    recommendations = generate_recommendations(intent_name, confidence, sentiment, relationship, can_self_serve)
    
    return {
        'intentName': intent_name,
        'confidence': str(round(confidence * 100)),
        'relationship': relationship,
        'callType': call_type,
        'authTier': str(auth_tier),
        'entity': entity,
        'sentiment': sentiment,
        'canSelfServe': 'true' if can_self_serve else 'false',
        'providerSubType': provider_sub_type,
        'utterance': utterance,
        'recommendations': recommendations
    }


def classify_with_gpt4o(utterance: str) -> Dict[str, Any]:
    """
    Actual GPT-4o classification (for production)
    """
    # Uncomment for production with Azure OpenAI
    """
    from openai import AzureOpenAI
    
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
    prompt = f'''
    Analyze this customer utterance and classify it:
    
    Utterance: "{utterance}"
    
    Return JSON with:
    - intentName: CLAIM_STATUS | PAYMENT | COVERAGE_INQUIRY | RATE_INCREASE | AGENT_REQUEST | UNKNOWN
    - confidence: 0-100
    - relationship: owner | third_party | agent | unknown
    - callType: Owner | Other | Agent
    - authTier: 1 (public) | 2 (light auth) | 3 (full auth)
    - entity: main noun (claim, payment, etc)
    - sentiment: positive | neutral | negative | frustrated
    - canSelfServe: true | false
    '''
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an insurance call center intent classifier."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    result = json.loads(response.choices[0].message.content)
    return result
    """
    
    # Fallback to rules if GPT-4o not configured
    return classify_with_rules(utterance)


def determine_auth_tier(intent: str, relationship: str) -> int:
    """
    Determine authentication tier needed
    
    Tier 1: Public info (no auth)
    Tier 2: Light auth (name + DOB)
    Tier 3: Full auth (POA required)
    """
    # Public info intents
    if intent in ['COVERAGE_INQUIRY']:
        return 1
    
    # Sensitive info intents
    if intent in ['CLAIM_STATUS', 'PAYMENT']:
        if relationship == 'third_party':
            return 3  # Need POA for third-party claim access
        else:
            return 2  # Owner can get with light auth
    
    # Default
    return 2


def can_self_service(intent: str, confidence: float, relationship: str) -> bool:
    """
    Determine if intent can be self-served
    """
    # High confidence required
    if confidence < 0.85:
        return False
    
    # Self-serviceable intents
    self_serve_intents = ['CLAIM_STATUS', 'PAYMENT', 'COVERAGE_INQUIRY', 'RATE_INCREASE', 'PROVIDER_REFERRAL']
    
    if intent not in self_serve_intents:
        return False
    
    # Third-party requires agent (for now)
    if relationship == 'third_party':
        return False
    
    return True


def extract_entity(utterance: str, intent: str) -> str:
    """
    Extract main entity from utterance
    """
    entity_patterns = {
        'claim': r'claim',
        'payment': r'pay|premium|bill',
        'coverage': r'coverage|benefit',
        'policy': r'policy'
    }
    
    for entity, pattern in entity_patterns.items():
        if re.search(pattern, utterance):
            return entity
    
    return 'unknown'


def detect_sentiment(utterance: str) -> str:
    """
    Simple sentiment detection
    """
    frustrated_words = ['frustrated', 'angry', 'waiting', 'forever', 'why', 'problem']
    positive_words = ['thank', 'great', 'good', 'appreciate']
    
    if any(word in utterance for word in frustrated_words):
        return 'frustrated'
    elif any(word in utterance for word in positive_words):
        return 'positive'
    else:
        return 'neutral'


def generate_recommendations(intent: str, confidence: float, sentiment: str, relationship: str, can_self_serve: bool) -> Dict[str, Any]:
    """
    Generate AI-powered recommendations for next steps before agent escalation
    """
    recommendations = {
        'primaryAction': '',
        'secondaryActions': [],
        'educationalContent': [],
        'escalationReason': '',
        'customerExperience': ''
    }
    
    # Intent-specific recommendations
    if intent == 'CLAIM_STATUS':
        recommendations['primaryAction'] = 'Provide real-time claim status with detailed tracking information'
        recommendations['secondaryActions'] = [
            'Offer proactive updates via email/SMS',
            'Explain next steps in claim process',
            'Provide estimated completion timeline'
        ]
        recommendations['educationalContent'] = [
            'Typical claim processing timeframes (7-14 business days)',
            'Required documentation checklist',
            'How to expedite claims if needed'
        ]
        if not can_self_serve:
            recommendations['escalationReason'] = 'Requires agent verification or complex claim inquiry'
        
    elif intent == 'PAYMENT':
        recommendations['primaryAction'] = 'Provide payment amount, due date, and multiple payment options'
        recommendations['secondaryActions'] = [
            'Offer to set up autopay',
            'Explain late payment consequences',
            'Provide grace period information'
        ]
        recommendations['educationalContent'] = [
            'Payment methods: online, phone, mail',
            'Autopay enrollment benefits',
            'Premium payment history access'
        ]
        if not can_self_serve:
            recommendations['escalationReason'] = 'Requires payment plan setup or billing dispute resolution'
    
    elif intent == 'COVERAGE_INQUIRY':
        recommendations['primaryAction'] = 'Explain policy benefits, daily limits, and coverage periods'
        recommendations['secondaryActions'] = [
            'Provide examples of covered care scenarios',
            'Explain elimination period and waiting periods',
            'Detail inflation protection benefits'
        ]
        recommendations['educationalContent'] = [
            'Types of care covered: nursing home, assisted living, home care',
            'Benefit triggers and qualification criteria',
            'How to file claims when care begins'
        ]
        if not can_self_serve:
            recommendations['escalationReason'] = 'Requires detailed policy interpretation or customization discussion'
    
    elif intent == 'RATE_INCREASE':
        recommendations['primaryAction'] = 'Explain rate increase reason, amount, and effective date transparently'
        recommendations['secondaryActions'] = [
            'Offer rate stability options (reduce benefits, longer elimination period)',
            'Explain industry-wide rate trends',
            'Provide comparison with original pricing disclosure'
        ]
        recommendations['educationalContent'] = [
            'Why LTC rates increase (healthcare costs, claims experience)',
            'Options to reduce premium while maintaining coverage',
            'State insurance department contact for rate questions'
        ]
        if sentiment == 'frustrated' or sentiment == 'angry':
            recommendations['customerExperience'] = 'Customer shows frustration - use empathetic language and offer flexible options'
        if not can_self_serve:
            recommendations['escalationReason'] = 'Customer needs personalized rate mitigation strategies or billing adjustment'
    
    elif intent == 'AGENT_REQUEST':
        recommendations['primaryAction'] = 'Transfer to appropriate specialist based on underlying need'
        recommendations['secondaryActions'] = [
            'Attempt to identify specific concern before transfer',
            'Route to specialized queue (claims, underwriting, billing)',
            'Provide estimated wait time'
        ]
        recommendations['escalationReason'] = 'Direct agent request or complex inquiry requiring human judgment'
    
    elif intent == 'UNKNOWN':
        recommendations['primaryAction'] = 'Ask clarifying question to understand customer need'
        recommendations['secondaryActions'] = [
            'Provide menu of common intents (claim, payment, coverage, rate)',
            'Use open-ended question to gather more context',
            'Offer to transfer to generalist agent if still unclear'
        ]
        recommendations['educationalContent'] = [
            'Common reasons customers call',
            'Self-service options available'
        ]
        recommendations['escalationReason'] = 'Intent unclear after clarification attempt'
    
    # Confidence-based adjustments
    if confidence < 0.70:
        recommendations['customerExperience'] = 'Low confidence - ask confirmation question before proceeding'
        recommendations['secondaryActions'].insert(0, 'Confirm understanding before providing detailed response')
    
    # Relationship-based adjustments
    if relationship == 'third_party':
        recommendations['primaryAction'] = 'Verify authorization before discussing protected health information'
        recommendations['secondaryActions'] = [
            'Request power of attorney documentation',
            'Verify relationship and consent',
            'Explain HIPAA privacy requirements'
        ]
        recommendations['escalationReason'] = 'Third-party caller requires authorization verification'
    
    # Sentiment-based adjustments
    if sentiment == 'angry' or sentiment == 'frustrated':
        recommendations['customerExperience'] = 'Customer shows negative emotion - prioritize empathy and de-escalation'
        recommendations['secondaryActions'].insert(0, 'Acknowledge concern and apologize for frustration')
    elif sentiment == 'urgent':
        recommendations['customerExperience'] = 'Time-sensitive issue - expedite response and offer priority handling'
    
    return recommendations


def error_response(message: str) -> Dict[str, Any]:
    """
    Return error response
    """
    return {
        'intentName': 'ERROR',
        'confidence': '0',
        'relationship': 'unknown',
        'callType': 'Unknown',
        'authTier': '2',
        'entity': 'error',
        'sentiment': 'neutral',
        'canSelfServe': 'false',
        'error': message
    }


# For local testing
if __name__ == '__main__':
    test_utterances = [
        "I need to check my claim status",
        "I want to pay my premium",
        "What's covered under my policy?",
        "I'm calling about my mother's claim",
        "I need to speak to an agent",
        "Why did my rate increase?"
    ]
    
    for utterance in test_utterances:
        event = {
            'Details': {
                'Parameters': {
                    'transcription': utterance
                }
            }
        }
        result = lambda_handler(event, None)
        print(f"\nUtterance: {utterance}")
        print(f"Result: {json.dumps(result, indent=2)}")
