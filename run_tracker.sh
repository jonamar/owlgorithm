#!/bin/bash
# Duolingo Tracker Runner Script
# This script is called by cron to run the daily tracker

# Change to the project directory
cd /Users/jonamar/Documents/owlgorithm

# Activate the virtual environment and run the tracker
source duolingo_env/bin/activate
python scripts/daily_update.py

# Log the completion
echo "Tracker run completed at $(date)" >> logs/tracker_runs.log 