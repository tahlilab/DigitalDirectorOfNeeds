"""
Twilio Voice Webhook for Testing AI Flow
Allows you to test the AI-enhanced flow by calling a Twilio phone number

Setup:
1. pip install flask twilio
2. Sign up at twilio.com (free trial)
3. Buy a phone number (~$1/month)
4. Run: python twilio_webhook.py
5. In another terminal: ngrok http 5000
6. Configure Twilio number webhook to ngrok URL
7. Call your Twilio number!
"""

from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse, Gather
import sys
import os
from pathlib import Path
from datetime import datetime

# Import Lambda functions
sys.path.append(str(Path(__file__).parent / 'lambda'))
try:
    from gpt4o_intent_classifier import lambda_handler as gpt4o_handler
    from self_service_automation import lambda_handler as selfserve_handler
except ImportError:
    print("Warning: Lambda functions not found. Using mock responses.")
    gpt4o_handler = None
    selfserve_handler = None

app = Flask(__name__)

# Store session data (in production, use Redis or database)
sessions = {}


def format_phone_number(phone: str) -> str:
    """Format phone number for speech (e.g., +15551234567 -> 555-123-4567)"""
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) == 10:
        return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
    return phone


@app.route("/voice", methods=['POST'])
def voice_greeting():
    """
    Initial greeting when call comes in
    Enhanced with quick menu option to reduce wait time
    """
    call_sid = request.values.get('CallSid', '')
    from_number = request.values.get('From', '')
    
    print(f"\n📞 New call from {from_number}")
    
    # Initialize session
    sessions[call_sid] = {
        'from': from_number,
        'step': 'greeting',
        'start_time': datetime.now().isoformat()
    }
    
    resp = VoiceResponse()
    
    # Greeting with natural speech - no menu needed
    gather = resp.gather(
        input='speech dtmf',
        action='/process-intent',
        timeout=4,
        speech_timeout='3',
        language='en-US',
        num_digits=1,
        enhanced=True,
        profanity_filter=False
    )
    
    gather.say(
        "Hey, thanks for calling John Hancock. What can I help you with today?",
        voice='Polly.Salli-Neural'
    )
    
    # If no input, offer callback option instead of infinite loop
    resp.redirect('/no-input-handler')
    
    return str(resp)


@app.route("/continue-call", methods=['GET', 'POST'])
def continue_call():
    """
    Simplified prompt for continuing within the same call (no full greeting)
    """
    resp = VoiceResponse()
    
    # Simple prompt without menu - just natural speech
    gather = resp.gather(
        input='speech dtmf',
        action='/process-intent',
        timeout=4,
        speech_timeout='3',
        language='en-US',
        num_digits=1,
        enhanced=True,
        profanity_filter=False
    )
    
    gather.say(
        "What else can I do for you?",
        voice='Polly.Salli-Neural'
    )
    
    # If no input, go to no-input handler
    resp.redirect('/no-input-handler')
    
    return str(resp)


