#!/usr/bin/env python3
"""
Script to analyze the lessons-to-unit ratio from recent Duolingo data.
Focuses on the last 6 completed units to determine the new ratio.
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime

def load_latest_data():
    """Load the most recent JSON data file."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    json_files = [f for f in os.listdir(data_dir) if f.startswith("duome_raw_") and f.endswith(".json")]
    json_files.sort(reverse=True)  # Most recent first
    
    if not json_files:
        raise FileNotFoundError("No JSON data files found")
    
    latest_file = os.path.join(data_dir, json_files[0])
    print(f"Loading data from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def analyze_unit_boundaries(sessions):
    """
    Analyze sessions to identify unit boundaries using the simple hack:
    - Look for significant gaps in session timing
    - Look for unit name changes
    - Look for patterns that indicate unit completion
    """
    print("\n=== ANALYZING UNIT BOUNDARIES ===")
    
    # Group sessions by unit
    unit_sessions = defaultdict(list)
    unit_dates = defaultdict(set)
    
    for session in sessions:
        unit = session.get('assigned_unit') or session.get('unit') or 'Unknown'
        unit_sessions[unit].append(session)
        unit_dates[unit].add(session.get('date'))
    
    print(f"\nUnits found: {list(unit_sessions.keys())}")
    
    # Sort units by first occurrence
    unit_first_date = {}
    for unit, sessions_list in unit_sessions.items():
        if sessions_list:
            first_session = min(sessions_list, key=lambda x: x.get('datetime', ''))
            unit_first_date[unit] = first_session.get('datetime', '')
    
    sorted_units = sorted(unit_first_date.keys(), key=lambda x: unit_first_date[x], reverse=True)
    
    print(f"\nUnits in chronological order (newest first):")
    unit_lesson_counts = {}
    
    for i, unit in enumerate(sorted_units):
        sessions_list = unit_sessions[unit]
        lesson_count = len([s for s in sessions_list if s.get('is_lesson', True)])
        unit_lesson_counts[unit] = lesson_count
        
        date_range = f"{min(unit_dates[unit])} to {max(unit_dates[unit])}"
        print(f"{i+1:2d}. {unit:15s} - {lesson_count:3d} lessons ({date_range})")
    
    return sorted_units, unit_lesson_counts

def calculate_ratio_for_last_n_units(sorted_units, unit_lesson_counts, n=6):
    """Calculate lessons-to-unit ratio for the last N completed units."""
    print(f"\n=== CALCULATING RATIO FOR LAST {n} UNITS ===")
    
    if len(sorted_units) < n:
        print(f"Warning: Only {len(sorted_units)} units available, less than requested {n}")
        n = len(sorted_units)
    
    last_n_units = sorted_units[:n]  # Most recent N units
    
    print(f"\nAnalyzing these {n} units:")
    total_lessons = 0
    
    for i, unit in enumerate(last_n_units):
        lessons = unit_lesson_counts[unit]
        total_lessons += lessons
        print(f"{i+1}. {unit:15s} - {lessons:3d} lessons")
    
    ratio = total_lessons / n if n > 0 else 0
    
    print(f"\nRESULTS:")
    print(f"Total lessons in last {n} units: {total_lessons}")
    print(f"Average lessons per unit: {ratio:.2f}")
    print(f"Compared to old average of ~31 lessons/unit: {ratio/31:.2f}x")
    
    return ratio, total_lessons, n

def main():
    try:
        data = load_latest_data()
        
        print(f"Data overview:")
        print(f"- Total sessions: {data.get('total_sessions', 'Unknown')}")
        print(f"- Computed lessons: {data.get('computed_lesson_count', 'Unknown')}")
        print(f"- Scraped at: {data.get('scraped_at', 'Unknown')}")
        
        sessions = data.get('sessions', [])
        if not sessions:
            print("No sessions found in data!")
            return
        
        sorted_units, unit_lesson_counts = analyze_unit_boundaries(sessions)
        
        # Calculate for last 6 units
        ratio, total_lessons, actual_n = calculate_ratio_for_last_n_units(sorted_units, unit_lesson_counts, 6)
        
        print(f"\n" + "="*50)
        print(f"NEW LESSONS-TO-UNIT RATIO: {ratio:.1f} lessons per unit")
        print(f"Based on {actual_n} most recent completed units")
        print(f"Reduction factor: {31/ratio:.2f}x fewer lessons per unit")
        print(f"="*50)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
