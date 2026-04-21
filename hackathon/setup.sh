#!/bin/bash

echo "🚀 Setting up Digital Director of Needs Hackathon Demo"
echo "======================================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo "  Found Python $python_version"
else
    echo "  ❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "✓ Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt --quiet

# Copy environment template
if [ ! -f .env ]; then
    echo "✓ Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "  ⚠️  IMPORTANT: Please edit .env and add your API keys!"
    echo "  Required: AZURE_OPENAI_API_KEY or OPENAI_API_KEY"
else
    echo "  ℹ️  .env file already exists (not overwriting)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Edit .env file and add your API keys:"
echo "   $ nano .env"
echo ""
echo "2. Run the Streamlit demo:"
echo "   $ source .venv/bin/activate"
echo "   $ streamlit run app.py"
echo ""
echo "3. Open browser to http://localhost:8501"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