@app.route("/process-intent", methods=['POST'])
def process_intent():
    """
    Process customer utterance with GPT-4o
    Enhanced with DTMF quick menu support
    """
    call_sid = request.values.get('CallSid', '')
    utterance = request.values.get('SpeechResult', '')
    digits = request.values.get('Digits', '')
    from_number = request.values.get('From', '')
    
    # Handle DTMF quick menu
    if digits:
        print(f"🔢 Customer pressed: {digits}")
        intent_map = {
            '1': 'CLAIM_STATUS',
            '2': 'PAYMENT',
            '3': 'COVERAGE_INQUIRY',
            '0': 'AGENT_REQUEST'
        }
        
        if digits in intent_map:
            resp = VoiceResponse()
            intent = intent_map[digits]
            
            if intent == 'AGENT_REQUEST':
                resp.redirect('/transfer-agent')
            else:
                resp.redirect(f'/self-service?intent={intent}&phone={from_number}')
            
            return str(resp)
    
    print(f"🎤 Customer said: '{utterance}'")
    
    if not utterance:
        # No speech detected, try again
        resp = VoiceResponse()
        resp.say("I didn't catch that. Could you please repeat?", voice='Polly.Salli-Neural')
        resp.redirect('/voice')
        return str(resp)
    
    # Call GPT-4o intent classifier
    if gpt4o_handler:
        event = {
            'Details': {
                'Parameters': {
                    'transcription': utterance,
                    'phoneNumber': from_number
                }
            }
        }
        
        result = gpt4o_handler(event, None)
        print(f"✅ GPT-4o Result: {result}")
        
        # Log AI recommendations if available
        if 'recommendations' in result:
            recs = result['recommendations']
            print(f"🤖 AI Recommendations:")
            print(f"   Primary Action: {recs.get('primaryAction', 'N/A')}")
            print(f"   Secondary Actions: {len(recs.get('secondaryActions', []))} items")
            print(f"   Customer Experience: {recs.get('customerExperience', 'N/A')}")
        
        # Store in session
        if call_sid in sessions:
            sessions[call_sid].update(result)
    else:
        # Mock response
        result = {
            'intentName': 'CLAIM_STATUS',
            'confidence': '85',
            'canSelfServe': 'true',
            'relationship': 'owner',
            'callType': 'Owner'
        }
    
    resp = VoiceResponse()
    
    # Route based on confidence
    confidence = int(result.get('confidence', '0'))
    intent_name = result.get('intentName', 'UNKNOWN')
    
    if confidence < 70:
        # Low confidence - clarify
        print("⚠️  Low confidence, asking for clarification")
        resp.say(
            "I want to make sure I help you correctly. Are you calling about a claim, "
            "a payment, coverage, finding a provider, or something else?",
            voice='Polly.Salli-Neural'
        )
        
        gather = resp.gather(
            input='speech',
            action='/process-clarification',
            timeout=5,
            speech_timeout='3',
            enhanced=True,
            speech_model='phone_call'
        )
        
        return str(resp)
    
    # Check if customer wants to speak with agent
    if intent_name == 'AGENT_REQUEST' or result.get('canSelfServe') == 'false':
        print("📞 Transfer to agent")
        resp.redirect('/transfer-agent')
        return str(resp)
    
    # Self-serviceable intents
    if result.get('canSelfServe') == 'true':
        print("✅ Self-service path")
        resp.redirect(f'/self-service?intent={intent_name}&phone={from_number}')
    else:
        print("📞 Transfer to agent (default)")
        resp.redirect('/transfer-agent')
    
    return str(resp)


