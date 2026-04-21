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
    
    # Greeting with speech input and DTMF quick menu
    gather = resp.gather(
        input='speech dtmf',
        action='/process-intent',
        timeout=3,
        speech_timeout='auto',
        language='en-US',
        num_digits=1
    )
    
    gather.say(
        "Thank you for calling John Hancock Long Term Care. "
        "I'm your digital assistant. How can I help you today? "
        "You can also press 1 for claims, 2 for payments, 3 for coverage, or 0 for an agent.",
        voice='Polly.Joanna-Neural'
    )
    
    # If no input, offer callback option instead of infinite loop
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
        resp.say("I didn't catch that. Could you please repeat?", voice='Polly.Joanna-Neural')
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
            "a payment, or something else?",
            voice='Polly.Joanna-Neural'
        )
        
        gather = resp.gather(
            input='speech',
            action='/process-clarification',
            timeout=3,
            speech_timeout='auto'
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
    """
    call_sid = request.values.get('CallSid', '')
    utterance = request.values.get('SpeechResult', '')
    from_number = request.values.get('From', '')
    
    print(f"🔄 Clarification received: {utterance}")
    
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
            voice='Polly.Joanna-Neural'
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
                voice='Polly.Joanna-Neural'
            )
            resp.pause(length=1)
    
    # Acknowledge
    resp.say(
        "Let me look that up for you.",
        voice='Polly.Joanna-Neural'
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
                    resp.say(chunk, voice='Polly.Joanna-Neural')
                
                # Add educational content if available from AI recommendations
                educational_content = recommendations.get('educationalContent', [])
                if educational_content and len(educational_content) > 0:
                    resp.pause(length=1)
                    resp.say(
                        f"Here's something helpful to know: {educational_content[0]}",
                        voice='Polly.Joanna-Neural'
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
                            voice='Polly.Joanna-Neural'
                        )
                
                # For PAYMENT intent, offer interactive payment options
                if intent == 'PAYMENT':
                    resp.pause(length=1)
                    resp.redirect('/payment-options?phone=' + phone)
                    return str(resp)
                
            else:
                resp.say(
                    "I'm having trouble looking that up. Let me connect you with an agent.",
                    voice='Polly.Joanna-Neural'
                )
                resp.redirect('/transfer-agent')
                return str(resp)
        except Exception as e:
            print(f"❌ Self-service error: {e}")
            resp.say(
                "I apologize, but I encountered an error. Let me connect you with an agent.",
                voice='Polly.Joanna-Neural'
            )
            resp.redirect('/transfer-agent')
            return str(resp)
    else:
        # Mock response
        resp.say(
            "Your claim number 12345 was approved on April 10th for 2,800 dollars. "
            "Your reimbursement check was mailed on April 18th.",
            voice='Polly.Joanna-Neural'
        )
    
    # Ask if anything else
    resp.pause(length=1)
    
    gather = resp.gather(
        input='speech dtmf',
        action='/anything-else',
        method='POST',
        timeout=5,
        num_digits=1,
        speech_timeout='auto'
    )
    
    gather.say(
        "Is there anything else I can help you with? Press 1 to continue, press 2 to end the call, or press 3 to start over from the beginning.",
        voice='Polly.Joanna-Neural'
    )
    
    # Default to goodbye if no response
    resp.redirect('/anything-else')
    
    return str(resp)


@app.route("/anything-else", methods=['GET', 'POST'])
def anything_else():
    """
    Handle anything else prompt with restart option
    """
    response = request.values.get('Digits', request.values.get('SpeechResult', ''))
    
    resp = VoiceResponse()
    
    if '1' in response or 'yes' in response.lower():
        # Continue with another question
        resp.say("Sure, what else can I help you with?", voice='Polly.Joanna-Neural')
        resp.redirect('/voice')
    elif '3' in response or 'start over' in response.lower() or 'restart' in response.lower():
        # Restart from the very beginning
        resp.say("No problem! Let's start fresh.", voice='Polly.Joanna-Neural')
        resp.pause(length=1)
        resp.redirect('/voice')  # Goes to the greeting with menu
    else:
        # End call (2 or "no" or timeout)
        resp.redirect('/goodbye')
    
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
        speech_timeout='auto'
    )
    
    gather.say(
        "I can connect you with a specialist now. Current wait time is approximately 3 to 5 minutes. "
        "Press 1 to hold, or press 2 to request a callback within the next hour.",
        voice='Polly.Joanna-Neural'
    )
    
    # Default to hold if no response
    resp.redirect('/process-transfer-choice?Digits=1')
    
    return str(resp)


@app.route("/process-transfer-choice", methods=['GET', 'POST'])
def process_transfer_choice():
    """
    Handle transfer vs callback choice
    """
    response = request.values.get('Digits', request.values.get('SpeechResult', '1'))
    from_number = request.values.get('From', '')
    call_sid = request.values.get('CallSid', '')
    
    resp = VoiceResponse()
    
    if '2' in response or 'callback' in response.lower() or 'call me back' in response.lower():
        # Callback option
        resp.say(
            f"Perfect! We'll call you back at {format_phone_number(from_number)} within the next hour. "
            "You'll receive a confirmation text message shortly. Thank you for calling!",
            voice='Polly.Joanna-Neural'
        )
        resp.hangup()
        
        # Log callback request (in production, create ticket in CRM)
        print(f"📞 Callback requested for {from_number} at {datetime.now()}")
        
        # Clean up session
        if call_sid in sessions:
            del sessions[call_sid]
        
        return str(resp)
    else:
        # Hold option - provide engaging hold experience
        resp.say(
            "Thank you for holding. Let me connect you now. While you wait, you can also manage your policy anytime at our customer portal.",
            voice='Polly.Joanna-Neural'
        )
        
        # In production, use resp.dial() to transfer to real agent line
        # For demo, we'll play hold music with periodic updates
        resp.play('http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3')
        
        # Periodic update to prevent customer from hanging up
        resp.pause(length=5)
        resp.say(
            "You're next in line. An agent will be with you shortly.",
            voice='Polly.Joanna-Neural'
        )
        
        resp.pause(length=5)
        resp.say(
            "Thank you for holding. In a production system, you would now be connected to an agent.",
            voice='Polly.Joanna-Neural'
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
        speech_timeout='auto'
    )
    
    gather.say(
        "I didn't hear you. How can I help you today? "
        "Say 'claims', 'payments', 'coverage', or press 0 for an agent.",
        voice='Polly.Joanna-Neural'
    )
    
    # After second no-input, offer callback
    resp.say(
        "I'm having trouble hearing you. For faster service, visit our website or press 0 to speak with an agent.",
        voice='Polly.Joanna-Neural'
    )
    resp.redirect('/transfer-agent')
    
    return str(resp)


@app.route("/payment-options", methods=['GET', 'POST'])
def payment_options():
    """
    Interactive payment processing - prevent drops by offering choices
    """
    phone = request.args.get('phone', request.values.get('From', ''))
    
    resp = VoiceResponse()
    
    gather = resp.gather(
        input='speech dtmf',
        action='/process-payment-choice',
        timeout=5,
        num_digits=1,
        speech_timeout='auto'
    )
    
    gather.say(
        "Would you like to make a payment now? "
        "Press 1 to pay by phone, press 2 to hear other payment methods, or press 3 to return to the main menu.",
        voice='Polly.Joanna-Neural'
    )
    
    # Default to payment methods if no response
    resp.redirect('/payment-methods')
    
    return str(resp)


@app.route("/process-payment-choice", methods=['POST'])
def process_payment_choice():
    """
    Handle payment choice from customer
    """
    response = request.values.get('Digits', request.values.get('SpeechResult', ''))
    from_number = request.values.get('From', '')
    
    resp = VoiceResponse()
    
    if '1' in response or 'pay now' in response.lower() or 'pay by phone' in response.lower():
        # Interactive payment via phone
        resp.say(
            "I'll transfer you to our secure automated payment system. "
            "You'll need your policy number and a credit card or bank account information.",
            voice='Polly.Joanna-Neural'
        )
        
        # In production, dial payment IVR: resp.dial('+18005551234')
        resp.play('http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3')
        resp.pause(length=3)
        resp.say(
            "In a production system, you would now be connected to the payment system.",
            voice='Polly.Joanna-Neural'
        )
        resp.redirect('/goodbye')
        
    elif '2' in response or 'other methods' in response.lower():
        # Provide payment methods info
        resp.redirect('/payment-methods')
        
    elif '3' in response or 'main menu' in response.lower():
        # Return to main menu
        resp.say("Returning to the main menu.", voice='Polly.Joanna-Neural')
        resp.redirect('/voice')
        
    else:
        # Unclear response
        resp.say("I didn't understand that.", voice='Polly.Joanna-Neural')
        resp.redirect('/payment-options?phone=' + from_number)
    
    return str(resp)


@app.route("/payment-methods", methods=['GET', 'POST'])
def payment_methods():
    """
    Provide payment method information
    """
    resp = VoiceResponse()
    
    resp.say(
        "You can pay your premium in three ways: "
        "One, mail a check to P O Box 12345, Boston Massachusetts, 02101. "
        "Two, call our automated payment line at 1-800-555-1234. "
        "Or three, visit our website at johnhancockltc.com and log in to your account.",
        voice='Polly.Joanna-Neural'
    )
    
    resp.pause(length=1)
    
    # Offer to continue or end
    gather = resp.gather(
        input='speech dtmf',
        action='/anything-else',
        method='POST',
        timeout=5,
        num_digits=1,
        speech_timeout='auto'
    )
    
    gather.say(
        "Is there anything else I can help you with? Press 1 to continue, or press 2 to end the call.",
        voice='Polly.Joanna-Neural'
    )
    
    # Fallback to anything-else endpoint (will redirect to goodbye if no input)
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
        "Thank you for calling John Hancock Long Term Care. Have a great day!",
        voice='Polly.Joanna-Neural'
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
