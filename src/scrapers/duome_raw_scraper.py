#!/usr/bin/env python3
"""
Enhanced Duome Raw Data Scraper with Auto-Update
Fetches and analyzes Duolingo session data directly from duome.eu
Automatically clicks the "update your stats" button before scraping
Now includes daily lesson counts and unit-specific analysis
"""

import os
import sys

# Add project root and src to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SRC_DIR)

import re
import json
import requests
from datetime import datetime
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Removed Chrome imports - using Firefox only
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import app_config as cfg
from utils.constants import DEFAULT_SCRAPE_DELAY, DEFAULT_REQUEST_TIMEOUT

def validate_headless_update_with_timestamps(username, wait_seconds=cfg.VALIDATION_WAIT_SECONDS):
    """
    Validate that headless button clicks work by checking timestamp changes.
    
    Approach: Run headless scraping twice, 30 seconds apart, and verify that
    the timestamp in .duo-the-owl-offset .cCCC updates between runs.
    
    Returns:
        dict: {
            'success': bool,
            'first_timestamp': str,
            'second_timestamp': str,
            'timestamp_changed': bool,
            'message': str
        }
    """
    print(f"🕐 Starting headless validation: running twice {wait_seconds}s apart...")
    
    # First run
    print("📱 First headless run...")
    first_result = scrape_duome_headless_with_timestamp(username)
    if not first_result['success']:
        return {
            'success': False,
            'first_timestamp': None,
            'second_timestamp': None,
            'timestamp_changed': False,
            'message': f"First run failed: {first_result['message']}"
        }
    
    first_timestamp = first_result['timestamp']
    print(f"✅ First run timestamp: {first_timestamp}")
    
    # Wait between runs
    print(f"⏳ Waiting {wait_seconds} seconds before second run...")
    time.sleep(wait_seconds)
    
    # Second run  
    print("📱 Second headless run...")
    second_result = scrape_duome_headless_with_timestamp(username)
    if not second_result['success']:
        return {
            'success': False,
            'first_timestamp': first_timestamp,
            'second_timestamp': None,
            'timestamp_changed': False,
            'message': f"Second run failed: {second_result['message']}"
        }
    
    second_timestamp = second_result['timestamp']
    print(f"✅ Second run timestamp: {second_timestamp}")
    
    # Check if timestamp changed
    timestamp_changed = first_timestamp != second_timestamp
    
    if timestamp_changed:
        message = "🎉 Headless validation SUCCESS: Timestamps changed, button clicks working!"
    else:
        message = "⚠️ Headless validation UNCLEAR: Timestamps identical, may indicate stale data"
    
    print(message)
    
    return {
        'success': True,
        'first_timestamp': first_timestamp,
        'second_timestamp': second_timestamp,
        'timestamp_changed': timestamp_changed,
        'message': message
    }


def scrape_duome_headless_with_timestamp(username):
    """
    Headless scrape focused on timestamp extraction for validation.
    
    Returns:
        dict: {
            'success': bool,
            'timestamp': str or None,
            'message': str
        }
    """
    driver = None
    try:
        print(f"🔄 Starting headless timestamp scrape for {username}...")
        
        # Setup headless Firefox
        driver = setup_firefox_driver(headless=True)
        from utils.path_utils import build_duome_url
        url = build_duome_url(username)
        driver.get(url)
        
        # Wait for page load
        WebDriverWait(driver, cfg.BROWSER_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Extract timestamp BEFORE update attempt
        timestamp_before = extract_duome_timestamp(driver)
        print(f"📅 Timestamp before update: {timestamp_before}")
        
        # Try to click update button
        update_success = click_duome_update_button(driver, username)
        if not update_success:
            print("⚠️ Update button click failed, but continuing...")
        
        # Wait for update to process
        time.sleep(DEFAULT_SCRAPE_DELAY)
        
        # Extract timestamp AFTER update attempt
        timestamp_after = extract_duome_timestamp(driver)
        print(f"📅 Timestamp after update: {timestamp_after}")
        
        # For validation purposes, return the BEFORE timestamp
        # This represents the state of the data when we arrived, before our update
        validation_timestamp = timestamp_before
        
        return {
            'success': True,
            'timestamp': validation_timestamp,
            'message': f"Headless scrape completed, pre-update timestamp: {validation_timestamp}"
        }
        
    except Exception as e:
        error_msg = f"Headless scrape failed: {e}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'timestamp': None,
            'message': error_msg
        }
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                cleanup_zombie_processes()  # Only cleanup on quit failure


