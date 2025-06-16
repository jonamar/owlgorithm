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
from pushover_notifier import PushoverNotifier

# --- Configuration ---
MARKDOWN_FILE = 'personal-math.md'
STATE_FILE = 'tracker_state.json'
USERNAME = 'jonamar'
TOTAL_UNITS_IN_COURSE = 272
GOAL_DAYS = 548  # 18 months

# --- Baseline Metrics (from personal-math.md) ---
# These are updated manually if a new, more accurate analysis is done.
BASE_LESSONS_PER_UNIT = 31
BASE_MINS_PER_LESSON = 7.5

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
    
    # Also identify session data from the latest scrape
    json_session_dates = {
        session['datetime'][:10]  # Extract just the date part
        for session in json_data.get('sessions', [])
        if session.get('datetime')
    }
    
    # Get units we have already processed
    processed_units = set(state_data.get('processed_units', []))
    
    # Get the last scrape date we processed
    last_scrape_date = state_data.get('last_scrape_date', None)
    
    # Check if we have any new sessions since the last scrape
    has_new_sessions = False
    if last_scrape_date:
        latest_session_date = max(json_session_dates) if json_session_dates else None
        if latest_session_date and latest_session_date > last_scrape_date:
            print(f"✨ Found new sessions since last scrape! Latest: {latest_session_date}, Last processed: {last_scrape_date}")
            has_new_sessions = True
    
    newly_completed = completed_in_json - processed_units
    
    # If we have new completed units or new session data, let's update
    return newly_completed, completed_in_json, has_new_sessions

def update_markdown_file(newly_completed_count, total_lessons_completed, content):
    """Reads, updates, and writes the personal-math.md file."""
    print(f"📈 Updating stats...")
    
    # --- Read existing values ---
    try:
        # More robust regex that handles markdown formatting, bullet points, etc.
        completed_units_match = re.search(r"\*\*Completed Units\*\*:?\s*(\d+)", content)
        if not completed_units_match:
            # Try alternative formats
            completed_units_match = re.search(r"Completed Units:?\s*(\d+)", content)
        
        if not completed_units_match:
            # Last resort: just look for the number after 'Completed Units'
            completed_units_match = re.search(r"Completed Units.*?(\d+)", content)
            
        if not completed_units_match:
            raise ValueError("Could not locate the 'Completed Units' pattern in the file")
            
        completed_units_old = int(completed_units_match.group(1))
        print(f"Found completed units: {completed_units_old}")
    except (AttributeError, ValueError) as e:
        print(f"❌ Could not parse 'Completed Units' from {MARKDOWN_FILE}: {e}")
        return False

    # --- Calculate new values using baseline constants ---
    new_completed_units = completed_units_old + newly_completed_count
    new_remaining_units = TOTAL_UNITS_IN_COURSE - new_completed_units
    total_lessons_remaining = new_remaining_units * BASE_LESSONS_PER_UNIT
    lessons_per_day_required = total_lessons_remaining / GOAL_DAYS
    time_per_day_required_mins = lessons_per_day_required * BASE_MINS_PER_LESSON
    
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
    return True

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
    newly_completed, all_completed_in_json, has_new_sessions = get_newly_completed_units(json_data, state_data)
    
    # Get the current scrape timestamp
    current_scrape_date = json_data.get('scraped_at', datetime.now().isoformat())[:10]  # Keep just the date part
    
    new_total_lessons = json_data.get('total_lessons_completed', 0)
    old_total_lessons = state_data.get('total_lessons_completed', 0)

    # Detect changes in various ways
    has_new_units = bool(newly_completed)
    has_new_lessons = new_total_lessons != old_total_lessons
    
    # Force update if scraping timestamp has changed significantly (new day)
    last_scrape_date = state_data.get('last_scrape_date', '')
    force_update = current_scrape_date != last_scrape_date
    
    # Log what's happening
    print(f"🔍 Checking for changes...")
    print(f"   - New units completed: {'Yes' if has_new_units else 'No'}")
    print(f"   - New lessons count: {'Yes' if has_new_lessons else 'No'} ({old_total_lessons} → {new_total_lessons})")
    print(f"   - New sessions detected: {'Yes' if has_new_sessions else 'No'}")
    print(f"   - Last scrape date: {last_scrape_date}, Current: {current_scrape_date}")

    # Initialize Pushover notifier
    notifier = PushoverNotifier()

    # Decide whether to update based on new units, new lessons, new sessions or force update
    if has_new_units or has_new_lessons or has_new_sessions or force_update:
        print(f"🔄 Changes detected, updating tracker data...")
        
        with open(MARKDOWN_FILE, 'r') as f:
            content = f.read()
            
        success = update_markdown_file(len(newly_completed), new_total_lessons, content)
        
        if success:
            # Update the state file with ALL new information
            state_data['processed_units'] = list(all_completed_in_json)
            state_data['total_lessons_completed'] = new_total_lessons
            state_data['last_scrape_date'] = current_scrape_date
            state_data['last_update_timestamp'] = datetime.now().isoformat()
            
            with open(STATE_FILE, 'w') as f:
                json.dump(state_data, f, indent=2)
            print(f"✅ State file '{STATE_FILE}' updated with latest data.")
            
            # Send push notification with updated progress
            if notifier.is_enabled():
                # Calculate current metrics for notification
                new_completed_units = len(newly_completed)
                new_remaining_units = TOTAL_UNITS_IN_COURSE - len(all_completed_in_json)
                total_lessons_remaining = new_remaining_units * BASE_LESSONS_PER_UNIT
                lessons_per_day_required = total_lessons_remaining / GOAL_DAYS
                time_per_day_required_mins = lessons_per_day_required * BASE_MINS_PER_LESSON
                
                hours = int(time_per_day_required_mins // 60)
                minutes = int(time_per_day_required_mins % 60)
                time_per_day_str = f"~{hours}h {minutes}m"
                
                # If we have new units, highlight that in the notification
                if has_new_units:
                    notifier.send_daily_update(
                        newly_completed_units=len(newly_completed),
                        total_lessons=new_total_lessons,
                        lessons_per_day_required=lessons_per_day_required,
                        time_per_day_required=time_per_day_str
                    )
                # Otherwise just show updated metrics
                else:
                    notifier.send_daily_update(
                        newly_completed_units=0,  # No new completed units
                        total_lessons=new_total_lessons,
                        lessons_per_day_required=lessons_per_day_required,
                        time_per_day_required=time_per_day_str
                    )
        else:
            print("❌ Failed to update markdown file.")
    else:
        print("✅ No changes detected since last check. No updates needed.")
        
        # Even if no changes, we should update the last scrape date
        state_data['last_scrape_date'] = current_scrape_date
        with open(STATE_FILE, 'w') as f:
            json.dump(state_data, f, indent=2)

if __name__ == "__main__":
    main() 