@app.route("/process-clarification", methods=['POST'])
def process_clarification():
    """
    Handle clarification response when confidence is low
    Includes retry logic with 2 attempts before agent transfer
    """
    call_sid = request.values.get('CallSid', '')
    utterance = request.values.get('SpeechResult', '')
    from_number = request.values.get('From', '')
    
    print(f"🔄 Clarification received: {utterance}")
    
    # Track retry attempts
    if call_sid in sessions:
        retry_count = sessions[call_sid].get('clarification_retry', 0)
    else:
        sessions[call_sid] = {'clarification_retry': 0}
        retry_count = 0
    
    # If no utterance captured
    if not utterance:
        retry_count += 1
        sessions[call_sid]['clarification_retry'] = retry_count
        
        resp = VoiceResponse()
        
        if retry_count == 1:
            # First retry - ask more clearly with all options
            resp.say(
                "Sorry, didn't catch that. Are you calling about a claim, payment, coverage, "
                "finding a provider, a rate increase, or do you need to speak with someone?",
                voice='Polly.Salli-Neural'
            )
            gather = resp.gather(
                input='speech',
                action='/process-clarification',
                timeout=5,
                speech_timeout='3',
                enhanced=True,
                speech_model='phone_call'
            )
            return str(resp)
        
        elif retry_count >= 2:
            # After 2 retries - transfer to agent
            resp.say(
                "Alright, let me get you to someone who can help. Hold on just a sec.",
                voice='Polly.Salli-Neural'
            )
            sessions[call_sid]['clarification_retry'] = 0
            resp.redirect('/transfer-agent')
            return str(resp)
    
    # Process the clarified intent
    if gpt4o_handler:
        event = {
            'Details': {
                'Parameters': {
                    'utterance': utterance,
                    'transcription': utterance,
                    'phoneNumber': from_number
                }
            }
        }
        
        result = gpt4o_handler(event, None)
        print(f"✅ GPT-4o Result: {result}")
        
        if call_sid in sessions:
            sessions[call_sid].update(result)
    else:
        # Mock response
        result = {
            'intentName': 'CLAIM_STATUS',
            'confidence': '90',
            'canSelfServe': 'true',
            'relationship': 'owner',
            'callType': 'Owner'
        }
    
    resp = VoiceResponse()
    
    # Check confidence again
    confidence = int(result.get('confidence', '0'))
    
    if confidence < 70:
        # Still low confidence after clarification
        retry_count += 1
        sessions[call_sid]['clarification_retry'] = retry_count
        
        if retry_count >= 2:
            # After 2 attempts, transfer to agent
            resp.say(
                "Let me connect you with someone who can help you better.",
                voice='Polly.Salli-Neural'
            )
            sessions[call_sid]['clarification_retry'] = 0
            resp.redirect('/transfer-agent')
            return str(resp)
        else:
            # Try one more time with specific simplified options
            resp.say(
                "Let me try to help. Say 'claim' for claim status, 'payment' for billing, "
                "'coverage' for benefits, 'provider' to find care, 'rate' for rate questions, "
                "or 'agent' to speak with someone.",
                voice='Polly.Salli-Neural'
            )
            gather = resp.gather(
                input='speech',
                action='/process-clarification',
                timeout=5,
                speech_timeout='3',
                enhanced=True,
                speech_model='phone_call'
            )
            return str(resp)
    
    # Reset retry counter on success
    sessions[call_sid]['clarification_retry'] = 0
    
    # Route based on self-service capability
    intent_name = result.get('intentName', 'UNKNOWN')
    
    # Check if customer wants agent or intent requires agent
    if intent_name == 'AGENT_REQUEST' or result.get('canSelfServe') == 'false':
        resp.redirect('/transfer-agent')
        return str(resp)
    
    # Self-serviceable intents
    if result.get('canSelfServe') == 'true':
        resp.redirect(f'/self-service?intent={intent_name}&phone={from_number}')
    else:
        resp.redirect('/transfer-agent')
    
    return str(resp)


