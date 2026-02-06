#!/bin/bash
# Installation script for Market Analyzer dependencies

echo "📦 Installing Market Analyzer dependencies..."

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip3 not found. Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Install Python packages
echo "Installing Python packages..."
python3 -m pip install --break-system-packages \
    yfinance \
    pandas \
    numpy \
    fastapi \
    uvicorn \
    requests \
    beautifulsoup4 \
    python-telegram-bot

echo "✅ Dependencies installed successfully!"
echo ""
echo "To test the analyzer, run:"
echo "  python3 scripts/analyzer.py analyze AAPL"
