#!/bin/bash
# Wrapper script for email processor to run from cron
# This ensures proper environment and working directory

# Set the working directory to the project root
cd /Users/devpatel/Downloads/Dev

# Set environment variables
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
export PYTHONPATH="/Users/devpatel/Downloads/Dev"

# Activate virtual environment if it exists
VENV_PATH=".venv"
if [ ! -d "$VENV_PATH" ]; then
  VENV_PATH="venv"
fi

if [ -f "$VENV_PATH/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$VENV_PATH/bin/activate"
    PYTHON_BIN="$VENV_PATH/bin/python"
else
    PYTHON_BIN="/usr/bin/python3"
fi

# Ensure logs directory exists
mkdir -p /Users/devpatel/Downloads/Dev/logs
umask 027

# Run the email processor using selected python binary
"$PYTHON_BIN" /Users/devpatel/Downloads/Dev/src/email_processor.py >> /Users/devpatel/Downloads/Dev/logs/email_processor.log 2>&1
