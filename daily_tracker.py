#!/usr/bin/env python3
"""
Daily Duolingo Tracker
Orchestrates the scraping of duome.eu, parsing the data, and updating
the personal-math.md file with the latest progress and projections.
"""

import os
import json
import re
import subprocess
import glob
from datetime import datetime

# --- Configuration ---
MARKDOWN_FILE = 'personal-math.md'
STATE_FILE = 'tracker_state.json'
USERNAME = 'jonamar'
TOTAL_UNITS_IN_COURSE = 272
GOAL_DAYS = 548  # 18 months

def run_scraper():
    """Runs the duome_raw_scraper.py script to get the latest data."""
    print("🚀 Starting scraper to fetch latest data...")
    try:
        # Find the python executable in the virtual environment
        venv_python = 'duolingo_env/bin/python'
        if not os.path.exists(venv_python):
            print("❌ Virtual environment python not found. Please ensure duolingo_env is set up.")
            return False

        # Run the scraper script
        subprocess.run(
            [venv_python, 'duome_raw_scraper.py', '--username', USERNAME],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Scraper ran successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraper script failed with error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Scraper script not found. Make sure you are in the correct directory.")
        return False

def find_latest_json_file():
    """Finds the most recently created JSON output file."""
    try:
        list_of_files = glob.glob(f'duome_raw_{USERNAME}_*.json')
        if not list_of_files:
            return None
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    except Exception as e:
        print(f"❌ Error finding latest JSON file: {e}")
        return None

def get_newly_completed_units(json_data, state_data):
    """
    Compares the latest scrape with the saved state to find newly
    completed units.
    """
    # Find all units marked as complete in the latest data
    completed_in_json = {
        session['unit']
        for session in json_data.get('sessions', [])
        if session.get('is_unit_completion') and session.get('unit')
    }

    # Get units we have already processed
    processed_units = set(state_data.get('processed_units', []))

    newly_completed = completed_in_json - processed_units
    return newly_completed, completed_in_json

def update_markdown_file(newly_completed_count, total_lessons_completed):
    """Reads, updates, and writes the personal-math.md file."""
    print(f"📈 Updating stats...")
    
    with open(MARKDOWN_FILE, 'r') as f:
        content = f.read()

    # --- Read existing values ---
    try:
        completed_units_old = int(re.search(r"Completed Units:\s*(\d+)", content).group(1))
        lessons_per_unit = int(re.search(r"Total Lessons:\s*(\d+)", content).group(1))
        mins_per_lesson = float(re.search(r"Time per Lesson:\s*([\d.]+)", content).group(1))
    except (AttributeError, ValueError) as e:
        print(f"❌ Could not parse existing stats from {MARKDOWN_FILE}: {e}")
        return

    # --- Calculate new values ---
    new_completed_units = completed_units_old + newly_completed_count
    new_remaining_units = TOTAL_UNITS_IN_COURSE - new_completed_units
    total_lessons_remaining = new_remaining_units * lessons_per_unit
    lessons_per_day_required = total_lessons_remaining / GOAL_DAYS
    time_per_day_required_mins = lessons_per_day_required * mins_per_lesson
    
    hours = int(time_per_day_required_mins // 60)
    minutes = int(time_per_day_required_mins % 60)
    time_per_day_str = f"~{hours} hour {minutes} minutes"

    # --- Update content with new values ---
    content = re.sub(r"(Completed Units:\s*)(\d+)", rf"\g<1>{new_completed_units}", content)
    content = re.sub(r"(Remaining Units:\s*)(\d+)", rf"\g<1>{new_remaining_units}", content)
    content = re.sub(r"(Total Lessons Completed:\s*)(\d+)", rf"\g<1>{total_lessons_completed}", content)
    content = re.sub(r"(Total Lessons Remaining:\s*)~?[\d,]+", rf"\g<1>~{total_lessons_remaining:,.0f}", content)
    content = re.sub(r"(Lessons Per Day Required:\s*)\*\*~?[\d.]+\*\*", rf"\g<1>**~{lessons_per_day_required:.1f} lessons**", content)
    content = re.sub(r"(Time Per Day Required:\s*)\*\*~?[\w\s]+\*\*", rf"\g<1>**{time_per_day_str}**", content)
    content = re.sub(r"(\*Last updated:\s*)[\w\s,]+", rf"\g<1>{datetime.now().strftime('%B %d, %Y')}", content)

    with open(MARKDOWN_FILE, 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully updated {MARKDOWN_FILE}.")
    if newly_completed_count > 0:
        print(f"   - Newly Completed Units: {newly_completed_count}")
    print(f"   - Total Lessons Completed: {total_lessons_completed}")

def main():
    """Main execution function."""
    if not run_scraper():
        return

    latest_json_path = find_latest_json_file()
    if not latest_json_path:
        print("❌ No JSON file found after running scraper.")
        return

    with open(latest_json_path, 'r') as f:
        json_data = json.load(f)
        
    state_data = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state_data = json.load(f)

    # Check for changes
    newly_completed, all_completed_in_json = get_newly_completed_units(json_data, state_data)
    new_total_lessons = json_data.get('total_lessons_completed', 0)
    old_total_lessons = state_data.get('total_lessons_completed', 0)

    has_new_units = bool(newly_completed)
    has_new_lessons = new_total_lessons > old_total_lessons

    if has_new_units or has_new_lessons:
        update_markdown_file(len(newly_completed), new_total_lessons)
        
        # Update state file with the latest data
        state_data['processed_units'] = list(all_completed_in_json)
        state_data['total_lessons_completed'] = new_total_lessons
        with open(STATE_FILE, 'w') as f:
            json.dump(state_data, f, indent=2)
        print(f"✅ State file '{STATE_FILE}' updated.")
    else:
        print("✅ No new units or lessons completed since last check. No updates needed.")

if __name__ == "__main__":
    main() 