@app.route("/self-service", methods=['GET', 'POST'])
def self_service():
    """
    Handle self-service automation with AI recommendations
    """
    intent = request.args.get('intent', request.values.get('intent', 'UNKNOWN'))
    phone = request.args.get('phone', request.values.get('From', ''))
    call_sid = request.values.get('CallSid', '')
    
    print(f"🤖 Self-service: {intent}")
    
    resp = VoiceResponse()
    
    # Validate intent
    if intent == 'UNKNOWN' or not intent:
        print("❌ Unknown intent, transferring to agent")
        resp.say(
            "I'm having trouble understanding your request. Let me connect you with an agent.",
            voice='Polly.Salli-Neural'
        )
        resp.redirect('/transfer-agent')
        return str(resp)
    
    # Get recommendations from session if available
    recommendations = {}
    if call_sid in sessions and 'recommendations' in sessions[call_sid]:
        recommendations = sessions[call_sid]['recommendations']
        sentiment = sessions[call_sid].get('sentiment', 'neutral')
        
        # If customer is frustrated, add empathy first
        if sentiment in ['frustrated', 'angry']:
            resp.say(
                "I understand your concern, and I apologize for any frustration.",
                voice='Polly.Salli-Neural'
            )
            resp.pause(length=1)
    
    # Acknowledge
    resp.say(
        "Give me just a sec to pull that up.",
        voice='Polly.Salli-Neural'
    )
    
    resp.pause(length=2)  # Simulate lookup
    
    # Call self-service automation
    if selfserve_handler:
        try:
            event = {
                'Details': {
                    'Parameters': {
                        'intentName': intent,
                        'phoneNumber': phone
                    }
                }
            }
            
            result = selfserve_handler(event, None)
            print(f"✅ Self-service result: {result}")
            
            if result.get('success'):
                message = result.get('responseMessage', 'Your request has been processed.')
                
                # Split long messages into chunks (TwiML has length limits)
                chunks = [message[i:i+500] for i in range(0, len(message), 500)]
                
                for chunk in chunks:
                    resp.say(chunk, voice='Polly.Salli-Neural')
                
                # Add educational content if available from AI recommendations
                educational_content = recommendations.get('educationalContent', [])
                if educational_content and len(educational_content) > 0:
                    resp.pause(length=1)
                    resp.say(
                        f"Here's something helpful to know: {educational_content[0]}",
                        voice='Polly.Salli-Neural'
                    )
                
                # Offer secondary action if available
                secondary_actions = recommendations.get('secondaryActions', [])
                if secondary_actions and len(secondary_actions) > 0:
                    # Filter out empathy messages (already handled)
                    proactive_actions = [
                        action for action in secondary_actions 
                        if 'apologize' not in action.lower() and 'acknowledge' not in action.lower()
                    ]
                    if proactive_actions and len(proactive_actions) > 0:
                        resp.pause(length=1)
                        resp.say(
                            proactive_actions[0],
                            voice='Polly.Salli-Neural'
                        )
                
                # For PAYMENT intent, offer interactive payment options
                if intent == 'PAYMENT':
                    resp.pause(length=1)
                    # Use from_number from request instead of phone parameter
                    from_number = request.values.get('From', phone)
                    resp.redirect(f'/payment-options?phone={from_number}')
                    return str(resp)
                
                # For PROVIDER_REFERRAL intent, collect provider name and zip
                if intent == 'PROVIDER_REFERRAL':
                    needs_info = result.get('needsProviderInfo', False)
                    if needs_info:
                        resp.pause(length=1)
                        from_number = request.values.get('From', phone).strip()
                        resp.redirect(f'/provider-collect-name?phone={from_number}')
                        return str(resp)
                
            else:
                resp.say(
                    "I'm having trouble looking that up. Let me connect you with an agent.",
                    voice='Polly.Salli-Neural'
                )
                resp.redirect('/transfer-agent')
                return str(resp)
        except Exception as e:
            print(f"❌ Self-service error: {e}")
            resp.say(
                "I apologize, but I encountered an error. Let me connect you with an agent.",
                voice='Polly.Salli-Neural'
            )
            resp.redirect('/transfer-agent')
            return str(resp)
    else:
        # Mock response
        resp.say(
            "Your claim number 12345 was approved on April 10th for 2,800 dollars. "
            "Your reimbursement check was mailed on April 18th.",
            voice='Polly.Salli-Neural'
        )
    
    # Ask if anything else
    resp.pause(length=1)
    
    gather = resp.gather(
        input='speech dtmf',
        action='/anything-else',
        method='POST',
        timeout=5,
        num_digits=1,
        speech_timeout='3'
    )
    
    gather.say(
        "Anything else?",
        voice='Polly.Salli-Neural'
    )
    
    # Default to goodbye if no response
    resp.redirect('/anything-else')
    
    return str(resp)


@app.route("/anything-else", methods=['GET', 'POST'])
def anything_else():
    """
    Handle anything else prompt - natural speech recognition
    """
    response = request.values.get('Digits', request.values.get('SpeechResult', '')).lower()
    
    resp = VoiceResponse()
    
    # Check for continuation or restart
    if any(word in response for word in ['yes', 'yeah', 'yep', 'sure', 'another', 'more', 'continue', 'start over', 'restart', 'beginning', 'fresh']):
        # Continue with another question - use simplified prompt
        resp.redirect('/continue-call')
    # Check for explicit no or goodbye
    elif any(word in response for word in ['no', 'nope', 'done', 'good', 'bye', 'hang up', "that's it", "that's all"]) or not response:
        # End call
        resp.redirect('/goodbye')
    else:
        # If they said something else, ask for clarification
        resp.say("I didn't catch that. Did you need help with something else?", voice='Polly.Salli-Neural')
        resp.redirect('/continue-call')
    
    return str(resp)


