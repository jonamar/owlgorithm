#!/usr/bin/env python3
"""
Enhanced Duome Raw Data Scraper with Auto-Update
Fetches and analyzes Duolingo session data directly from duome.eu
Automatically clicks the "update your stats" button before scraping
Now includes daily lesson counts and unit-specific analysis
"""

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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def fetch_duome_data_with_update(username, headless=True):
    """Fetch raw data from duome.eu with automatic stats update"""
    # Use direct URL with update parameter for more reliable updates
    url = f"https://duome.eu/{username}"
    update_url = f"https://duome.eu/{username}?update=true"
    print(f"Opening browser and navigating to {update_url} (with auto-update)...")
    
    driver = None
    try:
        # Try different browsers in order of preference
        browsers_to_try = [
            ('chrome', lambda: setup_chrome_driver(headless)),
            ('firefox', lambda: setup_firefox_driver(headless)),
            ('safari', lambda: setup_safari_driver()),
        ]
        
        driver = None
        browser_name = None
        
        for name, setup_func in browsers_to_try:
            try:
                print(f"Trying {name.title()} browser...")
                driver = setup_func()
                browser_name = name
                print(f"Successfully initialized {name.title()} browser")
                break
            except Exception as e:
                print(f"{name.title()} browser failed: {e}")
                continue
        
        if not driver:
            print("No suitable browser found. Please install Chrome, Firefox, or enable Safari WebDriver.")
            print("For Chrome: Download from https://www.google.com/chrome/")
            print("For Safari: Run 'sudo safaridriver --enable' in terminal")
            return None
        
        # Navigate to the page with update parameter
        driver.get(update_url)
        print("Navigated to page with update parameter - stats should be refreshed automatically")
        
        # Wait for page to load and update to complete
        print("Waiting for page to load and stats to update...")
        WebDriverWait(driver, 15).until(
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
            
        # Try to find and click the specific update button even if we used ?update=true
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
            print("Proceeding with current data loaded from ?update=true URL")
            
        # Give additional time for the update to complete
        print("Allowing time for stats update to complete...")
        time.sleep(12)  # Increased wait time for update to process
        
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
        print(f"Error during browser automation: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()

def setup_chrome_driver(headless=True):
    """Setup Chrome WebDriver"""
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def setup_firefox_driver(headless=True):
    """Setup Firefox WebDriver"""
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from webdriver_manager.firefox import GeckoDriverManager
    
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("--headless")
    
    service = Service(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=firefox_options)

def setup_safari_driver():
    """Setup Safari WebDriver (macOS only)"""
    from selenium.webdriver.safari.service import Service
    
    # Safari doesn't support headless mode
    service = Service()
    return webdriver.Safari(service=service)

def fetch_duome_data(username):
    """Fallback method: Fetch raw data from duome.eu without automation"""
    url = f"https://duome.eu/{username}"
    print(f"Fetching data from {url} (fallback method)...")
    
    try:
        # Add headers to mimic a browser request (sometimes needed to avoid blocks)  
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)  # Add timeout
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
        
        # Determine session type and unit
        session_type = "unknown"
        unit = None
        is_lesson = False
        is_unit_completion = False  # New: track unit completion lessons
        
        # Check for lesson indicator
        if "· lesson" in text:
            is_lesson = True
            
        # Check for unit completion indicators (unit review, legendary)
        if any(keyword in text.lower() for keyword in ["unit review", "legendary", "legendary / unit review"]):
            is_unit_completion = True
            session_type = "unit_completion"
            
        # Check for personalized practice
        elif "personalized practice" in text:
            session_type = "personalized_practice"
        elif "story /practice" in text or "story / practice" in text:
            session_type = "story"
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
        
        if session['is_lesson']:
            daily_stats[date]['total_lessons'] += 1
        elif session['session_type'] == 'personalized_practice':
            daily_stats[date]['total_practice'] += 1
    
    # Convert to regular dict and sort by date
    return dict(sorted(daily_stats.items(), reverse=True))

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
    
    # --- New: Parse main stats for total lesson count ---
    total_lessons_completed = 0
    try:
        stats_text = soup.get_text()
        lessons_match = re.search(r"Lessons:\s*([\d,]+)", stats_text)
        if lessons_match:
            total_lessons_completed = int(lessons_match.group(1).replace(',', ''))
            print(f"📊 Found total lessons completed: {total_lessons_completed}")
    except Exception as e:
        print(f"⚠️ Could not parse total lessons count: {e}")

    # --- Parse session data from raw div ---
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
    
    # Prepare output data
    output_data = {
        'username': username,
        'scraped_at': datetime.now().isoformat(),
        'total_lessons_completed': total_lessons_completed,
        'total_sessions': len(sessions),
        'sessions': sessions,
        'daily_stats': daily_stats,
        'unit_stats': unit_stats,
        'unit_transitions': {unit: dt.isoformat() for unit, dt in unit_transitions.items()}
    }
    
    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"duome_raw_{username}_{timestamp}.json"
    
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
    print(f"Date range: {sessions[-1]['date']} to {sessions[0]['date']}")
    
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
    parser.add_argument("--headless", "-l", action="store_false", dest="visible", help="Run browser in headless mode (no UI)")
    parser.add_argument("--visible", "-v", action="store_true", dest="visible", default=False, help="Show browser UI for debugging")
    parser.add_argument("--output", "-o", help="Output file path (default: duome_raw_<username>_<timestamp>.json)")
    parser.add_argument("--debug-click", "-d", action="store_true", help="Debug mode: just attempt update click and show browser")
    
    args = parser.parse_args()
    
    # Special debug mode just for diagnosing update click issue
    if args.debug_click:
        print("🔍 Running in debug mode - browser will be visible")
        print("👀 Observe what happens when clicking the update button")
        # Force visible browser in debug mode
        page_source = fetch_duome_data_with_update(args.username, headless=False)
        if page_source:
            print("✅ Page loaded successfully")
            print("🔎 Checking for direct URL parameters that might force a refresh...")
            
            # Try direct update URL - some sites have parameters that force refresh
            try:
                direct_url = f"https://duome.eu/{args.username}?update=true"
                print(f"Trying direct URL: {direct_url}")
                response = requests.get(direct_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml'
                })
                
                if response.status_code == 200:
                    print("✅ Direct URL request successful!")
                    
                    # Check if timestamp changed
                    import re
                    timestamp_match = re.search(r"Last update: ([\d\-:\s]+GMT[\+\-]\d)", response.text)
                    if timestamp_match:
                        print(f"⏰ Timestamp from direct URL: {timestamp_match.group(1)}")
                    else:
                        print("⚠️ Could not find timestamp in response")
                else:
                    print(f"❌ Direct URL request failed: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error trying direct URL: {e}")
        
        return
        
    # Normal operation mode
    data = scrape_duome(args.username, use_automation=not args.no_automation, headless=not args.visible)
    
    if not data:
        print("❌ Failed to gather data")
        return
        
    # Generate default output filename if not specified
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"duome_raw_{args.username}_{timestamp}.json"
    
    # Write data to JSON file
    with open(args.output, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Data saved to {args.output}")
    
    print("\nScraping completed successfully!")

if __name__ == "__main__":
    main()