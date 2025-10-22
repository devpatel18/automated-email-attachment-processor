#!/usr/bin/env python3
"""
Email Attachment Processor - Main Entry Point

This is the main entry point for the email processor.
It imports and runs the actual processor from the src directory.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Change to the project root directory
os.chdir(os.path.dirname(__file__))

# Import and run the main processor
from email_processor import main

if __name__ == "__main__":
    main()
