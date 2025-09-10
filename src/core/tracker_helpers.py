#!/usr/bin/env python3
"""Helper functions for the daily tracker to reduce file size and improve clarity.

This module contains cohesive helper routines extracted from daily_tracker.py:
- Running the scraper
- Loading the latest JSON data
- Analyzing changes between state and JSON data
- Reconciling and updating state/markdown when changes occur
"""
from __future__ import annotations

import os
import glob
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from config import app_config as cfg
from .markdown_updater import update_markdown_file
from .metrics_calculator import (
    count_todays_lessons,
)
from utils.validation import validate_venv_python


def run_scraper(logger=None) -> bool:
    """Run the duome_raw_scraper.py script to get the latest data."""
    print("🚀 Starting scraper to fetch latest data...")
    try:
        venv_python = cfg.VENV_PYTHON_PATH
        if not validate_venv_python():
            return False

        scraper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scrapers', 'duome_raw_scraper.py'))
        start_ts = time.time()
        cmd = [venv_python, scraper_path, '--username', cfg.USERNAME]
        timeout_secs = getattr(cfg, 'SCRAPER_TIMEOUT_SECONDS', 120)
        print(f"▶️ Running scraper: {cmd} (timeout={timeout_secs}s)")
        import subprocess
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_secs
        )
        duration = time.time() - start_ts
        stdout_len = len(result.stdout or "") if hasattr(result, 'stdout') else 0
        stderr_len = len(result.stderr or "") if hasattr(result, 'stderr') else 0
        print(f"✅ Scraper ran successfully in {duration:.1f}s. stdout={stdout_len} chars, stderr={stderr_len} chars")
        try:
            if logger:
                logger.external_call("scraper", "completed", success=True)
        except:  # noqa: E722
            pass
        return True
    except subprocess.TimeoutExpired as e:  # type: ignore[name-defined]
        print(f"⏱️ Scraper timed out after {getattr(cfg, 'SCRAPER_TIMEOUT_SECONDS', 120)}s. Initiating cleanup...")
        try:
            import subprocess as sp
            sp.run(['pkill', '-f', 'geckodriver'], capture_output=True)
            sp.run(['pkill', '-f', 'firefox.*--headless'], capture_output=True)
            sp.run(['pkill', '-f', 'firefox.*--marionette'], capture_output=True)
            sp.run(['pkill', '-f', 'plugin-container'], capture_output=True)
            sp.run(['pkill', '-f', 'duome_raw_scraper.py'], capture_output=True)
        except Exception:
            pass
        try:
            if logger:
                logger.external_call("scraper", "timeout", success=False, error=str(e))
        except:  # noqa: E722
            pass
        return False
    except subprocess.CalledProcessError as e:  # type: ignore[name-defined]
        print(f"❌ Scraper script failed with error: {getattr(e, 'stderr', '')}")
        try:
            if logger:
                logger.external_call("scraper", "failed", success=False, error=str(getattr(e, 'stderr', ''))) 
        except:  # noqa: E722
            pass
        return False
    except FileNotFoundError:
        print("❌ Scraper script not found. Make sure you are in the correct directory.")
        return False


def find_latest_json_file() -> Optional[str]:
    """Find the most recently created JSON output file."""
    try:
        pattern = os.path.join(cfg.DATA_DIR, f'duome_raw_{cfg.USERNAME}_*.json')
        list_of_files = glob.glob(pattern)
        if not list_of_files:
            return None
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    except Exception as e:
        print(f"❌ Error finding latest JSON file: {e}")
        return None