@app.route("/transfer-agent", methods=['GET', 'POST'])
def transfer_agent():
    """
    Transfer to agent with enhanced experience to prevent drops
    Offers callback option and realistic wait time estimates
    """
    call_sid = request.values.get('CallSid', '')
    
    resp = VoiceResponse()
    
    # Offer callback option to prevent drops during long holds
    gather = resp.gather(
        input='speech dtmf',
        action='/process-transfer-choice',
        timeout=5,
        num_digits=1,
        speech_timeout='3'
    )
    
    gather.say(
        "Let me get you to someone. Wait time's about 3 to 5 minutes right now. "
        "Wanna hold, or should we just call you back in an hour?",
        voice='Polly.Salli-Neural'
    )
    
    # Default to hold if no response
    resp.redirect('/process-transfer-choice?Digits=1')
    
    return str(resp)


@app.route("/process-transfer-choice", methods=['GET', 'POST'])
def process_transfer_choice():
    """
    Handle transfer vs callback choice - natural speech
    """
    response = request.values.get('Digits', request.values.get('SpeechResult', '')).lower()
    from_number = request.values.get('From', '')
    call_sid = request.values.get('CallSid', '')
    
    resp = VoiceResponse()
    
    # Check for callback keywords
    if any(word in response for word in ['callback', 'call back', 'call me', 'later', 'no']):
        # Callback option
        resp.say(
            f"Perfect! We'll hit you back at {format_phone_number(from_number)} within the hour. "
            "You'll get a text too. Talk soon!",
            voice='Polly.Salli-Neural'
        )
        resp.hangup()
        
        # Log callback request (in production, create ticket in CRM)
        print(f"📞 Callback requested for {from_number} at {datetime.now()}")
        
        # Clean up session
        if call_sid in sessions:
            del sessions[call_sid]
        
        return str(resp)
    else:
        # Hold option (default or explicitly stated) - provide engaging hold experience
        resp.say(
            "Alright, putting you through. While you're waiting, remember you can handle stuff online anytime.",
            voice='Polly.Salli-Neural'
        )
        
        # In production, use resp.dial() to transfer to real agent line
        # For demo, we'll play hold music with periodic updates
        resp.play('http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3')
        
        # Periodic update to prevent customer from hanging up
        resp.pause(length=5)
        resp.say(
            "Almost there. Someone'll grab you in just a sec.",
            voice='Polly.Salli-Neural'
        )
        
        resp.pause(length=5)
        resp.say(
            "Thanks for waiting. In the real deal, you'd be chatting with someone now.",
            voice='Polly.Salli-Neural'
        )
        
        resp.redirect('/goodbye')
        
        return str(resp)


@app.route("/no-input-handler", methods=['POST'])
def no_input_handler():
    """
    Handle no input after greeting - offer callback instead of loop
    """
    resp = VoiceResponse()
    
    gather = resp.gather(
        input='speech dtmf',
        action='/process-intent',
        timeout=3,
        num_digits=1,
        speech_timeout='3'
    )
    
    gather.say(
        "Didn't catch that. What's up?",
        voice='Polly.Salli-Neural'
    )
    
    # After second no-input, offer transfer
    resp.say(
        "Having trouble hearing you. Let me get you to a real person.",
        voice='Polly.Salli-Neural'
    )
    resp.redirect('/transfer-agent')
    
    return str(resp)


@app.route("/payment-options", methods=['GET', 'POST'])
def payment_options():
    """
    Interactive payment processing - prevent drops by offering choices
    """
    try:
        resp = VoiceResponse()
        
        gather = resp.gather(
            input='speech dtmf',
            action='/process-payment-choice',
            timeout=5,
            num_digits=1,
            speech_timeout='3'
        )
        
        gather.say(
            "Wanna pay now, or you want to hear your options first?",
            voice='Polly.Salli-Neural'
        )
        
        # Default to payment methods if no response
        resp.redirect('/payment-methods')
        
        return str(resp)
    except Exception as e:
        print(f"❌ Payment options error: {e}")
        resp = VoiceResponse()
        resp.say("Having trouble with that. Let me get you to someone who can help.", voice='Polly.Salli-Neural')
        resp.redirect('/transfer-agent')
        return str(resp)