def extract_duome_timestamp(driver):
    """
    Extract timestamp from duome.eu using the specific CSS selector.
    
    Looks for timestamp in .duo-the-owl-offset .cCCC as suggested.
    Falls back to other timestamp selectors if needed.
    
    Returns:
        str or None: Timestamp text if found
    """
    selectors = [
        # Primary: Your suggested selector
        ".duo-the-owl-offset .cCCC",
        
        # Fallbacks: Other potential timestamp locations
        ".cCCC",
        "[class*='cCCC']",
        
        # Legacy: Current XPath approach as fallback
        "//text()[contains(., 'Last update:')]/following-sibling::*[1]"
    ]
    
    for selector in selectors:
        try:
            if selector.startswith("//"):
                # XPath selector
                element = driver.find_element(By.XPATH, selector)
            else:
                # CSS selector
                element = driver.find_element(By.CSS_SELECTOR, selector)
                
            if element and element.text.strip():
                timestamp_text = element.text.strip()
                print(f"📍 Found timestamp using selector '{selector}': {timestamp_text}")
                return timestamp_text
                
        except (NoSuchElementException, AttributeError) as e:
            print(f"🔍 Selector '{selector}' not found: {e}")
            continue
    
    print("⚠️ No timestamp found with any selector")
    return None


def click_duome_update_button(driver, username):
    """
    Click the duome.eu update button with multiple fallback strategies.
    
    Returns:
        bool: True if button was clicked successfully
    """
    selectors = [
        # Target the exact element as specified
        (By.CSS_SELECTOR, f"span.fade.aggiorna.inline[data-id='{username}']"),
        (By.CSS_SELECTOR, "span.fade.aggiorna.inline"),
        (By.CSS_SELECTOR, ".aggiorna"),
        (By.XPATH, f"//span[@data-id='{username}']"),
        (By.XPATH, "//span[contains(@class, 'aggiorna')]"),
    ]
    
    for selector_type, selector in selectors:
        try:
            elements = driver.find_elements(selector_type, selector)
            if elements:
                update_button = elements[0]
                print(f"🎯 Found update button using selector: {selector}")
                try:
                    print("🖱️ Clicking update button...")
                    update_button.click()
                    print("✅ Update button clicked successfully")
                    return True
                except Exception as e:
                    print(f"❌ Standard click failed: {e}, trying JavaScript click")
                    try:
                        driver.execute_script("arguments[0].click();", update_button)
                        print("✅ JavaScript click succeeded")
                        return True
                    except Exception as e2:
                        print(f"❌ JavaScript click failed: {e2}")
        except Exception as e:
            print(f"❌ Error with selector {selector}: {e}")
            continue
    
    print("❌ Update button not found or not clickable")
    return False