def run_scraper_and_load_data(logger=None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Run scraper and load JSON data."""
    if not run_scraper(logger=logger):
        if logger:
            logger.execution_step("Scraper failed - exiting")
        return None, None

    latest_json_path = find_latest_json_file()
    if not latest_json_path:
        print("❌ No JSON file found after running scraper.")
        if logger:
            logger.execution_step("No JSON file found - exiting")
        return None, None

    if logger:
        logger.execution_step(f"Processing data from {latest_json_path}")

    try:
        fsize = os.path.getsize(latest_json_path)
        print(f"📥 Loading JSON {latest_json_path} ({fsize}B)")
    except Exception:
        print(f"📥 Loading JSON {latest_json_path}")

    t0 = time.time()
    with open(latest_json_path, 'r') as f:
        json_data = json.load(f)
    load_dur = time.time() - t0
    try:
        session_count = len(json_data.get('sessions', []))
    except Exception:
        session_count = 'unknown'
    print(f"📥 Loaded JSON in {load_dur:.2f}s with {session_count} sessions")

    return json_data, latest_json_path


def analyze_changes(json_data: Dict[str, Any], state_data: Dict[str, Any]):
    """Analyze JSON data and state to determine changes and compute metrics."""
    # Get newly completed units and session info
    newly_completed = {
        session['unit']
        for session in json_data.get('sessions', [])
        if session.get('is_unit_completion') and session.get('unit')
    }
    json_session_dates = {
        session['datetime'][:10]
        for session in json_data.get('sessions', [])
        if session.get('datetime')
    }
    processed_units = set(state_data.get('processed_units', []))
    last_scrape_date = state_data.get('last_scrape_date', None)

    has_new_sessions = False
    if last_scrape_date:
        latest_session_date = max(json_session_dates) if json_session_dates else None
        if latest_session_date and latest_session_date > last_scrape_date:
            print(f"✨ Found new sessions since last scrape! Latest: {latest_session_date}, Last processed: {last_scrape_date}")
            has_new_sessions = True

    newly_completed = newly_completed - set(processed_units)

    current_scrape_date = datetime.now().strftime('%Y-%m-%d')
    if json_data and json_data.get('sessions'):
        latest_session = max(json_data['sessions'], key=lambda x: x.get('datetime', ''))
        current_scrape_date = latest_session.get('datetime', '')[:10]

    new_total_lessons = json_data.get('computed_total_sessions', 0)
    new_core_lessons = json_data.get('computed_lesson_count', 0)
    new_practice_sessions = json_data.get('computed_practice_count', 0)
    old_computed_total = state_data.get('computed_total_sessions', 0)

    return (newly_completed, set(processed_units) | (newly_completed | set()), has_new_sessions, current_scrape_date,
            new_total_lessons, new_core_lessons, new_practice_sessions, old_computed_total)


def reconcile_state_data(json_data: Dict[str, Any], state_data: Dict[str, Any]):
    """Handle state reconciliation and detect changes."""
    current_date = datetime.now().strftime('%Y-%m-%d')
    actual_today_sessions = count_todays_lessons(json_data, current_date)
    stored_daily_sessions = state_data.get('daily_lessons_completed', 0)

    new_total_lessons = json_data.get('computed_total_sessions', 0)
    old_computed_total = state_data.get('computed_total_sessions', 0)

    total_diff = new_total_lessons - old_computed_total
    daily_diff = actual_today_sessions - stored_daily_sessions

    print(f"📊 State reconciliation check:")
    print(f"   - State total: {old_computed_total} → Fresh data: {new_total_lessons} (diff: {total_diff:+d})")
    print(f"   - State daily: {stored_daily_sessions} → Actual today: {actual_today_sessions} (diff: {daily_diff:+d})")

    has_new_daily_sessions = actual_today_sessions > stored_daily_sessions
    has_total_increase = new_total_lessons > old_computed_total
    has_new_lessons = has_new_daily_sessions or has_total_increase

    if has_new_daily_sessions:
        print(f"🆕 Found {daily_diff} new sessions today! Updating daily counter: {stored_daily_sessions} → {actual_today_sessions}")
        state_data['daily_lessons_completed'] = actual_today_sessions
    elif total_diff != 0:
        print(f"📉 Data window changed (total: {total_diff:+d}), but daily count stays accurate at {actual_today_sessions}")
        state_data['daily_lessons_completed'] = actual_today_sessions

    return has_new_lessons, has_new_daily_sessions, has_total_increase, actual_today_sessions, stored_daily_sessions


def update_data_if_changed(
    has_new_units: bool,
    has_new_lessons: bool,
    has_new_sessions: bool,
    force_update: bool,
    newly_completed,
    new_total_lessons: int,
    new_core_lessons: int,
    new_practice_sessions: int,
    all_completed_in_json,
    current_scrape_date: str,
    json_data: Dict[str, Any],
    state_data: Dict[str, Any],
    state_repo,
    logger=None,
) -> None:
    """Update markdown and state data if changes detected."""
    if has_new_units or has_new_lessons or has_new_sessions or force_update:
        print(f"🔄 Changes detected, updating tracker data...")

        with open(cfg.MARKDOWN_FILE, 'r') as f:
            content = f.read()
        print(f"📝 Loaded markdown from '{cfg.MARKDOWN_FILE}' (len={len(content)})")

        success = update_markdown_file(
            newly_completed_count=len(newly_completed),
            total_lessons_count=new_total_lessons,
            content=content,
            core_lessons=new_core_lessons,
            practice_sessions=new_practice_sessions,
            json_data=json_data,
            state_data=state_data,
        )
        print(f"🧮 Markdown update completed (success={success})")

        if success:
            state_data['processed_units'] = list(all_completed_in_json)
            state_data['computed_total_sessions'] = new_total_lessons
            state_data['computed_lesson_count'] = new_core_lessons
            state_data['computed_practice_count'] = new_practice_sessions
            state_data['total_lessons_completed'] = new_total_lessons
            state_data['last_scrape_date'] = current_scrape_date

            save_start = time.time()
            if state_repo.save(state_data):
                print(f"✅ State file '{cfg.STATE_FILE}' updated with latest data.")
                print(f"💾 State save completed in {time.time()-save_start:.2f}s")
            else:
                print(f"❌ Failed to save state file '{cfg.STATE_FILE}'")
        else:
            print("❌ Failed to update markdown file.")
    else:
        print("✅ No changes detected since last check. No updates needed.")
        state_data['last_scrape_date'] = current_scrape_date
        save_start = time.time()
        state_repo.save(state_data)
        print(f"💾 State save (no changes) completed in {time.time()-save_start:.2f}s")
