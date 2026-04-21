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
    utterance_lower = utterance.lower()
    
    # Intent patterns
    intent_patterns = {
        'CLAIM_STATUS': [
            r'claim\s+status',
            r'check.*claim',
            r'where.*claim',
            r'claim.*approved',
            r'claim.*paid',
            r'reimbursement'
        ],
        'PAYMENT': [
            r'pay.*premium',
            r'make.*payment',
            r'how.*pay',
            r'bill.*due',
            r'payment.*due'
        ],
        'COVERAGE_INQUIRY': [
            r'coverage',
            r'what.*covered',
            r'benefits',
            r'policy.*details',
            r'how much.*cover'
        ],
        'RATE_INCREASE': [
            r'rate.*increase',
            r'premium.*went up',
            r'premium.*increase',
            r'premium.*increasing',
            r'letter.*rate',
            r'why.*higher',
            r'why.*premium',
            r'cost.*more',
            r'price.*increase'
        ],
        'AGENT_REQUEST': [
            r'speak.*agent',
            r'talk.*person',
            r'representative',
            r'speak.*someone'
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
    
    # Determine auth tier needed
    auth_tier = determine_auth_tier(intent_name, relationship)
    
    # Determine if can self-serve
    can_self_serve = can_self_service(intent_name, confidence, relationship)
    
    # Extract entities
    entity = extract_entity(utterance_lower, intent_name)
    
    # Detect sentiment
    sentiment = detect_sentiment(utterance_lower)
    
    return {
        'intentName': intent_name,
        'confidence': str(round(confidence * 100)),
        'relationship': relationship,
        'callType': call_type,
        'authTier': str(auth_tier),
        'entity': entity,
        'sentiment': sentiment,
        'canSelfServe': 'true' if can_self_serve else 'false',
        'utterance': utterance
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
    self_serve_intents = ['CLAIM_STATUS', 'PAYMENT', 'COVERAGE_INQUIRY', 'RATE_INCREASE']
    
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