def fetch_duome_data_with_update(username, headless=True):
    """Fetch raw data from duome.eu with automatic stats update using Firefox"""
    from utils.path_utils import build_duome_url
    url = build_duome_url(username)
    print(f"Opening Firefox browser and navigating to {url}...")
    
    driver = None
    try:
        print("Initializing Firefox browser...")
        driver = setup_firefox_driver(headless)
        print("✅ Firefox browser initialized successfully")
        
        # Navigate to the standard page
        driver.get(url)
        print("Navigated to duome.eu page")
        
        # Wait for page to load and update to complete
        print("Waiting for page to load and stats to update...")
        WebDriverWait(driver, cfg.BROWSER_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check for timestamp before attempting click
        timestamp_before = None
        try:
            timestamp_element = driver.find_element(By.XPATH, "//text()[contains(., 'Last update:')]/parent::*")
            timestamp_before = timestamp_element.text if timestamp_element else None
            print(f"Timestamp before update: {timestamp_before}")
        except (NoSuchElementException, AttributeError):
            print("Could not find timestamp element before update")
            
        # Try to find and click the specific update button
        print("Looking for the aggiorna update element...")
        update_clicked = False
        
        selectors = [
            # Target the exact element as specified
            (By.CSS_SELECTOR, f"span.fade.aggiorna.inline[data-id='{username}']"),
            (By.CSS_SELECTOR, "span.fade.aggiorna.inline"),
            (By.CSS_SELECTOR, ".aggiorna"),
            (By.XPATH, f"//span[@data-id='{username}']"),
            (By.XPATH, "//span[contains(@class, 'aggiorna')]"),
        ]
        
        for selector_type, selector in selectors:
            try:
                elements = driver.find_elements(selector_type, selector)
                if elements:
                    update_button = elements[0]
                    print(f"Found update button using selector: {selector}")
                    try:
                        print("Clicking update button...")
                        update_button.click()
                        update_clicked = True
                        print("Update button clicked successfully")
                        break
                    except Exception as e:
                        print(f"Standard click failed: {e}, trying JavaScript click")
                        try:
                            driver.execute_script("arguments[0].click();", update_button)
                            update_clicked = True
                            print("JavaScript click succeeded")
                            break
                        except Exception as e2:
                            print(f"JavaScript click failed: {e2}")
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        if not update_clicked:
            print("Update button not found or not clickable")
            print("Proceeding with current page data")
            
        # Give additional time for the update to complete
        print("Allowing time for stats update to complete...")
        time.sleep(DEFAULT_SCRAPE_DELAY)  # Wait time for update to process
        
        # Verify the update by checking for timestamp
        try:
            timestamp_element = driver.find_element(By.XPATH, "//text()[contains(., 'Last update:')]/following-sibling::*[1]")
            current_timestamp = timestamp_element.text if timestamp_element else "Unknown"
            print(f"Current page timestamp: {current_timestamp}")
        except (NoSuchElementException, AttributeError):
            print("Could not find timestamp element (this is normal for some page layouts)")
        
        # Get the page source after potential update
        print("Extracting page data...")
        page_source = driver.page_source
        return page_source
        
    except Exception as e:
        print(f"❌ Firefox browser automation failed: {e}")
        
        if 'firefox' in str(e).lower() or 'geckodriver' in str(e).lower():
            print("🔧 Firefox Setup Issues:")
            print("   • Install Firefox: https://www.mozilla.org/firefox/")
            print("   • Geckodriver will be auto-installed via webdriver-manager")
        elif 'permission' in str(e).lower():
            print("🔧 Permission Issues:")
            print("   • Grant Firefox accessibility permissions in System Preferences")
            print("   • Try running with sudo if needed")
        else:
            print("🔧 General browser automation error - check logs above for details")
        
        print("\n💡 Attempting fallback to direct HTTP request...")
        return None
        
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                cleanup_zombie_processes()  # Only cleanup on quit failure


def cleanup_zombie_processes():
    """Clean up hanging geckodriver processes (minimal prevention).""" 
    import subprocess
    try:
        result = subprocess.run(['pkill', '-f', 'geckodriver'], capture_output=True)
        if result.returncode == 0:
            print("🧹 Cleaned up hanging geckodriver processes")
    except Exception:
        pass  # Non-critical, continue anyway


def setup_firefox_driver(headless=True):
    """Setup Firefox WebDriver with robust process management"""
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    import shutil
    
    # Clean up any zombie processes before starting
    cleanup_zombie_processes()
    
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("--headless")
    
    # Set explicit Firefox binary path for macOS
    firefox_binary_path = "/Applications/Firefox.app/Contents/MacOS/firefox"
    if os.path.exists(firefox_binary_path):
        firefox_options.binary_location = firefox_binary_path
        print(f"Using Firefox binary at: {firefox_binary_path}")
    else:
        print("Firefox binary not found at expected location, using system PATH")
    
    # Use system geckodriver instead of webdriver-manager
    geckodriver_path = shutil.which('geckodriver')
    if geckodriver_path:
        print(f"Using system geckodriver at: {geckodriver_path}")
        service = Service(geckodriver_path)
    else:
        print("System geckodriver not found, falling back to webdriver-manager")
        from webdriver_manager.firefox import GeckoDriverManager
        service = Service(GeckoDriverManager().install())
    
    return webdriver.Firefox(service=service, options=firefox_options)


def fetch_duome_data(username):
    """
    DEPRECATED: Fetch raw data from duome.eu without automation
    
    WARNING: This method DOES NOT work for getting fresh data!
    
    duome.eu serves stale cached session data unless the "aggiorna" update 
    button is clicked via browser automation. This HTTP-only method bypasses 
    that refresh mechanism and returns outdated data.
    
    Confirmed 2025-06-30: HTTP method failed to detect new lesson completed
    at 09:20, while browser automation detected it immediately.
    
    Use fetch_duome_data_with_update() instead for reliable fresh data.
    """
    from utils.path_utils import build_duome_url
    url = build_duome_url(username)
    print(f"Fetching data from {url} (fallback method)...")
    
    try:
        # Add headers to mimic a browser request (sometimes needed to avoid blocks)  
        from utils.constants import DEFAULT_HEADERS
        headers = DEFAULT_HEADERS
        
        response = requests.get(url, headers=headers, timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.content
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def parse_session_data(html_content):
    """Parse session data from raw HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all session entries (li elements)
    session_items = soup.find_all('li')
    
    sessions = []
    unit_transitions = {}  # Track when units first appear
    
    for item in session_items:
        text = item.get_text(strip=True)
        if not text or 'XP' not in text:
            continue
            
        # Parse datetime and XP
        datetime_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', text)
        xp_match = re.search(r'(\d+)XP', text)
        
        if not datetime_match or not xp_match:
            continue
            
        datetime_str = datetime_match.group(1)
        xp = int(xp_match.group(1))
        
        # Parse datetime
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        
        # =================================================================
        # LESSON COUNTING LOGIC - CORE PRINCIPLE:
        # =================================================================
        # ALL XP-earning sessions are lessons, regardless of type/subclass.
        # Session types are metadata only - they do NOT affect lesson counting.
        # This ensures no learning activity is excluded from lesson totals.
        # =================================================================
        
        # CORE LESSON COUNT: Every session that earns XP is a lesson
        is_lesson = True  # ALWAYS TRUE - all sessions count as lessons
        
        # METADATA ONLY: Classify session types for reporting/analysis
        # These classifications do NOT affect whether it counts as a lesson
        session_type = "unknown"  # Default metadata classification
        unit = None
        is_unit_completion = False  # Special flag for unit completion tracking
        
        # Classify session type for metadata purposes only
        # CRITICAL: Only "unit review" marks unit boundaries, not all "legendary" sessions
        if "unit review" in text.lower():
            session_type = "unit_completion"
            is_unit_completion = True
        elif "legendary" in text.lower():
            session_type = "legendary_lesson"  # Legendary within unit, not unit boundary
        elif "personalized practice" in text:
            session_type = "personalized_practice" 
        elif "story /practice" in text or "story / practice" in text:
            session_type = "story_practice"
        elif "· lesson" in text:
            session_type = "unit_lesson"
            # Extract unit name from skill links for unit lessons
            skill_links = item.find_all('a', href=re.compile(r'/skill/fr/'))
            if skill_links:
                href = skill_links[0]['href']
                unit_match = re.search(r'/skill/fr/([^/]+)', href)
                if unit_match:
                    unit_name = unit_match.group(1).replace('-', ' ')
                    unit = unit_name
                    
                    # Track unit transitions (first appearance chronologically)
                    if unit not in unit_transitions:
                        unit_transitions[unit] = dt
            else:
                # Fallback: try to extract unit name from text pattern XPUnitName
                # Example: "102XPRequests· lesson" -> extract "Requests"
                unit_text_match = re.search(r'\d+XP([A-Za-z]+)·', text)
                if unit_text_match:
                    unit_name = unit_text_match.group(1)
                    unit = unit_name
                    
                    # Track unit transitions (first appearance chronologically)
                    if unit not in unit_transitions:
                        unit_transitions[unit] = dt
        # Note: Even "unknown" session types count as lessons (is_lesson = True)
        else:
            # Look for unit name in skill links
            skill_links = item.find_all('a', href=re.compile(r'/skill/fr/'))
            if skill_links:
                # Extract unit name from skill link
                href = skill_links[0]['href']
                unit_match = re.search(r'/skill/fr/([^/]+)', href)
                if unit_match:
                    unit_name = unit_match.group(1).replace('-', ' ')
                    unit = unit_name
                    session_type = "unit_lesson"
                    
                    # Track unit transitions (first appearance chronologically)
                    if unit not in unit_transitions:
                        unit_transitions[unit] = dt
        
        session = {
            'datetime': dt.isoformat(),
            'date': dt.date().isoformat(),
            'time': dt.time().isoformat(),
            'xp': xp,
            'session_type': session_type,
            'unit': unit,
            'is_lesson': is_lesson,
            'is_unit_completion': is_unit_completion,
            'raw_text': text
        }
        
        sessions.append(session)
    
    # Sort sessions chronologically (oldest first for proper unit transition detection)
    sessions.sort(key=lambda x: x['datetime'])
    
    # Now assign units based on unit completion transitions
    current_unit = None
    unit_completion_transitions = {}  # Track when units are completed
    
    # First pass: identify unit completions and their associated units
    for session in sessions:
        if session['unit']:  # This session has a unit name
            current_unit = session['unit']
        elif session['is_unit_completion'] and current_unit:
            # This is a unit completion for the current unit
            session['unit'] = current_unit
            unit_completion_transitions[current_unit] = session['datetime']
            print(f"Found unit completion for {current_unit} at {session['datetime']}")
    
    # Second pass: assign practice sessions to the correct unit based on completion transitions
    current_active_unit = None
    completed_units = set()
    
    for session in sessions:
        if session['unit'] and not session['is_unit_completion']:
            # Regular unit lesson - this unit becomes active
            current_active_unit = session['unit']
        elif session['is_unit_completion']:
            # Unit completion - mark this unit as completed
            completed_unit = session['unit']
            if completed_unit:
                completed_units.add(completed_unit)
                print(f"Unit {completed_unit} completed at {session['datetime']}")
            # After completion, no active unit until next unit starts
            current_active_unit = None
        elif session['session_type'] == 'personalized_practice' and not session['unit']:
            # Unassigned practice session - assign to current active unit
            if current_active_unit and current_active_unit not in completed_units:
                # Assign to current active unit if it's not completed yet
                session['unit'] = current_active_unit
            else:
                # If no active unit or current unit is completed, 
                # this practice belongs to the next unit (which we'll determine later)
                pass
    
    # Third pass: assign remaining practice sessions to the next unit after completion
    for i, session in enumerate(sessions):
        if session['session_type'] == 'personalized_practice' and not session['unit']:
            # Look forward to find the next unit that starts
            for j in range(i + 1, len(sessions)):
                future_session = sessions[j]
                if future_session['unit'] and not future_session['is_unit_completion']:
                    session['unit'] = future_session['unit']
                    break
    
    # Sort back to newest first for output
    sessions.sort(key=lambda x: x['datetime'], reverse=True)
    
    return sessions, unit_transitions

def calculate_daily_stats(sessions):
    """Calculate daily lesson and practice statistics"""
    daily_stats = defaultdict(lambda: {
        'total_sessions': 0,
        'total_lessons': 0,
        'total_practice': 0,
        'total_xp': 0,
        'session_types': Counter()
    })
    
    for session in sessions:
        date = session['date']
        daily_stats[date]['total_sessions'] += 1
        daily_stats[date]['total_xp'] += session['xp']
        daily_stats[date]['session_types'][session['session_type']] += 1
        
        # Since ALL sessions are lessons now (is_lesson=True always), this simplifies:
        daily_stats[date]['total_lessons'] += 1
        
        # Legacy practice count (for historical compatibility)
        # Note: This is now always 0 since all sessions count as lessons
        if session['session_type'] == 'personalized_practice':
            daily_stats[date]['total_practice'] += 1
    
    # Convert to regular dict and sort by date
    return dict(sorted(daily_stats.items(), reverse=True))

def calculate_total_lessons(sessions):
    """
    Compute total lessons from session data
    
    CORE PRINCIPLE: ALL sessions count as lessons.
    Since is_lesson=True for every session, this equals total session count.
    """
    # Every session is a lesson, so return total count
    return len(sessions)


def calculate_recent_lessons_per_unit(sessions):
    """
    Calculate lessons per unit using Algorithm 1: "First Mention = Unit Start" with Sub-unit Folding.
    
    CRITICAL CONSTRAINTS (see docs/claude.md Algorithm 1 Specifications):
    - Hard-coded start date: 2025-06-19 (Nightmare unit start - first complete unit)
    - Exclude incomplete units: On Sale (no reliable start), current active unit
    - Target validation: Requests = 34 lessons, Grooming+Reflexives = 39 lessons
    
    Algorithm:
    1. Filter to complete unit date range (2025-06-19 onwards)
    2. Detect unit boundaries by first mention of unit name (chronologically)
    3. Assign ALL XP-earning sessions to the currently active unit
    4. Fold small units (<8 lessons) into adjacent units when appropriate
    5. Exclude current incomplete unit and units without reliable starts
    
    Returns:
        dict: {
            'average_lessons_per_unit': float,
            'completed_units_analyzed': int,
            'unit_analysis': list of dicts with unit data,
            'algorithm': 'first_mention_with_folding'
        }
    """
    if not sessions:
        return None
    
    # HARD-CODED CONSTRAINT: Only analyze data from first complete unit (Nightmare) onwards
    filtered_sessions = [s for s in sessions if s['date'] >= cfg.ANALYSIS_START_DATE]
    
    print(f"📊 Algorithm 1 constraints: Using sessions from {cfg.ANALYSIS_START_DATE} onwards")
    print(f"📊 Filtered {len(sessions)} → {len(filtered_sessions)} sessions for analysis")
    
    # Sort sessions chronologically (oldest first) for proper unit detection
    sorted_sessions = sorted(filtered_sessions, key=lambda x: x['datetime'])
    
    # Step 1: Detect unit boundaries by first mention
    unit_boundaries = []
    seen_units = set()
    
    for session in sorted_sessions:
        if session.get('unit') and session['unit'] not in seen_units:
            seen_units.add(session['unit'])
            unit_boundaries.append({
                'unit': session['unit'],
                'start_datetime': session['datetime']
            })
            print(f"📊 Unit boundary detected: {session['unit']} starts at {session['datetime']}")
    
    if len(unit_boundaries) < 2:
        print(f"⚠️ Need at least 2 units for analysis, found {len(unit_boundaries)}")
        return None
    
    # Step 2: Assign ALL sessions to units based on chronological active unit
    unit_session_counts = defaultdict(int)
    current_unit = None
    
    for session in sorted_sessions:
        # Update current unit if this session has an explicit unit
        if session.get('unit'):
            current_unit = session['unit']
        
        # CRITICAL FIX: Assign unit to session object AND count it
        if current_unit:
            # Update session metadata with assigned unit (for data integrity)
            session['assigned_unit'] = current_unit
            unit_session_counts[current_unit] += 1
    
    # Step 3: Exclude incomplete units (current unit + units without reliable starts)
    unit_sequence = [b['unit'] for b in unit_boundaries]
    EXCLUDED_UNITS = {'On Sale'}  # Units without reliable start points
    
    if unit_sequence:
        current_unit_name = unit_sequence[-1]
        excluded_units = EXCLUDED_UNITS | {current_unit_name}
        print(f"📊 Excluding incomplete units: {excluded_units}")
        completed_units = {unit: count for unit, count in unit_session_counts.items() 
                          if unit not in excluded_units}
    else:
        completed_units = {unit: count for unit, count in unit_session_counts.items() 
                          if unit not in EXCLUDED_UNITS}
    
    # Step 4: Apply sub-unit folding for small units
    final_unit_counts = {}
    folded_units = set()
    
    for i, unit in enumerate(unit_sequence[:-1]):  # Exclude current unit
        if unit in folded_units:
            continue
            
        lesson_count = completed_units.get(unit, 0)
        
        if lesson_count < 8:  # Small unit - check for folding
            # Find adjacent unit to fold into
            target_unit = None
            if i > 0:
                target_unit = unit_sequence[i-1]
            elif i < len(unit_sequence) - 2:  # Not current unit
                target_unit = unit_sequence[i+1]
            
            if target_unit and target_unit in completed_units:
                print(f"📊 Folding {unit} ({lesson_count} lessons) into {target_unit}")
                if target_unit not in final_unit_counts:
                    final_unit_counts[target_unit] = completed_units[target_unit]
                final_unit_counts[target_unit] += lesson_count
                folded_units.add(unit)
            else:
                final_unit_counts[unit] = lesson_count
        else:
            final_unit_counts[unit] = lesson_count
    
    if not final_unit_counts:
        print("⚠️ No completed units found for analysis")
        return None
    
    # Calculate average
    total_lessons = sum(final_unit_counts.values())
    num_units = len(final_unit_counts)
    average_lessons_per_unit = total_lessons / num_units
    
    # Step 5: Build unit analysis details
    unit_analysis = []
    for unit, lesson_count in final_unit_counts.items():
        # Find start date for this unit
        start_date = None
        for boundary in unit_boundaries:
            if boundary['unit'] == unit:
                start_date = boundary['start_datetime'][:10]
                break
        
        unit_analysis.append({
            'unit_name': unit,
            'lessons_count': lesson_count,
            'start_date': start_date or 'Unknown',
            'algorithm': 'first_mention_with_folding'
        })
    
    print(f"📊 Algorithm 1 unit analysis complete:")
    print(f"   Detected {len(unit_boundaries)} unit boundaries")
    print(f"   Analyzed {len(final_unit_counts)} completed units")
    for unit_data in unit_analysis:
        print(f"   - {unit_data['unit_name']}: {unit_data['lessons_count']} lessons (started {unit_data['start_date']})")
    print(f"   Average: {average_lessons_per_unit:.1f} lessons per unit")
    
    return {
        'average_lessons_per_unit': average_lessons_per_unit,
        'completed_units_analyzed': len(final_unit_counts),
        'unit_analysis': unit_analysis,
        'algorithm': 'first_mention_with_folding',
        'total_lessons_analyzed': total_lessons
    }

def calculate_unit_stats(sessions):
    """Calculate unit-specific lesson and practice statistics"""
    unit_stats = defaultdict(lambda: {
        'total_sessions': 0,
        'total_lessons': 0,
        'total_practice': 0,
        'total_combined_lessons': 0,  # New: core lessons + practice sessions
        'total_xp': 0,
        'first_seen': None,
        'last_seen': None,
        'session_types': Counter()
    })
    
    for session in sessions:
        unit = session.get('unit')
        if not unit:
            continue
            
        stats = unit_stats[unit]
        stats['total_sessions'] += 1
        stats['total_xp'] += session['xp']
        stats['session_types'][session['session_type']] += 1
        
        # Track date range
        session_date = session['datetime']
        if not stats['first_seen'] or session_date < stats['first_seen']:
            stats['first_seen'] = session_date
        if not stats['last_seen'] or session_date > stats['last_seen']:
            stats['last_seen'] = session_date
        
        if session['is_lesson'] or session['is_unit_completion']:
            stats['total_lessons'] += 1
            stats['total_combined_lessons'] += 1  # Count core lessons and completions
        elif session['session_type'] == 'personalized_practice':
            stats['total_practice'] += 1
            stats['total_combined_lessons'] += 1  # Count practice as lessons too
    
    # Calculate practice-to-lesson ratios
    for unit, stats in unit_stats.items():
        if stats['total_lessons'] > 0:
            stats['practice_to_lesson_ratio'] = stats['total_practice'] / stats['total_lessons']
        else:
            stats['practice_to_lesson_ratio'] = 0
    
    return dict(unit_stats)

def scrape_duome(username, use_automation=True, headless=True):
    """Main scraping function"""
    # Fetch data from duome.eu
    if use_automation:
        html_content = fetch_duome_data_with_update(username, headless)
        if not html_content:
            print("Browser automation failed, trying fallback method...")
            html_content = fetch_duome_data(username)
    else:
        html_content = fetch_duome_data(username)
        
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # =================================================================
    # CRITICAL DATA SOURCE WARNING:
    # =================================================================
    # ONLY the <div id="raw"> modal data is reliable from duome.eu
    # ALL other duome.eu displayed data is chronically inaccurate
    # The raw div contains the ONLY trusted session history data
    # =================================================================
    
    # --- Parse main stats for reference (UNRELIABLE - DO NOT USE) ---
    duome_reported_lessons = 0
    try:
        stats_text = soup.get_text()
        lessons_match = re.search(r"Lessons:\s*([\d,]+)", stats_text)
        if lessons_match:
            duome_reported_lessons = int(lessons_match.group(1).replace(',', ''))
            print(f"📊 Duome reports lessons completed: {duome_reported_lessons} (UNRELIABLE - for reference only)")
    except Exception as e:
        print(f"⚠️ Could not parse duome lessons count: {e}")

    # --- Parse session data from raw div (ONLY TRUSTED DATA SOURCE) ---
    raw_div = soup.find('div', {'id': 'raw'})
    if not raw_div:
        print("Error: Could not find raw data section in the page source")
        sessions, unit_transitions = [], {}
    else:
        sessions, unit_transitions = parse_session_data(str(raw_div))
    
    if not sessions:
        print("No session data found")
        # Do not fail if only session data is missing, we might still have stats
    
    print(f"Found {len(sessions)} recent sessions")
    
    # Calculate statistics
    daily_stats = calculate_daily_stats(sessions)
    unit_stats = calculate_unit_stats(sessions)
    
    # Calculate recent lessons per unit from unit review boundaries
    recent_unit_analysis = calculate_recent_lessons_per_unit(sessions)
    
    # Compute accurate totals from session data
    computed_lessons = sum(1 for s in sessions if s.get('is_lesson', False))
    computed_practice = sum(1 for s in sessions if not s.get('is_lesson', False))
    computed_total = computed_lessons + computed_practice
    print(f"📊 Computed from sessions: {computed_lessons} lessons + {computed_practice} practice = {computed_total} total")
    
    # Prepare output data
    output_data = {
        'username': username,
        'scraped_at': datetime.now().isoformat(),
        'duome_reported_lessons': duome_reported_lessons,  # Keep for reference but don't rely on this
        'computed_lesson_count': computed_lessons,
        'computed_practice_count': computed_practice,
        'computed_total_sessions': computed_total,
        'total_sessions': len(sessions),
        'sessions': sessions,
        'daily_stats': daily_stats,
        'unit_stats': unit_stats,
        'unit_transitions': {unit: dt.isoformat() for unit, dt in unit_transitions.items()},
        'recent_unit_analysis': recent_unit_analysis  # New: lessons per unit from unit boundaries
    }
    
    # Generate output filename in data directory
    import os
    import sys
    # Add config to path if running as standalone script
    if 'config' not in sys.modules:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from config import app_config as cfg
    
    data_dir = cfg.DATA_DIR
    os.makedirs(data_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(data_dir, f"duome_raw_{username}_{timestamp}.json")
    
    # Save to JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")
        return None
    
    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"Username: {username}")
    print(f"Total sessions: {len(sessions)}")
    if sessions:
        print(f"Date range: {sessions[-1]['date']} to {sessions[0]['date']}")
    else:
        print("Date range: No sessions found")
    
    # Daily summary
    print(f"\n=== DAILY LESSON COUNTS ===")
    for date, stats in list(daily_stats.items())[:7]:  # Show last 7 days
        print(f"{date}: {stats['total_lessons']} lessons, {stats['total_practice']} practice, {stats['total_xp']} XP")
    
    # Unit summary
    print(f"\n=== UNIT STATISTICS ===")
    for unit, stats in unit_stats.items():
        ratio = stats['practice_to_lesson_ratio']
        total_combined = stats['total_combined_lessons']
        print(f"{unit}: {stats['total_lessons']} core lessons, {stats['total_practice']} practice, {total_combined} total lessons (ratio: {ratio:.2f}:1)")
    
    return output_data

def main():
    """Command-line interface to run the scraper."""
    parser = argparse.ArgumentParser(description="Fetch and analyze Duolingo session data from duome.eu")
    parser.add_argument("--username", "-u", default="jonamar", help="Duolingo username to fetch data for")
    parser.add_argument("--no-automation", "-n", action="store_true", help="Skip browser automation and use direct request")
    parser.add_argument("--visible", "-v", action="store_true", dest="visible", default=False, help="Show browser UI for debugging")
    parser.add_argument("--headless", "-l", action="store_true", dest="headless_flag", help="Force headless mode (default behavior)")
    parser.add_argument("--output", "-o", help="Output file path (default: duome_raw_<username>_<timestamp>.json)")
    parser.add_argument("--validate-headless", action="store_true", help="Test headless scraping by running twice and checking timestamp changes")
    parser.add_argument("--wait-seconds", type=int, default=30, help="Seconds to wait between validation runs (default: 30)")
    
    args = parser.parse_args()
    
    # Special mode: Headless validation test
    if args.validate_headless:
        print("🔍 HEADLESS VALIDATION MODE")
        print("=" * 50)
        result = validate_headless_update_with_timestamps(args.username, args.wait_seconds)
        
        print("\n📋 VALIDATION RESULTS:")
        print(f"   Success: {result['success']}")
        print(f"   First timestamp: {result['first_timestamp']}")
        print(f"   Second timestamp: {result['second_timestamp']}")
        print(f"   Timestamp changed: {result['timestamp_changed']}")
        print(f"   Message: {result['message']}")
        
        if result['timestamp_changed']:
            print("\n🎉 CONCLUSION: Headless scraping appears to be working correctly!")
            return  # Exit successfully
        else:
            print("\n⚠️ CONCLUSION: Headless validation inconclusive - consider manual verification")
            return
        
    # Normal operation mode (default: headless unless --visible flag used)
    data = scrape_duome(args.username, use_automation=not args.no_automation, headless=not args.visible)
    
    if not data:
        print("❌ Failed to gather data")
        return
        
    # Generate default output filename if not specified
    if not args.output:
        import os
        import sys
        # Add config to path if running as standalone script
        if 'config' not in sys.modules:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from config import app_config as cfg
        
        data_dir = cfg.DATA_DIR
        os.makedirs(data_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = os.path.join(data_dir, f"duome_raw_{args.username}_{timestamp}.json")
    
    # Write data to JSON file
    with open(args.output, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Data saved to {args.output}")
    
    print("\nScraping completed successfully!")

if __name__ == "__main__":
    main()