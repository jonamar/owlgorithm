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
import sys

# Adjust Python path to import sibling and project-level packages
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))      # /src
sys.path.append(os.path.abspath(os.path.join(current_dir, '..', '..')))  # project root
import glob
from datetime import datetime
from notifiers.pushover_notifier import PushoverNotifier

# --- Configuration (centralised) ---
from config import app_config as cfg

# --- Import extracted modules ---
from .metrics_calculator import (
    count_todays_lessons,
    calculate_daily_lesson_goal, 
    calculate_daily_progress,
    calculate_unit_completion_metrics,
    calculate_performance_metrics
)
from .markdown_updater import update_markdown_file

MARKDOWN_FILE = cfg.MARKDOWN_FILE
STATE_FILE = cfg.STATE_FILE
USERNAME = cfg.USERNAME
TOTAL_UNITS_IN_COURSE = cfg.TOTAL_UNITS_IN_COURSE
GOAL_DAYS = cfg.GOAL_DAYS  # 18 months

# --- Baseline Metrics (from config) ---
BASE_LESSONS_PER_UNIT = cfg.BASE_LESSONS_PER_UNIT
BASE_MINS_PER_LESSON = cfg.BASE_MINS_PER_LESSON

def get_current_date():
    """Get current date as YYYY-MM-DD string."""
    return datetime.now().strftime('%Y-%m-%d')

def get_current_time_slot():
    """Determine current time slot for notifications."""
    hour = datetime.now().hour
    
    if 5 <= hour < 11:
        return 'morning'
    elif 11 <= hour < 16:
        return 'midday'
    elif 16 <= hour < 21:
        return 'evening'
    else:
        return 'night'

def reset_daily_lessons_if_needed(state_data, json_data=None):
    """Reset daily lesson counters if it's a new day."""
    current_date = get_current_date()
    last_daily_reset = state_data.get('last_daily_reset', '')
    
    if current_date != last_daily_reset:
        # Count today's lessons from JSON data if available
        todays_lessons = 0
        if json_data:
            todays_lessons = count_todays_lessons(json_data, current_date)
        
        # Reset daily counters
        state_data['daily_lessons_completed'] = todays_lessons
        state_data['daily_goal_lessons'] = calculate_daily_lesson_goal(state_data)
        state_data['last_daily_reset'] = current_date
        print(f"🌅 New day detected! Reset daily counters for {current_date}")
        print(f"   Today's lessons found: {todays_lessons}")
        return True, state_data
    
    return False, state_data

# Metrics calculation functions moved to metrics_calculator.py

