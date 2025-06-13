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
    url = f"https://duome.eu/{username}"
    print(f"Opening browser and navigating to {url}...")
    
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
        
        # Navigate to the page
        driver.get(url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Look for the update button
        print("Looking for update button...")
        try:
            # Try different possible selectors for the update button
            update_selectors = [
                "//*[contains(text(), 'click here') and contains(text(), 'update')]",
                "//*[contains(text(), 'Please, click here')]",
                "//a[contains(@href, 'update')]",
                "//button[contains(text(), 'update')]",
                "//*[@class='update-button']",
                "//*[@id='update-button']",
            ]
            
            update_button = None
            for selector in update_selectors:
                try:
                    update_button = driver.find_element(By.XPATH, selector)
                    if update_button and update_button.is_displayed():
                        print(f"Found update button with XPath: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if update_button:
                print("Clicking update button...")
                # Scroll to button first
                driver.execute_script("arguments[0].scrollIntoView(true);", update_button)
                time.sleep(1)
                
                # Try clicking with JavaScript (more reliable)
                driver.execute_script("arguments[0].click();", update_button)
                
                # Wait for update to complete
                print("Waiting for stats to update...")
                time.sleep(8)  # Give it more time to update
                
                # Check if page has updated (look for newer timestamps)
                print("Checking if update completed...")
                
            else:
                print("Update button not found, proceeding with current data...")
                print("The page might already have the latest data.")
                
        except Exception as e:
            print(f"Could not click update button: {e}")
            print("Proceeding with current data...")
        
        # Get the page source after potential update
        print("Extracting page data...")
        page_source = driver.page_source
        
        # Parse with BeautifulSoup to find raw data
        soup = BeautifulSoup(page_source, 'html.parser')
        raw_div = soup.find('div', {'id': 'raw'})
        
        if not raw_div:
            print("Error: Could not find raw data section")
            return None
            
        return str(raw_div)
        
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
        response = requests.get(url)
        response.raise_for_status()
        
        # Find the raw data section
        soup = BeautifulSoup(response.content, 'html.parser')
        raw_div = soup.find('div', {'id': 'raw'})
        
        if not raw_div:
            print("Error: Could not find raw data section")
            return None
            
        return str(raw_div)
        
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
    
    print(f"Parsing session data for {username}...")
    sessions, unit_transitions = parse_session_data(html_content)
    
    if not sessions:
        print("No session data found")
        return None
    
    print(f"Found {len(sessions)} sessions")
    
    # Calculate statistics
    daily_stats = calculate_daily_stats(sessions)
    unit_stats = calculate_unit_stats(sessions)
    
    # Prepare output data
    output_data = {
        'username': username,
        'scraped_at': datetime.now().isoformat(),
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
    parser = argparse.ArgumentParser(description='Scrape and analyze Duome raw data with auto-update')
    parser.add_argument('--username', default='jonamar', help='Duolingo username to scrape')
    parser.add_argument('--no-automation', action='store_true', help='Skip browser automation (faster but no auto-update)')
    parser.add_argument('--show-browser', action='store_true', help='Show browser window during automation (for debugging)')
    
    args = parser.parse_args()
    
    use_automation = not args.no_automation
    headless = not args.show_browser
    
    result = scrape_duome(args.username, use_automation, headless)
    if result:
        print("\nScraping completed successfully!")
    else:
        print("Scraping failed!")

if __name__ == "__main__":
    main() 