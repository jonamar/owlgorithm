#!/bin/bash
# Debug runner to capture environment differences between manual vs launchd execution

LOG_FILE="/Users/jonamar/Documents/owlgorithm/logs/debug-environment.log"

echo "=== DEBUG RUN START: $(date) ===" > "$LOG_FILE"
echo "PWD: $(pwd)" >> "$LOG_FILE"
echo "USER: $USER" >> "$LOG_FILE"
echo "HOME: $HOME" >> "$LOG_FILE"
echo "PATH: $PATH" >> "$LOG_FILE"
echo "SHELL: $SHELL" >> "$LOG_FILE"
echo "TERM: $TERM" >> "$LOG_FILE"
echo "Python location: $(which python3)" >> "$LOG_FILE"
echo "Python version: $(python3 --version 2>&1)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Test changing to correct directory
echo "Changing to owlgorithm directory..." >> "$LOG_FILE"
cd /Users/jonamar/Documents/owlgorithm
echo "New PWD: $(pwd)" >> "$LOG_FILE"

# Test if our runner script exists and is executable
echo "Runner script check:" >> "$LOG_FILE"
ls -la /Users/jonamar/bin/owlgorithm-daily-runner >> "$LOG_FILE" 2>&1

# Try to execute the actual runner and capture any errors
echo "" >> "$LOG_FILE"
echo "=== ATTEMPTING TO RUN ACTUAL SCRIPT ===" >> "$LOG_FILE"
/Users/jonamar/bin/owlgorithm-daily-runner >> "$LOG_FILE" 2>&1
exit_code=$?

echo "" >> "$LOG_FILE"
echo "=== SCRIPT EXIT CODE: $exit_code ===" >> "$LOG_FILE"
echo "=== DEBUG RUN END: $(date) ===" >> "$LOG_FILE"