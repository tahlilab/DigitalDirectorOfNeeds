#!/bin/bash
# Quick setup for Twilio phone testing

echo "📞 Setting up Twilio Test Number for AI Flow"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing required packages..."
pip install -q flask twilio

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Sign up for Twilio (if you haven't):"
echo "   → https://www.twilio.com/try-twilio"
echo "   → Free trial includes \$15 credit"
echo ""
echo "2. Buy a phone number:"
echo "   → Twilio Console → Phone Numbers → Buy a number"
echo "   → Cost: ~\$1/month"
echo ""
echo "3. Start the webhook server:"
echo "   source venv/bin/activate"
echo "   python3 twilio_webhook.py"
echo ""
echo "4. In ANOTHER terminal, expose it with ngrok:"
echo "   brew install ngrok  # if you don't have it"
echo "   ngrok http 5000"
echo ""
echo "5. Configure your Twilio number:"
echo "   → Twilio Console → Your number → Voice Configuration"
echo "   → A call comes in: Webhook"
echo "   → URL: https://YOUR_NGROK_URL/voice"
echo "   → HTTP POST"
echo "   → Save"
echo ""
echo "6. Call your Twilio number and test!"
echo ""
echo "🎯 Test utterances:"
echo "   - 'I need to check my claim status'"
echo "   - 'I want to pay my premium'"
echo "   - 'I need to speak to an agent'"
echo ""
