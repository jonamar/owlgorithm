#!/usr/bin/env python3
"""
Daily Duolingo Tracker
Orchestrates the scraping of duome.eu, parsing the data, and updating
the progress-dashboard.md file with the latest progress and projections.
"""

import os
import json
import re
import subprocess
import sys

# Setup project paths - must be done before other imports
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..')))      # /src
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..', '..')))  # project root
import glob
from datetime import datetime, timedelta
from notifiers.pushover_notifier import PushoverNotifier

# --- Configuration (centralised) ---
from config import app_config as cfg

# --- Import extracted modules ---
from .metrics_calculator import (
    count_todays_lessons,
    calculate_daily_lesson_goal, 
    calculate_daily_progress,
    calculate_performance_metrics
)
from .markdown_updater import update_markdown_file
from utils.logger import get_logger, OWLLogger
from utils.validation import validate_venv_python
from data.repository import AtomicJSONRepository

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

def _should_throttle_notification(last_notification_time, has_data_changes):
    """
    Determine if notification should be throttled based on last timestamp and data changes.
    
    Args:
        last_notification_time (str|None): ISO timestamp of last notification
        has_data_changes (bool): Whether data changes were detected
        
    Returns:
        tuple: (should_throttle, minutes_remaining)
    """
    if has_data_changes or not last_notification_time:
        return False, 0
    
    try:
        last_time = datetime.fromisoformat(last_notification_time)
        time_diff = datetime.now() - last_time
        throttle_duration = timedelta(hours=getattr(cfg, 'NOTIFICATION_THROTTLE_HOURS', 2.5))
        
        if time_diff < throttle_duration:
            time_remaining = throttle_duration - time_diff
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            return True, minutes_remaining
            
    except (ValueError, TypeError) as e:
        # Handle corrupted/malformed timestamps gracefully
        print(f"⚠️  Invalid notification timestamp format: {last_notification_time}")
        if logger:
            logger.external_call("notification", "invalid_timestamp", success=False, error=str(e))
    
    return False, 0

def send_time_based_notification(notifier, time_slot, state_data, has_new_lessons, has_new_units, units_completed, json_data):
    """Send simplified notification - with configurable throttling when no data changes."""
    # Ensure state_data is a dict
    if state_data is None:
        state_data = {}
    
    # Check if we have any data changes
    has_data_changes = has_new_lessons or has_new_units
    
    # Get current timestamp once
    current_time = datetime.now()
    current_timestamp = current_time.isoformat()
    
    # Check throttling logic
    last_notification_time = state_data.get('last_notification_timestamp')
    should_throttle, minutes_remaining = _should_throttle_notification(last_notification_time, has_data_changes)
    
    if should_throttle:
        print(f"⏳ No data changes - notification throttled (next in {minutes_remaining} minutes)")
        return False
    
    # Send notification
    daily_progress = calculate_daily_progress(state_data)
    total_lessons = state_data.get('computed_total_sessions', 0)
    
    notifier.send_simple_notification(
        daily_progress=daily_progress,
        units_completed=units_completed,
        total_lessons=total_lessons,
        state_data=state_data,
        json_data=json_data
    )
    
    # Update notification timestamp
    state_data['last_notification_timestamp'] = current_timestamp
    
    # Log success
    change_status = "with data changes" if has_data_changes else "after throttle period"
    print(f"📱 Push notification sent successfully ({change_status})!")
    
    try:
        if logger:
            logger.external_call("notification", "sent_unified", success=True)
    except: 
        pass
    
    return True

