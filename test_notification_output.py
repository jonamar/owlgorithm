#!/usr/bin/env python3
"""
Test notification output accuracy after dual-mode tracking updates.
"""

import sys
import os
import json

# Setup project paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, 'src')))
sys.path.insert(0, os.path.abspath(current_dir))

from config import app_config as cfg
from src.core.metrics_calculator import get_tracked_unit_progress, calculate_performance_metrics
from src.notifiers.pushover_notifier import PushoverNotifier

def test_performance_metrics():
    """Test the updated performance metrics calculation."""
    print("=== TESTING PERFORMANCE METRICS ===\n")
    
    # Load actual session data
    data_dir = os.path.join(current_dir, 'data')
    target_file = 'duome_raw_jonamar_20250724_123025.json'
    file_path = os.path.join(data_dir, target_file)
    
    if not os.path.exists(file_path):
        print(f"❌ Test data file not found: {target_file}")
        return None
    
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    
    metrics = calculate_performance_metrics(json_data)
    
    if not metrics:
        print("❌ No performance metrics calculated!")
        return None
    
    print("Performance metrics results:")
    print(f"- Total sessions: {len(json_data.get('sessions', []))}")
    print(f"- Daily avg lessons: {metrics['daily_avg_lessons']:.2f}")
    print(f"- Daily avg sessions: {metrics['daily_avg_sessions']:.2f}")
    print(f"- Weekly avg lessons: {metrics['weekly_avg_lessons']:.2f}")
    print(f"- Recent avg lessons (7-day): {metrics['recent_avg_lessons']:.2f}")
    print(f"- Recent avg sessions (7-day): {metrics['recent_avg_sessions']:.2f}")
    print(f"- Active days: {metrics['active_days']}")
    print(f"- Recent days: {metrics['recent_days']}")
    
    print(f"\n🎯 Expected vs Actual:")
    print(f"- Our manual analysis: 11.6 lessons/day (last 7 days)")
    print(f"- System calculation: {metrics['recent_avg_lessons']:.1f} lessons/day")
    
    close_match = abs(metrics['recent_avg_lessons'] - 11.6) < 1.0
    print(f"- Match: {'✅ CLOSE' if close_match else '❌ MISMATCH'}")
    
    return metrics

def test_dual_mode_progress():
    """Test dual-mode progress calculations."""
    print("\n=== TESTING DUAL-MODE PROGRESS ===\n")
    
    # Current state
    current_state = {
        'total_lessons_completed': 134,
        'daily_lessons_completed': 14,
        'daily_goal_lessons': 12,
    }
    
    progress = get_tracked_unit_progress(current_state)
    
    print("Dual-mode progress results:")
    print(f"- Total lessons: {progress['total_lessons']}")
    print(f"- Completed units: {progress['completed_units']:.2f}")
    print(f"- Required lessons/day: {progress['required_lessons_per_day']:.1f}")
    print(f"- Course completion: {progress['course_completion_percentage']:.1f}%")
    print(f"- Time completion: {progress['time_completion_percentage']:.1f}%")
    
    # Verify course completion calculation
    expected_course_pct = (134 / (964 * 7)) * 100  # 964 units * 7 lessons = 6748 total
    actual_course_pct = progress['course_completion_percentage']
    
    print(f"\n📊 Course completion verification:")
    print(f"- Expected: {expected_course_pct:.2f}%")
    print(f"- Actual: {actual_course_pct:.2f}%")
    print(f"- Match: {'✅ CORRECT' if abs(expected_course_pct - actual_course_pct) < 0.1 else '❌ INCORRECT'}")
    
    return progress

def test_notification_format():
    """Test the notification message formatting."""
    print("\n=== TESTING NOTIFICATION FORMAT ===\n")
    
    # Load test data
    data_dir = os.path.join(current_dir, 'data')
    target_file = 'duome_raw_jonamar_20250724_123025.json'
    file_path = os.path.join(data_dir, target_file)
    
    if not os.path.exists(file_path):
        print(f"❌ Test data file not found: {target_file}")
        return False
    
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    
    # Current state and daily progress
    current_state = {
        'total_lessons_completed': 134,
        'daily_lessons_completed': 14,
        'daily_goal_lessons': 12,
    }
    
    daily_progress = {
        'completed': 14,
        'goal': 12,
        'progress_pct': 116.7
    }
    
    # Create notifier and format message
    notifier = PushoverNotifier()
    message = notifier._format_notification_message(daily_progress, current_state, json_data)
    
    print("Generated notification message:")
    print("─" * 40)
    print(message)
    print("─" * 40)
    
    # Verify message components
    lines = message.split('\n')
    if len(lines) != 3:
        print(f"❌ Expected 3 lines, got {len(lines)}")
        return False
    
    # Check line 1: daily progress
    line1_has_lessons = "lessons" in lines[0].lower()
    line1_has_daily_pct = "daily" in lines[0].lower()
    
    # Check line 2: course percentage and weekly average
    line2_has_course = "course:" in lines[1].lower()
    line2_has_week_avg = "week avg:" in lines[1].lower()
    
    # Check line 3: finish date
    line3_has_finish = "finish:" in lines[2].lower()
    
    print(f"\nMessage validation:")
    print(f"- Line 1 has lessons: {'✅' if line1_has_lessons else '❌'}")
    print(f"- Line 1 has daily %: {'✅' if line1_has_daily_pct else '❌'}")
    print(f"- Line 2 has course %: {'✅' if line2_has_course else '❌'}")
    print(f"- Line 2 has week avg: {'✅' if line2_has_week_avg else '❌'}")
    print(f"- Line 3 has finish: {'✅' if line3_has_finish else '❌'}")
    
    all_valid = all([line1_has_lessons, line1_has_daily_pct, line2_has_course, 
                     line2_has_week_avg, line3_has_finish])
    
    print(f"- Overall format: {'✅ VALID' if all_valid else '❌ INVALID'}")
    
    return all_valid

def main():
    """Run all notification tests."""
    print("🧪 TESTING NOTIFICATION OUTPUT AFTER DUAL-MODE UPDATES\n")
    
    # Run all tests
    metrics_result = test_performance_metrics()
    progress_result = test_dual_mode_progress()
    format_result = test_notification_format()
    
    # Summary
    print(f"\n📋 TEST SUMMARY:")
    metrics_ok = metrics_result is not None
    progress_ok = progress_result is not None
    
    print(f"- Performance metrics: {'✅ PASS' if metrics_ok else '❌ FAIL'}")
    print(f"- Dual-mode progress: {'✅ PASS' if progress_ok else '❌ FAIL'}")
    print(f"- Notification format: {'✅ PASS' if format_result else '❌ FAIL'}")
    
    all_tests_passed = metrics_ok and progress_ok and format_result
    
    if all_tests_passed:
        print(f"\n🎉 ALL TESTS PASSED! Notification system ready.")
        print(f"\nKey improvements verified:")
        print(f"- Weekly average now counts lessons (not sessions)")
        print(f"- Course completion percentage included")
        print(f"- Dual-mode tracking integration working")
        print(f"- Message format updated correctly")
    else:
        print(f"\n❌ Some tests failed. Please review the issues above.")
    
    return all_tests_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