@app.route("/process-payment-choice", methods=['POST'])
def process_payment_choice():
    """
    Handle payment choice from customer - natural speech
    """
    response = request.values.get('Digits', request.values.get('SpeechResult', '')).lower()
    
    resp = VoiceResponse()
    
    # Check for payment keywords
    if any(word in response for word in ['pay now', 'pay', 'yes', 'yeah', 'sure', 'phone']):
        # Interactive payment via phone
        resp.say(
            "Cool, I'll get you to the payment system. "
            "Have your policy number handy, plus a credit card or bank info.",
            voice='Polly.Salli-Neural'
        )
        
        # In production, dial payment IVR: resp.dial('+18005551234')
        resp.play('http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3')
        resp.pause(length=3)
        resp.say(
            "In a production system, you'd be connected to the payment system now.",
            voice='Polly.Salli-Neural'
        )
        resp.redirect('/goodbye')
        
    elif any(word in response for word in ['options', 'methods', 'ways', 'how', 'other']):
        # Provide payment methods info
        resp.redirect('/payment-methods')
        
    elif any(word in response for word in ['no', 'menu', 'back', 'something else']):
        # Return to main menu
        resp.redirect('/continue-call')
        
    else:
        # Default to payment methods if unclear
        resp.redirect('/payment-methods')
    
    return str(resp)


@app.route("/payment-methods", methods=['GET', 'POST'])
def payment_methods():
    """
    Provide payment method information
    """
    resp = VoiceResponse()
    
    resp.say(
        "You've got three ways: "
        "Mail a check to P O Box 12345, Boston Mass, 02101. "
        "Call the payment line at 1-800-555-1234. "
        "Or just hop online to johnhancockltc.com.",
        voice='Polly.Salli-Neural'
    )
    
    resp.pause(length=1)
    
    # Offer to continue or end
    gather = resp.gather(
        input='speech dtmf',
        action='/anything-else',
        method='POST',
        timeout=5,
        num_digits=1,
        speech_timeout='3'
    )
    
    gather.say(
        "Anything else?",
        voice='Polly.Salli-Neural'
    )
    
    # Fallback to anything-else endpoint (will redirect to goodbye if no input)
    resp.redirect('/anything-else')
    
    return str(resp)


@app.route("/provider-collect-name", methods=['GET', 'POST'])
def provider_collect_name():
    """
    Collect provider name for provider referral / add provider
    Step 1: Ask for provider name
    """
    resp = VoiceResponse()
    phone = request.args.get('phone', request.values.get('From', '')).strip()
    call_sid = request.values.get('CallSid', '')
    
    gather = resp.gather(
        input='speech',
        action=f'/provider-collect-zip?phone={phone}',
        timeout=5,
        speech_timeout='3'
    )
    
    gather.say(
        "What's the name of the provider you're looking for?",
        voice='Polly.Salli-Neural'
    )
    
    # No input fallback
    resp.say("Didn't catch that.", voice='Polly.Salli-Neural')
    resp.redirect(f'/provider-collect-name?phone={phone}')
    
    return str(resp)


@app.route("/provider-collect-zip", methods=['GET', 'POST'])
def provider_collect_zip():
    """
    Collect zip code for provider referral / add provider
    Step 2: Ask for zip code, then confirm and submit
    """
    resp = VoiceResponse()
    phone = request.args.get('phone', request.values.get('From', '')).strip()
    call_sid = request.values.get('CallSid', '')
    provider_name = request.values.get('SpeechResult', '')
    
    print(f"🏥 Provider name collected: '{provider_name}'")
    
    # Store provider name in session
    if call_sid in sessions:
        sessions[call_sid]['provider_name'] = provider_name
    else:
        sessions[call_sid] = {'provider_name': provider_name}
    
    gather = resp.gather(
        input='speech dtmf',
        action=f'/provider-confirm?phone={phone}',
        timeout=5,
        speech_timeout='3',
        num_digits=5
    )
    
    gather.say(
        "Got it. And what's the zip code?",
        voice='Polly.Salli-Neural'
    )
    
    # No input fallback
    resp.say("Didn't catch that.", voice='Polly.Salli-Neural')
    resp.redirect(f'/provider-collect-zip?phone={phone}')
    
    return str(resp)


