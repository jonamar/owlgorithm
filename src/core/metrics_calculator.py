#!/usr/bin/env python3
"""
Metrics Calculator
Handles all performance metrics, goal calculations, and progress tracking.
Extracted from daily_tracker.py for better organization and testability.
"""

from collections import defaultdict
from datetime import datetime
from config import app_config as cfg


def count_todays_lessons(json_data, target_date):
    """Count all sessions (lessons + practice) completed on a specific date."""
    count = 0
    for session in json_data.get('sessions', []):
        session_date = session.get('date', '')
        if session_date == target_date:
            count += 1
    return count


def calculate_daily_lesson_goal(state_data, recent_scrape_data=None):
    """
    Return hardcoded daily goal - no dynamic calculation.
    
    URGENT FIX: This function previously had complex calculation logic that mixed
    historical and tracking data, causing notifications to show "1 lesson/day".
    Now returns hardcoded 12 lessons/day to fix the notification bug immediately.
    
    Args:
        state_data (dict): Current state (unused, for compatibility)
        recent_scrape_data (dict): Recent scrape data (unused, for compatibility)
        
    Returns:
        int: Hardcoded daily lesson goal (12)
    """
    return cfg.DAILY_GOAL_LESSONS


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


def calculate_completion_projection(state_data):
    """
    Calculate course completion projections based on actual performance.
    
    Returns estimated completion date and whether user is on track for 18-month goal.
    """
    from datetime import datetime, timedelta
    
    # Get current progress data
    # Use total_completed_units if available, otherwise fall back to processed_units count  
    total_completed_units = state_data.get('total_completed_units', len(state_data.get('processed_units', [])))
    total_lessons_completed = state_data.get('total_lessons_completed', 0)
    remaining_units = cfg.TOTAL_COURSE_UNITS - total_completed_units
    
    # Calculate dynamic lessons per unit
    if total_completed_units > 0:
        actual_lessons_per_unit = total_lessons_completed / total_completed_units
        total_lessons_remaining = remaining_units * actual_lessons_per_unit
    else:
        actual_lessons_per_unit = cfg.BASE_LESSONS_PER_UNIT
        total_lessons_remaining = remaining_units * actual_lessons_per_unit
    
    # Calculate total course lessons estimate
    total_estimated_lessons = cfg.TOTAL_COURSE_UNITS * actual_lessons_per_unit
    
    # Calculate current daily average (would need start date for accurate calculation)
    # For now, use simplified calculation
    current_daily_average = total_lessons_completed / max(1, cfg.GOAL_DAYS * 0.1)  # Rough approximation
    
    # Project completion based on current pace
    if current_daily_average > 0:
        days_to_completion = total_lessons_remaining / current_daily_average
        projected_completion_date = datetime.now() + timedelta(days=days_to_completion)
    else:
        days_to_completion = float('inf')
        projected_completion_date = None
    
    # Calculate 18-month target date
    target_completion_date = datetime.now() + timedelta(days=cfg.GOAL_DAYS)
    
    # Determine if on track
    if projected_completion_date and projected_completion_date <= target_completion_date:
        schedule_status = "ahead" if projected_completion_date < target_completion_date else "on_track"
    else:
        schedule_status = "behind"
    
    return {
        'total_estimated_lessons': total_estimated_lessons,
        'lessons_remaining': total_lessons_remaining,
        'actual_lessons_per_unit': actual_lessons_per_unit,
        'current_daily_average': current_daily_average,
        'projected_completion_date': projected_completion_date.isoformat() if projected_completion_date else None,
        'target_completion_date': target_completion_date.isoformat(),
        'days_to_completion': days_to_completion if days_to_completion != float('inf') else None,
        'schedule_status': schedule_status,
        'completion_percentage': (total_lessons_completed / total_estimated_lessons * 100) if total_estimated_lessons > 0 else 0
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


def get_tracked_unit_progress(state_data, json_data=None):
    """
    Single source of truth for tracked unit progress calculations.
    
    Returns progress based on 3 tracked complete units only, used by both
    notifications and markdown updates for consistency.
    
    Args:
        state_data (dict): Current tracker state data
        json_data (dict): Optional session data for unit analysis
        
    Returns:
        dict: Standardized progress data for all components
    """
    from datetime import datetime, timedelta
    
    # Core tracking data (clean, no historical confusion)
    completed_units = len(cfg.TRACKED_COMPLETE_UNITS)
    total_lessons = state_data.get('total_lessons_completed', 0)
    remaining_units = cfg.TOTAL_COURSE_UNITS - cfg.ACTUALLY_COMPLETED_TOTAL  # Total actually completed (historical + tracked)
    
    # Calculate lessons per unit - use course average for consistency
    # Note: Tracked average (total_lessons/completed_units) may be skewed by 
    # excessive practice in early units, so we use the established course average
    tracked_lessons_per_unit = total_lessons / completed_units if completed_units > 0 else cfg.BASE_LESSONS_PER_UNIT
    lessons_per_unit = cfg.BASE_LESSONS_PER_UNIT  # Use course average (31) for projections
    
    # 18-month goal timeline tracking
    goal_start_date = datetime.strptime(cfg.TRACKING_START_DATE, "%Y-%m-%d")
    goal_end_date = goal_start_date + timedelta(days=cfg.GOAL_DAYS)  # 18 months
    today = datetime.now()
    days_elapsed = (today - goal_start_date).days
    days_remaining = (goal_end_date - today).days
    completion_percentage = (days_elapsed / cfg.GOAL_DAYS) * 100 if days_elapsed > 0 else 0
    
    # Burn rate analysis
    total_lessons_remaining = remaining_units * lessons_per_unit
    
    # Historical pace (actual performance since tracking started)
    if days_elapsed > 0:
        actual_units_per_day = completed_units / days_elapsed
        actual_lessons_per_day = total_lessons / days_elapsed
    else:
        actual_units_per_day = 0
        actual_lessons_per_day = 0
    
    # Required pace (to meet 18-month goal)
    if days_remaining > 0:
        required_units_per_day = remaining_units / days_remaining
        required_lessons_per_day = total_lessons_remaining / days_remaining
    else:
        required_units_per_day = 0
        required_lessons_per_day = 0
    
    # Pace comparison
    pace_difference = actual_lessons_per_day - required_lessons_per_day
    if pace_difference >= 0:
        pace_status = "ON TRACK" if abs(pace_difference) < 0.5 else "AHEAD"
        pace_status_display = f"✅ {pace_status}" + (f" by {pace_difference:.1f} lessons/day" if pace_difference >= 0.5 else "")
    else:
        pace_status = "BEHIND"
        pace_status_display = f"⚠️ BEHIND by {abs(pace_difference):.1f} lessons/day"
    
    # Projected completion
    if actual_lessons_per_day > 0:
        projected_days_total = total_lessons_remaining / actual_lessons_per_day
        projected_completion_date = today + timedelta(days=projected_days_total)
        projected_months = projected_days_total / 30.44  # avg days per month
        months_difference = projected_months - 18
    else:
        projected_completion_date = None
        projected_months = float('inf')
        months_difference = float('inf')
    
    return {
        'completed_units': completed_units,
        'total_lessons': total_lessons,
        'lessons_per_unit': lessons_per_unit,
        'remaining_units': remaining_units,
        'total_lessons_remaining': total_lessons_remaining,
        'required_lessons_per_day': required_lessons_per_day,
        'current_daily_avg': actual_lessons_per_day,
        'pace_difference': pace_difference,
        'pace_status': pace_status_display,
        'daily_goal': cfg.DAILY_GOAL_LESSONS,
        
        # 18-month goal tracking
        'goal_start_date': goal_start_date.strftime('%Y-%m-%d'),
        'goal_end_date': goal_end_date.strftime('%Y-%m-%d'),
        'days_elapsed': days_elapsed,
        'days_remaining': days_remaining,
        'completion_percentage': completion_percentage,
        'actual_units_per_day': actual_units_per_day,
        'actual_lessons_per_day': actual_lessons_per_day,
        'required_units_per_day': required_units_per_day,
        'projected_completion_date': projected_completion_date.strftime('%Y-%m-%d') if projected_completion_date else None,
        'projected_months': projected_months if projected_months != float('inf') else None,
        'months_difference': months_difference if months_difference != float('inf') else None
    }