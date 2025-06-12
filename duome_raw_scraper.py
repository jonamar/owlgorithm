#!/usr/bin/env python3
"""
Enhanced Duome Raw Data Scraper
Extracts and analyzes Duolingo session data from raw duome.eu HTML
Now includes daily lesson counts and unit-specific analysis
"""

import re
import json
from datetime import datetime
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import argparse

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
        
        # Check for lesson indicator
        if "· lesson" in text:
            is_lesson = True
            
        # Check for personalized practice
        if "personalized practice" in text:
            session_type = "personalized_practice"
        elif "story /practice" in text:
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
            'raw_text': text
        }
        
        sessions.append(session)
    
    # Sort sessions chronologically (oldest first for proper unit transition detection)
    sessions.sort(key=lambda x: x['datetime'])
    
    # Now assign units based on chronological transitions
    current_unit = None
    for session in sessions:
        if session['unit']:  # This session has a unit
            current_unit = session['unit']
        elif session['session_type'] == 'personalized_practice' and current_unit:
            # Assign personalized practice to current active unit
            session['unit'] = current_unit
    
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
        
        if session['is_lesson']:
            stats['total_lessons'] += 1
        elif session['session_type'] == 'personalized_practice':
            stats['total_practice'] += 1
    
    # Calculate practice-to-lesson ratios
    for unit, stats in unit_stats.items():
        if stats['total_lessons'] > 0:
            stats['practice_to_lesson_ratio'] = stats['total_practice'] / stats['total_lessons']
        else:
            stats['practice_to_lesson_ratio'] = 0
    
    return dict(unit_stats)

def scrape_duome_raw(html_file, username=None):
    """Main scraping function"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{html_file}' not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    # Extract username from filename if not provided
    if not username:
        username = html_file.split('.')[0].replace('duome_raw_', '')
    
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
        print(f"{unit}: {stats['total_lessons']} lessons, {stats['total_practice']} practice (ratio: {ratio:.2f}:1)")
    
    return output_data

def main():
    parser = argparse.ArgumentParser(description='Scrape and analyze Duome raw data')
    parser.add_argument('html_file', help='Path to the raw HTML file')
    parser.add_argument('--username', help='Username (auto-detected from filename if not provided)')
    
    args = parser.parse_args()
    
    result = scrape_duome_raw(args.html_file, args.username)
    if result:
        print("\nScraping completed successfully!")
    else:
        print("Scraping failed!")

if __name__ == "__main__":
    main() 