@app.route("/provider-confirm", methods=['GET', 'POST'])
def provider_confirm():
    """
    Confirm provider name and zip, then submit to Helper Bees
    """
    resp = VoiceResponse()
    phone = request.args.get('phone', request.values.get('From', '')).strip()
    call_sid = request.values.get('CallSid', '')
    zip_code = request.values.get('Digits', request.values.get('SpeechResult', ''))
    
    # Get provider name from session
    provider_name = ''
    if call_sid in sessions:
        provider_name = sessions[call_sid].get('provider_name', '')
        sessions[call_sid]['provider_zip'] = zip_code
    
    print(f"📍 Provider zip collected: '{zip_code}' for provider: '{provider_name}'")
    
    resp.say(
        f"Perfect! I've got {provider_name} in zip code {zip_code}. "
        "I'm sending that over now. "
        "You should hear back within 1 to 2 business days with options and next steps.",
        voice='Polly.Salli-Neural'
    )
    
    resp.pause(length=1)
    
    # Ask if anything else
    gather = resp.gather(
        input='speech dtmf',
        action='/anything-else',
        method='POST',
        timeout=5,
        num_digits=1,
        speech_timeout='3'
    )
    
    gather.say(
        "Anything else?",
        voice='Polly.Salli-Neural'
    )
    
    resp.redirect('/anything-else')
    
    return str(resp)


@app.route("/provider-email-verify", methods=['GET', 'POST'])
def provider_email_verify():
    """
    Handle email verification for provider referral
    Following flow: verify email → send to Helper Bees → set SLA expectation
    Includes retry logic with 2 attempts before agent transfer
    """
    resp = VoiceResponse()
    phone = request.args.get('phone', request.values.get('From', ''))
    call_sid = request.values.get('CallSid', '')
    
    # Track retry attempts
    if call_sid in sessions:
        retry_count = sessions[call_sid].get('provider_email_retry', 0)
    else:
        sessions[call_sid] = {'provider_email_retry': 0}
        retry_count = 0
    
    # Get the speech response if any
    speech = request.values.get('SpeechResult', '').lower()
    
    if speech:
        # Check for yes/confirmation
        if any(word in speech for word in ['yes', 'yeah', 'correct', 'right', 'good', 'fine', 'yep', 'sure', 'ok', 'okay']):
            resp.say(
                "Perfect! I've put in the request. The Helper Bees will email you within 1-2 business days with provider options. "
                "They're really good at finding exactly what you need. Anything else I can help with?",
                voice='Polly.Salli-Neural'
            )
            resp.redirect('/anything-else')
            return str(resp)
        
        # Check for no/need different email
        elif any(word in speech for word in ['no', 'nope', 'different', 'change', 'update', 'wrong']):
            resp.say(
                "No problem! What's the best email address for you?",
                voice='Polly.Salli-Neural'
            )
            
            # Gather email (would need email collection flow in production)
            gather = resp.gather(
                input='speech',
                action='/provider-email-collected',
                timeout=10,
                speech_timeout='3'
            )
            
            return str(resp)
    
    # No input or unclear - retry with clearer options
    retry_count += 1
    sessions[call_sid]['provider_email_retry'] = retry_count
    
    if retry_count == 1:
        # First retry - ask more clearly
        resp.say(
            "Sorry, didn't catch that. Just need to know - is that email address still good? Say yes or no.",
            voice='Polly.Salli-Neural'
        )
        resp.redirect('/provider-email-verify?phone=' + phone)
        return str(resp)
    
    elif retry_count == 2:
        # Second retry - offer clearer binary choice
        resp.say(
            "Hmm, having trouble hearing you. Let me make this easier. "
            "Say 'yes' if the email is good, or say 'no' if you need to update it.",
            voice='Polly.Salli-Neural'
        )
        resp.redirect('/provider-email-verify?phone=' + phone)
        return str(resp)
    
    else:
        # After 2 retries - transfer to agent
        resp.say(
            "Alright, let me get you to someone who can help set this up. Hold on just a sec.",
            voice='Polly.Salli-Neural'
        )
        # Reset retry counter
        sessions[call_sid]['provider_email_retry'] = 0
        resp.redirect('/transfer-agent')
        return str(resp)


