#!/usr/bin/env python3
"""
Aggregate daily lesson counts from all JSON files to get real totals.

This script processes all duome JSON files and builds a complete picture
of daily lesson activity by combining data from the rolling windows.
"""

import json
import glob
import os
from collections import defaultdict
from datetime import datetime, timedelta
import sys

def parse_filename_date(filename):
    """Extract date from filename like duome_raw_jonamar_20250612_212357.json"""
    try:
        basename = os.path.basename(filename)
        date_part = basename.split('_')[3]  # 20250612
        return datetime.strptime(date_part, '%Y%m%d').date()
    except:
        return None

def aggregate_daily_lessons(data_dir):
    """
    Aggregate daily lesson counts from all JSON files.
    
    Strategy:
    1. Process files chronologically 
    2. For each date, use the count from the earliest file that contains it
    3. This gives us the most accurate count before the rolling window drops older data
    """
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(data_dir, 'duome_raw_jonamar_*.json'))
    
    # Sort by filename (chronological)
    json_files.sort()
    
    # Track daily counts and which file first reported each date
    daily_counts = {}
    date_sources = {}
    
    print(f"Processing {len(json_files)} JSON files...")
    
    for file_path in json_files:
        file_date = parse_filename_date(file_path)
        if not file_date:
            continue
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Skip empty files (338 bytes = error files)
            if len(data.get('sessions', [])) == 0:
                continue
                
            # Count lessons by date in this file
            file_daily_counts = defaultdict(int)
            for session in data['sessions']:
                session_date = session['date']
                file_daily_counts[session_date] += 1
            
            # For each date in this file, use it if we haven't seen it before
            # or if this file is older (more likely to have complete data)
            for session_date, count in file_daily_counts.items():
                if session_date not in daily_counts:
                    daily_counts[session_date] = count
                    date_sources[session_date] = file_path
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    return daily_counts, date_sources

def calculate_statistics(daily_counts, start_date_str='2025-06-23'):
    """Calculate statistics from the daily counts"""
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    today = datetime.now().date()
    
    # Filter to dates from start_date onwards
    relevant_counts = {
        date: count for date, count in daily_counts.items() 
        if datetime.strptime(date, '%Y-%m-%d').date() >= start_date
    }
    
    if not relevant_counts:
        return None
        
    total_lessons = sum(relevant_counts.values())
    days_elapsed = (today - start_date).days + 1
    days_with_lessons = len(relevant_counts)
    
    # Calculate averages
    daily_avg_all_days = total_lessons / days_elapsed
    daily_avg_active_days = total_lessons / days_with_lessons if days_with_lessons > 0 else 0
    
    return {
        'total_lessons': total_lessons,
        'days_elapsed': days_elapsed,
        'days_with_lessons': days_with_lessons,
        'days_without_lessons': days_elapsed - days_with_lessons,
        'daily_avg_all_days': daily_avg_all_days,
        'daily_avg_active_days': daily_avg_active_days,
        'start_date': start_date_str,
        'end_date': today.strftime('%Y-%m-%d')
    }

def main():
    data_dir = '/Users/jonamar/Development/owlgorithm/data'
    
    print("Aggregating daily lesson counts from JSON files...")
    daily_counts, date_sources = aggregate_daily_lessons(data_dir)
    
    if not daily_counts:
        print("No lesson data found!")
        return
    
    # Sort dates for display
    sorted_dates = sorted(daily_counts.keys())
    
    print(f"\nFound lesson data for {len(sorted_dates)} days")
    print(f"Date range: {sorted_dates[0]} to {sorted_dates[-1]}")
    
    # Show recent activity
    print(f"\nRecent daily activity (last 10 days):")
    for date in sorted_dates[-10:]:
        count = daily_counts[date]
        source_file = os.path.basename(date_sources[date])
        print(f"  {date}: {count:2d} lessons (from {source_file})")
    
    # Calculate statistics
    stats = calculate_statistics(daily_counts)
    if stats:
        print(f"\n=== STATISTICS (from {stats['start_date']} onwards) ===")
        print(f"Total lessons: {stats['total_lessons']}")
        print(f"Days elapsed: {stats['days_elapsed']}")
        print(f"Days with lessons: {stats['days_with_lessons']}")
        print(f"Days without lessons: {stats['days_without_lessons']}")
        print(f"Daily average (all days): {stats['daily_avg_all_days']:.3f} lessons/day")
        print(f"Daily average (active days): {stats['daily_avg_active_days']:.3f} lessons/day")
        
        # Compare with broken state file
        print(f"\n=== COMPARISON ===")
        print(f"Real total: {stats['total_lessons']} lessons")
        print(f"State file shows: 55 lessons")
        print(f"Difference: {stats['total_lessons'] - 55} lessons missing from state")

if __name__ == '__main__':
    main()