def run_scraper():
    """Runs the duome_raw_scraper.py script to get the latest data."""
    print("🚀 Starting scraper to fetch latest data...")
    try:
        # Find the python executable in the virtual environment
        venv_python = cfg.VENV_PYTHON_PATH
        if not validate_venv_python():
            return False

        # Run the scraper script
        subprocess.run(
            [venv_python, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scrapers', 'duome_raw_scraper.py')), '--username', cfg.USERNAME],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Scraper ran successfully.")
        try:
            if logger:
                logger.external_call("scraper", "completed", success=True)
        except: pass
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraper script failed with error: {e.stderr}")
        try:
            if logger:
                logger.external_call("scraper", "failed", success=False, error=str(e.stderr))
        except: pass
        return False
    except FileNotFoundError:
        print("❌ Scraper script not found. Make sure you are in the correct directory.")
        return False

def find_latest_json_file():
    """Finds the most recently created JSON output file."""
    try:
        # Look for JSON files in the data directory
        pattern = os.path.join(cfg.DATA_DIR, f'duome_raw_{cfg.USERNAME}_*.json')
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
    # Initialize logging with automation detection
    import sys
    run_type = "automated" if len(sys.argv) == 1 and 'launchd' in str(sys.argv) else "manual"
    global logger
    logger = OWLLogger("daily_tracker", run_type)
    logger.execution_step("Daily tracker started")
    
    if not run_scraper():
        logger.execution_step("Scraper failed - exiting")
        return

    latest_json_path = find_latest_json_file()
    if not latest_json_path:
        print("❌ No JSON file found after running scraper.")
        logger.execution_step("No JSON file found - exiting")
        return
    
    logger.execution_step(f"Processing data from {latest_json_path}")

    with open(latest_json_path, 'r') as f:
        json_data = json.load(f)
        
    # Load or create state data using atomic operations with versioning
    state_repo = AtomicJSONRepository(cfg.STATE_FILE, auto_migrate=True)
    state_data = state_repo.load({})

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

    # === STATE RECONCILIATION ===
    # Handle duome.eu data window changes (sessions may drop out or be added)
    current_date = get_current_date()
    actual_today_sessions = count_todays_lessons(json_data, current_date)
    stored_daily_sessions = state_data.get('daily_lessons_completed', 0)
    
    # If fresh data total differs significantly from state, reconcile using daily counts
    total_diff = new_total_lessons - old_computed_total
    daily_diff = actual_today_sessions - stored_daily_sessions
    
    print(f"📊 State reconciliation check:")
    print(f"   - State total: {old_computed_total} → Fresh data: {new_total_lessons} (diff: {total_diff:+d})")
    print(f"   - State daily: {stored_daily_sessions} → Actual today: {actual_today_sessions} (diff: {daily_diff:+d})")
    
    # Detect changes using multiple approaches
    has_new_units = bool(newly_completed)
    
    # Primary: Check if today's sessions increased (most reliable)
    has_new_daily_sessions = actual_today_sessions > stored_daily_sessions
    
    # Secondary: Check total count increase (but handle data window changes)
    has_total_increase = new_total_lessons > old_computed_total
    
    # Overall: Has new lessons if either daily increased OR total increased significantly
    has_new_lessons = has_new_daily_sessions or has_total_increase
    
    # Update daily counter based on actual data (most reliable)
    if has_new_daily_sessions:
        print(f"🆕 Found {daily_diff} new sessions today! Updating daily counter: {stored_daily_sessions} → {actual_today_sessions}")
        state_data['daily_lessons_completed'] = actual_today_sessions
    elif total_diff != 0:
        # Handle data window changes - keep daily count accurate
        print(f"📉 Data window changed (total: {total_diff:+d}), but daily count stays accurate at {actual_today_sessions}")
        state_data['daily_lessons_completed'] = actual_today_sessions
    
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

    # Initialize Pushover notifier
    notifier = PushoverNotifier()

    # Update data if changes detected
    if has_new_units or has_new_lessons or has_new_sessions or force_update:
        print(f"🔄 Changes detected, updating tracker data...")
        
        # Get markdown content
        with open(cfg.MARKDOWN_FILE, 'r') as f:
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
            
            # Write the updated state back to disk atomically
            if state_repo.save(state_data):
                print(f"✅ State file '{cfg.STATE_FILE}' updated with latest data.")
            else:
                print(f"❌ Failed to save state file '{cfg.STATE_FILE}'")
        else:
            print("❌ Failed to update markdown file.")
    else:
        print("✅ No changes detected since last check. No updates needed.")
        
        # Even if no changes, we should update the last scrape date
        state_data['last_scrape_date'] = current_scrape_date
        state_repo.save(state_data)

    # Send time-based notifications with throttling logic
    if notifier.is_enabled():
        notification_sent = send_time_based_notification(
            notifier, current_time_slot, state_data, 
            has_new_lessons, has_new_units, len(newly_completed), json_data
        )
        
        # Save state if notification was sent (to persist timestamp)
        if notification_sent:
            state_repo.save(state_data)


if __name__ == "__main__":
    main()