#!/usr/bin/env python3
"""Test script for new time-based notifications."""

import sys
import os
sys.path.append('src')

from notifiers.pushover_notifier import PushoverNotifier

def test_all_notifications():
    """Test all notification types."""
    notifier = PushoverNotifier()
    
    if not notifier.is_enabled():
        print("❌ Pushover not configured. Run scripts/setup_pushover.py first")
        return
    
    print("🧪 Testing all notification types...")
    
    # Test data
    daily_progress = {
        'completed': 3,
        'goal': 5,
        'remaining': 2,
        'progress_pct': 60.0,
        'status': 'close'
    }
    
    yesterday_progress = {
        'completed': 4,
        'goal': 5,
        'progress_pct': 80.0
    }
    
    trajectory_info = {
        'progress_pct': 45.2
    }
    
    # Test morning notification
    print("📧 Sending morning notification test...")
    notifier.send_morning_notification(
        daily_goal=5,
        current_streak=23,
        yesterday_progress=yesterday_progress
    )
    
    # Test midday notification
    print("📧 Sending midday notification test...")
    midday_progress = daily_progress.copy()
    midday_progress['completed'] = 2
    midday_progress['progress_pct'] = 40.0
    midday_progress['remaining'] = 3
    notifier.send_midday_notification(midday_progress)
    
    # Test evening notification (behind)
    print("📧 Sending evening notification test (behind)...")
    notifier.send_evening_notification(daily_progress)
    
    # Test evening notification (ahead)
    print("📧 Sending evening notification test (ahead)...")
    ahead_progress = daily_progress.copy()
    ahead_progress['completed'] = 6
    ahead_progress['progress_pct'] = 120.0
    ahead_progress['remaining'] = 0
    ahead_progress['status'] = 'ahead'
    notifier.send_evening_notification(ahead_progress)
    
    # Test night notification (success)
    print("📧 Sending night notification test (success)...")
    success_progress = daily_progress.copy()
    success_progress['completed'] = 5
    success_progress['progress_pct'] = 100.0
    success_progress['remaining'] = 0
    success_progress['status'] = 'on_track'
    notifier.send_night_notification(
        daily_progress=success_progress,
        units_completed=1,
        trajectory_info=trajectory_info
    )
    
    # Test night notification (missed goal)
    print("📧 Sending night notification test (missed goal)...")
    missed_progress = {
        'completed': 2,
        'goal': 5,
        'remaining': 3,
        'progress_pct': 40.0,
        'status': 'behind'
    }
    notifier.send_night_notification(
        daily_progress=missed_progress,
        units_completed=0,
        trajectory_info=trajectory_info
    )
    
    print("✅ All notification tests sent!")

if __name__ == "__main__":
    test_all_notifications() 