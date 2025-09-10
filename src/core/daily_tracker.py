#!/usr/bin/env python3
"""
Daily Duolingo Tracker
Orchestrates the scraping of duome.eu, parsing the data, and updating
the progress-dashboard.md file with the latest progress and projections.
"""

import os
import json
import sys
import time

# Setup project paths - must be done before other imports
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..')))      # /src
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..', '..')))  # project root
from datetime import datetime
# Notification sending is no longer handled here; see scripts/send_simple_notification.py

# --- Configuration (centralised) ---
from config import app_config as cfg

# --- Import extracted modules ---
from .metrics_calculator import (
    count_todays_lessons,
    calculate_daily_lesson_goal,
)
from .markdown_updater import update_markdown_file
from utils.logger import OWLLogger
from data.repository import AtomicJSONRepository
from .tracker_helpers import (
    run_scraper_and_load_data,
    analyze_changes,
    reconcile_state_data,
    update_data_if_changed,
)

# All constants imported directly from cfg

# Initialize logger as module-level variable
logger = None

def get_current_date():
    """Get current date as YYYY-MM-DD string."""
    return datetime.now().strftime('%Y-%m-%d')

def get_current_time_slot():
    """Determine current time slot for notifications."""
    hour = datetime.now().hour
    
    if cfg.MORNING_START_HOUR <= hour < cfg.MORNING_END_HOUR:
        return 'morning'
    elif cfg.MORNING_END_HOUR <= hour < cfg.MIDDAY_END_HOUR:
        return 'midday'
    elif cfg.MIDDAY_END_HOUR <= hour < cfg.EVENING_END_HOUR:
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
        state_data['daily_goal_lessons'] = calculate_daily_lesson_goal(state_data)  # Now returns hardcoded 12
        state_data['last_daily_reset'] = current_date
        print(f"🌅 New day detected! Reset daily counters for {current_date}")
        print(f"   Today's lessons found: {todays_lessons}")
        try:
            if logger:
                logger.info(f"New day reset: {current_date}, today's lessons: {todays_lessons}")
        except: pass
        return True, state_data
    
    return False, state_data

# Metrics calculation functions moved to metrics_calculator.py


# Helper functions moved to tracker_helpers.py
def _load_and_initialize():
    """Load state and initialize logging"""
    import sys
    run_type = "automated" if len(sys.argv) == 1 and 'launchd' in str(sys.argv) else "manual"
    global logger
    logger = OWLLogger("daily_tracker", run_type)
    logger.execution_step("Daily tracker started")
    
    # Load state data
    state_repo = AtomicJSONRepository(cfg.STATE_FILE, auto_migrate=True)
    state_data = state_repo.load({})
    # Log state file stats to help diagnose I/O hangs
    try:
        state_path = cfg.STATE_FILE
        exists = os.path.exists(state_path)
        if exists:
            size = os.path.getsize(state_path)
            mtime = datetime.fromtimestamp(os.path.getmtime(state_path)).isoformat()
            print(f" State file: {state_path} (exists=True, size={size}B, mtime={mtime})")
        else:
            print(f" State file: {state_path} (exists=False)")
    except Exception as e:
        print(f" Error finding latest JSON file: {e}")
        return None

    return state_repo, state_data

def main():
    """Main execution function."""
    # Initialize logging and load state
    state_repo, state_data = _load_and_initialize()
    
    # Run scraper and load data
    json_data, latest_json_path = run_scraper_and_load_data(logger=logger)
    if json_data is None:
        return
    
    # Handle daily reset
    daily_reset_occurred, state_data = reset_daily_lessons_if_needed(state_data, json_data)
    current_time_slot = get_current_time_slot()
    print(f"🕐 Current time slot: {current_time_slot}")
    
    # Analyze changes
    (newly_completed, all_completed_in_json, has_new_sessions, current_scrape_date,
     new_total_lessons, new_core_lessons, new_practice_sessions, old_computed_total) = analyze_changes(json_data, state_data)
    
    # Reconcile state and detect changes
    (has_new_lessons, has_new_daily_sessions, has_total_increase, 
     actual_today_sessions, stored_daily_sessions) = reconcile_state_data(json_data, state_data)
    
    # Determine various change flags
    has_new_units = bool(newly_completed)
    last_scrape_date = state_data.get('last_scrape_date', '')
    force_update = current_scrape_date != last_scrape_date
    
    # Log what's happening
    print(f"🔍 Checking for changes...")
    print(f"   - New units completed: {'Yes' if has_new_units else 'No'}")
    print(f"   - New daily sessions: {'Yes' if has_new_daily_sessions else 'No'} ({stored_daily_sessions} → {actual_today_sessions})")
    print(f"   - Total count changed: {'Yes' if has_total_increase else 'No'} ({old_computed_total} → {new_total_lessons})")
    print(f"   - Overall new lessons: {'Yes' if has_new_lessons else 'No'}")
    print(f"   - New sessions detected: {'Yes' if has_new_sessions else 'No'}")
    print(f"   - Last scrape date: {last_scrape_date}, Current: {current_scrape_date}")
    
    # Update data if needed
    update_data_if_changed(has_new_units, has_new_lessons, has_new_sessions, force_update, newly_completed, 
                           new_total_lessons, new_core_lessons, new_practice_sessions, all_completed_in_json,
                           current_scrape_date, json_data, state_data, state_repo, logger=logger)
    
    # Notifications are now handled by scripts/send_simple_notification.py on a fixed cron schedule.
    # Intentionally do not send notifications here to avoid duplicates.
    # _send_notifications_if_enabled(has_new_lessons, has_new_units, newly_completed, json_data, state_data, state_repo, current_time_slot)


if __name__ == "__main__":
    main()