def send_time_based_notification(notifier, time_slot, state_data, has_new_lessons, has_new_units, units_completed, json_data):
    """Send appropriate notification based on current time slot."""
    daily_progress = calculate_daily_progress(state_data)
    
    # Get overall trajectory info
    total_completed_units = len(state_data.get('processed_units', []))
    total_progress_pct = (total_completed_units / TOTAL_UNITS_IN_COURSE) * 100
    trajectory_info = {'progress_pct': total_progress_pct}
    
    # Get streak from scraper data
    current_streak = json_data.get('current_streak', 0)
    
    # Determine if we should send notification based on time slot and activity
    should_send = False
    
    if time_slot == 'morning':
        # Morning: Always send goal-setting message  
        should_send = True
        # Get yesterday's progress if available
        yesterday_progress = state_data.get('yesterday_progress')
        notifier.send_morning_notification(
            daily_goal=daily_progress['goal'],
            current_streak=current_streak,
            yesterday_progress=yesterday_progress
        )
        
    elif time_slot == 'midday':
        # Midday: Always send (simplified logic)
        should_send = True
        notifier.send_midday_notification(daily_progress)
            
    elif time_slot == 'evening':
        # Evening: Always send (simplified logic)  
        should_send = True
        notifier.send_evening_notification(daily_progress)
            
    elif time_slot == 'night':
        # Night: Always send recap
        should_send = True
        notifier.send_night_notification(
            daily_progress=daily_progress,
            units_completed=units_completed,
            trajectory_info=trajectory_info
        )
        
        # Save today's progress as yesterday's for tomorrow morning
        state_data['yesterday_progress'] = daily_progress.copy()
    
    if should_send:
        print(f"📱 Sent {time_slot} notification")
    else:
        print(f"⏭️  Skipped {time_slot} notification - no activity detected")

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
            [venv_python, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scrapers', 'duome_raw_scraper.py')), '--username', USERNAME],
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
        # Look for JSON files in the data directory
        pattern = os.path.join(cfg.DATA_DIR, f'duome_raw_{USERNAME}_*.json')
        list_of_files = glob.glob(pattern)
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

# Large metrics calculation functions moved to metrics_calculator.py

# Markdown file update function moved to markdown_updater.py

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

    # Handle daily lesson tracking (now that we have json_data)
    daily_reset_occurred, state_data = reset_daily_lessons_if_needed(state_data, json_data)
    current_time_slot = get_current_time_slot()
    
    print(f"🕐 Current time slot: {current_time_slot}")

    # Check for changes
    newly_completed, all_completed_in_json, has_new_sessions = get_newly_completed_units(json_data, state_data)
    
    # Get the current scrape timestamp
    current_scrape_date = json_data.get('scraped_at', datetime.now().isoformat())[:10]  # Keep just the date part
    
    # Switch to computed totals (more accurate than duome's reported lessons)
    new_total_lessons = json_data.get('computed_total_sessions', 0)  # Use computed_total_sessions (lessons + practice)
    new_core_lessons = json_data.get('computed_lesson_count', 0)  # Core lessons only
    new_practice_sessions = json_data.get('computed_practice_count', 0)  # Practice sessions only
    
    # Track both old metrics for backwards compatibility
    old_total_lessons = state_data.get('total_lessons_completed', 0)  # Legacy field
    old_computed_total = state_data.get('computed_total_sessions', 0)  # New computed field

    # Detect changes in various ways
    has_new_units = bool(newly_completed)
    has_new_lessons = new_total_lessons > old_total_lessons or new_total_lessons > old_computed_total
    
    # Update daily lesson counter
    if new_total_lessons > old_computed_total:
        new_daily_lessons = new_total_lessons - old_computed_total
        current_daily_lessons = state_data.get('daily_lessons_completed', 0)
        state_data['daily_lessons_completed'] = current_daily_lessons + new_daily_lessons
        print(f"🆕 Found {new_daily_lessons} new sessions today! Total today: {state_data['daily_lessons_completed']}")
        print(f"   - Breakdown: {new_core_lessons} total lessons, {new_practice_sessions} total practice")
    
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

    # Update data if changes detected
    if has_new_units or has_new_lessons or has_new_sessions or force_update:
        print(f"🔄 Changes detected, updating tracker data...")
        
        # Get markdown content
        with open(MARKDOWN_FILE, 'r') as f:
            content = f.read()
            
        # Now pass all computed metrics to the markdown update function
        success = update_markdown_file(
            newly_completed_count=len(newly_completed), 
            total_lessons_count=new_total_lessons, 
            content=content,
            core_lessons=new_core_lessons,
            practice_sessions=new_practice_sessions,
            json_data=json_data,
            state_data=state_data
        )
        
        if success:
            # Save state to avoid re-processing
            state_data['processed_units'] = list(all_completed_in_json)
            
            # Update with computed metrics (more reliable than duome.eu reported lessons)
            state_data['computed_total_sessions'] = new_total_lessons
            state_data['computed_lesson_count'] = new_core_lessons
            state_data['computed_practice_count'] = new_practice_sessions
            state_data['total_lessons_completed'] = new_total_lessons  # Legacy field, now using computed total
            
            state_data['last_scrape_date'] = current_scrape_date
            
            # Write the updated state back to disk
            with open(STATE_FILE, 'w') as f:
                json.dump(state_data, f, indent=2)
            print(f"✅ State file '{STATE_FILE}' updated with latest data.")
        else:
            print("❌ Failed to update markdown file.")
    else:
        print("✅ No changes detected since last check. No updates needed.")
        
        # Even if no changes, we should update the last scrape date
        state_data['last_scrape_date'] = current_scrape_date
        with open(STATE_FILE, 'w') as f:
            json.dump(state_data, f, indent=2)

    # Send time-based notifications REGARDLESS of whether data changed
    if notifier.is_enabled():
        send_time_based_notification(
            notifier, current_time_slot, state_data, 
            has_new_lessons, has_new_units, len(newly_completed), json_data
        )

 