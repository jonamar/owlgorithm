#!/usr/bin/env python3
"""
Quick check of daily lesson requirement from goal start date.
"""

import sys
import os

# Setup project paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, 'src')))
sys.path.insert(0, os.path.abspath(current_dir))

from config import app_config as cfg
from src.core.metrics_calculator import get_tracked_unit_progress

def check_daily_requirement():
    """Get the daily lesson requirement from goal start date."""
    print("=== DAILY LESSON REQUIREMENT (18-MONTH GOAL) ===\n")
    
    # Current state
    current_state = {
        'total_lessons_completed': 134,
        'daily_lessons_completed': 14,
        'daily_goal_lessons': 12,
    }
    
    result = get_tracked_unit_progress(current_state)
    
    print(f"🎯 **ANSWER: {result['required_lessons_per_day']:.1f} lessons per day**")
    print()
    print("Goal tracking details:")
    print(f"- Goal start date: {result['goal_start_date']}")
    print(f"- Goal end date: {result['goal_end_date']}")
    print(f"- Days elapsed: {result['days_elapsed']}")
    print(f"- Days remaining: {result['days_remaining']}")
    print(f"- Total lessons completed: {result['total_lessons']}")
    print(f"- Total lessons remaining: {result['total_lessons_remaining']:.0f}")
    print()
    print("Current vs required pace:")
    print(f"- Your current daily average: {result['current_daily_avg']:.1f} lessons/day")
    print(f"- Required daily average: {result['required_lessons_per_day']:.1f} lessons/day")
    print(f"- Pace difference: {result['pace_difference']:+.1f} lessons/day")
    print(f"- Status: {result['pace_status']}")
    print()
    print("Projected completion:")
    if result['projected_completion_date']:
        print(f"- At current pace: {result['projected_completion_date']}")
        if result['projected_months']:
            print(f"- That's {result['projected_months']:.1f} months from start")
        if result['months_difference']:
            print(f"- Difference from 18-month goal: {result['months_difference']:+.1f} months")
    
    return result

if __name__ == "__main__":
    check_daily_requirement()