@app.route("/provider-email-collected", methods=['POST'])
def provider_email_collected():
    """
    Process newly collected email for provider referral
    """
    resp = VoiceResponse()
    speech = request.values.get('SpeechResult', '')
    
    # In production, would validate and store email
    # For now, just confirm
    resp.say(
        f"Got it, I've updated your email to {speech}. "
        "The Helper Bees will reach out there within 1-2 business days with provider options. "
        "Is there anything else I can help you with?",
        voice='Polly.Salli-Neural'
    )
    
    resp.redirect('/anything-else')
    
    return str(resp)


@app.route("/goodbye", methods=['GET', 'POST'])
def goodbye():
    """
    End call gracefully
    """
    call_sid = request.values.get('CallSid', '')
    
    print(f"👋 Ending call {call_sid}")
    
    resp = VoiceResponse()
    resp.say(
        "Thanks for calling! Have a good one!",
        voice='Polly.Salli-Neural'
    )
    resp.hangup()
    
    # Clean up session
    if call_sid in sessions:
        del sessions[call_sid]
    
    return str(resp)


@app.route("/status", methods=['POST'])
def call_status():
    """
    Handle call status callbacks
    """
    call_sid = request.values.get('CallSid', '')
    call_status = request.values.get('CallStatus', '')
    
    print(f"📊 Call {call_sid}: {call_status}")
    
    return jsonify({'status': 'ok'})


@app.route("/", methods=['GET'])
def index():
    """
    Status page
    """
    return """
    <html>
    <head><title>LTC AI Voice Demo</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>📞 LTC AI-Enhanced Voice Demo</h1>
        <p><strong>Status:</strong> Running ✅</p>
        
        <h2>Setup Instructions:</h2>
        <ol>
            <li>Sign up at <a href="https://www.twilio.com/try-twilio">Twilio</a></li>
            <li>Buy a phone number (~$1/month)</li>
            <li>Get your ngrok URL (should be running on another terminal)</li>
            <li>Configure Twilio number:
                <ul>
                    <li>Voice & Fax → "A call comes in"</li>
                    <li>Webhook: <code>https://YOUR_NGROK_URL/voice</code></li>
                    <li>HTTP POST</li>
                </ul>
            </li>
            <li>Call your Twilio number!</li>
        </ol>
        
        <h2>Active Calls:</h2>
        <p>Sessions: {}</p>
        
        <h2>Endpoints:</h2>
        <ul>
            <li><code>/voice</code> - Initial greeting</li>
            <li><code>/process-intent</code> - GPT-4o classification</li>
            <li><code>/self-service</code> - Self-service automation</li>
            <li><code>/transfer-agent</code> - Agent transfer</li>
            <li><code>/goodbye</code> - End call</li>
        </ul>
    </body>
    </html>
    """.format(len(sessions))


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 LTC AI Voice Webhook Server Starting...")
    print("="*60)
    print("\n📋 Setup Steps:")
    print("1. Make sure this is running")
    print("2. In another terminal, run: ngrok http 5000")
    print("3. Copy the ngrok URL (e.g., https://abc123.ngrok.io)")
    print("4. Configure your Twilio number webhook to that URL")
    print("5. Call your Twilio number to test!")
    print("\n" + "="*60 + "\n")
    
    # Use PORT from environment (Render uses port 10000)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
