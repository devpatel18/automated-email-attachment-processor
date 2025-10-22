#!/bin/bash

# Email Attachment Processor Setup Script
# This script sets up the environment and installs dependencies

set -e

echo "=== Email Attachment Processor Setup ==="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
chmod +x email_processor.py
chmod +x demo_mock_data.py

# Create log directory if it doesn't exist
mkdir -p logs

# Create sample configuration if it doesn't exist
if [ ! -f "config.env" ]; then
    echo "Creating sample configuration..."
    cp config.env config.env.sample
    echo "Please edit config.env with your actual configuration values."
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit config.env with your actual configuration"
echo "2. Test the processor: python3 email_processor.py"
echo "3. Generate mock data: python3 demo_mock_data.py"
echo "4. Set up cron job using crontab_example as reference"
echo ""
echo "To activate the virtual environment in the future:"
echo "source venv/bin/activate"
