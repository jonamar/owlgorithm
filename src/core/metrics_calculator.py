#!/usr/bin/env python3
"""
Metrics Calculator
Handles all performance metrics, goal calculations, and progress tracking.
Extracted from daily_tracker.py for better organization and testability.
"""

from collections import defaultdict
from datetime import datetime
from config import app_config as cfg

# Import configuration constants
TOTAL_UNITS_IN_COURSE = cfg.TOTAL_UNITS_IN_COURSE
GOAL_DAYS = cfg.GOAL_DAYS  # 18 months
BASE_LESSONS_PER_UNIT = cfg.BASE_LESSONS_PER_UNIT


def count_todays_lessons(json_data, target_date):
    """Count all sessions (lessons + practice) completed on a specific date."""
    count = 0
    for session in json_data.get('sessions', []):
        session_date = session.get('date', '')
        if session_date == target_date:
            count += 1
    return count


def calculate_daily_lesson_goal(state_data):
    """Calculate how many lessons should be completed per day."""
    # Get current progress
    total_completed_units = len(state_data.get('processed_units', []))
    remaining_units = TOTAL_UNITS_IN_COURSE - total_completed_units
    total_lessons_remaining = remaining_units * BASE_LESSONS_PER_UNIT
    
    # Calculate daily goal
    lessons_per_day = total_lessons_remaining / GOAL_DAYS
    return max(1, round(lessons_per_day))  # At least 1 lesson per day


def calculate_daily_progress(state_data):
    """Calculate daily progress statistics."""
    daily_completed = state_data.get('daily_lessons_completed', 0)
    daily_goal = state_data.get('daily_goal_lessons', 1)
    
    progress_pct = (daily_completed / daily_goal) * 100 if daily_goal > 0 else 0
    lessons_remaining = max(0, daily_goal - daily_completed)
    
    # Determine status
    if daily_completed >= daily_goal:
        status = 'ahead' if daily_completed > daily_goal else 'on_track'
    elif daily_completed >= daily_goal * 0.8:
        status = 'close'
    else:
        status = 'behind'
    
    return {
        'completed': daily_completed,
        'goal': daily_goal,
        'remaining': lessons_remaining,
        'progress_pct': progress_pct,
        'status': status
    }


def calculate_unit_completion_metrics(json_data, total_completed_units):
    """Calculate lessons per unit based on completed units data."""
    unit_stats = json_data.get('unit_stats', {})
    
    # Find completed units (those with unit_completion sessions)
    completed_units_data = []
    for unit_name, stats in unit_stats.items():
        session_types = stats.get('session_types', {})
        completions = session_types.get('unit_completion', 0)
        
        if completions > 0:
            total_lessons = stats.get('total_combined_lessons', 0)
            core_lessons = stats.get('total_lessons', 0)
            practice_sessions = stats.get('total_practice', 0)
            
            completed_units_data.append({
                'name': unit_name,
                'total_lessons': total_lessons,
                'core_lessons': core_lessons,
                'practice_sessions': practice_sessions
            })
    
    if not completed_units_data:
        return None
        
    # Calculate average lessons per unit
    total_lessons_sum = sum(unit['total_lessons'] for unit in completed_units_data)
    avg_lessons_per_unit = total_lessons_sum / len(completed_units_data)
    
    # Calculate daily requirement
    remaining_units = TOTAL_UNITS_IN_COURSE - total_completed_units
    total_lessons_needed = remaining_units * avg_lessons_per_unit
    daily_requirement = total_lessons_needed / GOAL_DAYS
    
    return {
        'completed_units_tracked': len(completed_units_data),
        'avg_lessons_per_unit': avg_lessons_per_unit,
        'remaining_units': remaining_units,
        'total_lessons_needed': total_lessons_needed,
        'daily_requirement': daily_requirement,
        'completed_units_data': completed_units_data
    }


def calculate_performance_metrics(json_data):
    """Calculate daily/weekly averages and performance metrics from session data."""
    daily_stats = defaultdict(lambda: {'sessions': 0, 'xp': 0})
    total_sessions = 0
    total_xp = 0
    
    for session in json_data.get('sessions', []):
        date = session.get('date', 'unknown')
        xp = session.get('xp', 0)
        
        if date != 'unknown':
            daily_stats[date]['sessions'] += 1
            daily_stats[date]['xp'] += xp
            total_sessions += 1
            total_xp += xp
    
    # Get date range
    dates = sorted([d for d in daily_stats.keys()])
    if not dates:
        return None
    
    active_days = len(dates)
    daily_avg_sessions = total_sessions / active_days if active_days > 0 else 0
    daily_avg_xp = total_xp / active_days if active_days > 0 else 0
    
    # Weekly averages
    weekly_avg_sessions = daily_avg_sessions * 7
    weekly_avg_xp = daily_avg_xp * 7
    
    # Recent 7-day performance
    recent_dates = dates[-7:] if len(dates) >= 7 else dates
    recent_sessions = sum(daily_stats[d]['sessions'] for d in recent_dates)
    recent_xp = sum(daily_stats[d]['xp'] for d in recent_dates)
    recent_days = len(recent_dates)
    
    recent_avg_sessions = recent_sessions / recent_days if recent_days > 0 else 0
    recent_avg_xp = recent_xp / recent_days if recent_days > 0 else 0
    
    # Calculate streak
    consecutive_days = 0
    for date in reversed(dates):
        if daily_stats[date]['sessions'] > 0:
            consecutive_days += 1
        else:
            break
    
    return {
        'daily_avg_sessions': daily_avg_sessions,
        'weekly_avg_sessions': weekly_avg_sessions,
        'daily_avg_xp': daily_avg_xp,
        'weekly_avg_xp': weekly_avg_xp,
        'active_days': active_days,
        'consecutive_days': consecutive_days,
        'recent_avg_sessions': recent_avg_sessions,
        'recent_avg_xp': recent_avg_xp,
        'recent_days': recent_days
    }