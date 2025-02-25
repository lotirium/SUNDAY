#!/bin/bash
# F.R.I.D.A.Y. Assistant Launcher
# Stark Industries (c) 2025

echo "Initializing F.R.I.D.A.Y. Assistant..."

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Setting up initial environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the application
python src/main.py