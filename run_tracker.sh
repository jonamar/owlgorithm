#!/bin/bash
# This script ensures the daily tracker runs in the correct environment.

# Navigate to the project directory
cd /Users/jonamar/Documents/owlgorithm || exit

# Activate the virtual environment and run the tracker
# Log output to tracker.log
source duolingo_env/bin/activate
python daily_tracker.py >> tracker.log 2>&1 