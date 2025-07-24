#!/usr/bin/env python3
"""
Analyze lesson pace over the last 14 days (last 7 days + previous 7 days).
"""

import sys
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

# Setup project paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, 'src')))
sys.path.insert(0, os.path.abspath(current_dir))

def analyze_recent_pace():
    """Analyze daily lesson counts for the last 14 days."""
    print("=== RECENT PACE ANALYSIS (LAST 14 DAYS) ===\n")
    
    # Use the file with actual session data
    data_dir = os.path.join(current_dir, 'data')
    target_file = 'duome_raw_jonamar_20250724_123025.json'  # File with 134 sessions
    file_path = os.path.join(data_dir, target_file)
    
    if not os.path.exists(file_path):
        print(f"❌ Target data file not found: {target_file}")
        return
    
    print(f"📊 Analyzing data from: {target_file}")
    
    # Load the data
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    sessions = data.get('sessions', [])
    if not sessions:
        print("❌ No session data found in this file!")
        return
    
    # Get today's date and calculate date ranges
    today = datetime.now().date()
    last_7_start = today - timedelta(days=6)  # Include today
    previous_7_start = today - timedelta(days=13)
    previous_7_end = today - timedelta(days=7)
    
    print(f"📅 Date ranges:")
    print(f"   Last 7 days: {last_7_start} to {today}")
    print(f"   Previous 7 days: {previous_7_start} to {previous_7_end}")
    print()
    
    # Count lessons by date
    daily_counts = defaultdict(int)
    total_sessions = len(sessions)
    
    for session in sessions:
        session_date = datetime.fromisoformat(session['datetime']).date()
        
        # Count sessions marked as lessons
        if session.get('is_lesson', False):
            daily_counts[session_date] += 1
    
    print(f"📈 Daily lesson counts (from {total_sessions} total sessions):")
    print()
    
    # Last 7 days analysis
    last_7_total = 0
    print("🔥 LAST 7 DAYS:")
    for i in range(7):
        date = today - timedelta(days=6-i)
        count = daily_counts[date]
        last_7_total += count
        day_name = date.strftime('%a')
        date_str = date.strftime('%m/%d')
        print(f"   {day_name} {date_str}: {count:2d} lessons")
    
    print(f"   ➤ Total: {last_7_total} lessons")
    print(f"   ➤ Average: {last_7_total/7:.1f} lessons/day")
    print()
    
    # Previous 7 days analysis
    previous_7_total = 0
    print("📊 PREVIOUS 7 DAYS:")
    for i in range(7):
        date = previous_7_start + timedelta(days=i)
        count = daily_counts[date]
        previous_7_total += count
        day_name = date.strftime('%a')
        date_str = date.strftime('%m/%d')
        print(f"   {day_name} {date_str}: {count:2d} lessons")
    
    print(f"   ➤ Total: {previous_7_total} lessons")
    print(f"   ➤ Average: {previous_7_total/7:.1f} lessons/day")
    print()
    
    # Overall 14-day analysis
    total_14_days = last_7_total + previous_7_total
    print("📋 14-DAY SUMMARY:")
    print(f"   Total lessons: {total_14_days}")
    print(f"   Average per day: {total_14_days/14:.1f} lessons/day")
    print()
    
    # Compare to goal requirement
    required_daily = 11.6  # From previous calculation
    recent_pace = last_7_total / 7
    
    print("🎯 GOAL COMPARISON:")
    print(f"   Required for 18-month goal: {required_daily:.1f} lessons/day")
    print(f"   Your recent pace (last 7): {recent_pace:.1f} lessons/day")
    difference = recent_pace - required_daily
    if difference >= 0:
        print(f"   Status: ✅ AHEAD by {difference:.1f} lessons/day!")
    else:
        print(f"   Status: ⚠️ BEHIND by {abs(difference):.1f} lessons/day")
    
    return {
        'last_7_total': last_7_total,
        'last_7_avg': recent_pace,
        'previous_7_total': previous_7_total,
        'previous_7_avg': previous_7_total/7,
        'total_14_days': total_14_days,
        'avg_14_days': total_14_days/14
    }

if __name__ == "__main__":
    analyze_recent_pace()
