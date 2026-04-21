#!/bin/bash
# Quick setup script for Digital Director of Needs demo

echo "🚀 Setting up Digital Director of Needs Demo..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q streamlit

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 To run the Streamlit demo:"
echo "   source venv/bin/activate"
echo "   streamlit run streamlit_demo.py"
echo ""
echo "🧪 To run the flow simulator:"
echo "   python3 flow_simulator.py --test-all"
echo ""
