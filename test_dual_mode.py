#!/usr/bin/env python3
"""
Test script to verify the dual-mode tracking system works correctly.
"""

import sys
import os

# Setup project paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, 'src')))
sys.path.insert(0, os.path.abspath(current_dir))

from config import app_config as cfg
from src.core.metrics_calculator import get_tracked_unit_progress

def test_dual_mode_tracking():
    """Test the dual-mode tracking system with current data."""
    print("=== TESTING DUAL-MODE TRACKING SYSTEM ===\n")
    
    # Test with current state
    current_state = {
        'total_lessons_completed': 134,
        'daily_lessons_completed': 14,
        'daily_goal_lessons': 12,
    }
    
    print("Current configuration:")
    print(f"- Section 5 start lesson: {cfg.SECTION_5_START_LESSON}")
    print(f"- Legacy lessons (1-88): {cfg.LEGACY_LESSONS_COMPLETED}")
    print(f"- Legacy units completed: {cfg.LEGACY_COMPLETED_UNITS}")
    print(f"- Section 5+ lessons per unit: {cfg.NEW_LESSONS_PER_UNIT}")
    print(f"- Total course units: {cfg.TOTAL_COURSE_UNITS}")
    print()
    
    result = get_tracked_unit_progress(current_state)
    
    print("Dual-mode tracking results:")
    print(f"- Total lessons: {result['total_lessons']}")
    print(f"- Legacy units completed: {result['legacy_units_completed']}")
    print(f"- Legacy lessons completed: {result['legacy_lessons_completed']}")
    print(f"- Section 5+ units completed: {result['section5_units_completed']:.2f}")
    print(f"- Section 5+ lessons completed: {result['section5_lessons_completed']}")
    print(f"- Total units completed: {result['completed_units']:.2f}")
    print(f"- Remaining units: {result['remaining_units']:.2f}")
    print(f"- Lessons per unit (projection): {result['lessons_per_unit']}")
    print(f"- Tracking mode: {result['tracking_mode']}")
    print()
    
    # Verify calculations
    print("Verification:")
    expected_section5_lessons = 134 - 88  # Total - legacy
    expected_section5_units = expected_section5_lessons / 7
    expected_total_units = 3 + expected_section5_units
    
    print(f"- Expected Section 5+ lessons: {expected_section5_lessons}")
    print(f"- Expected Section 5+ units: {expected_section5_units:.2f}")
    print(f"- Expected total units: {expected_total_units:.2f}")
    
    # Check if calculations match
    calculations_correct = (
        result['section5_lessons_completed'] == expected_section5_lessons and
        abs(result['section5_units_completed'] - expected_section5_units) < 0.01 and
        abs(result['completed_units'] - expected_total_units) < 0.01
    )
    
    print(f"- Calculations correct: {'✅ YES' if calculations_correct else '❌ NO'}")
    
    if calculations_correct:
        print("\n🎉 Dual-mode tracking system working correctly!")
        print(f"You've completed {result['completed_units']:.1f} units total:")
        print(f"  - {result['legacy_units_completed']} units in Sections 1-4 (legacy tracking)")
        print(f"  - {result['section5_units_completed']:.1f} units in Section 5+ (simplified tracking)")
    else:
        print("\n❌ Calculation mismatch detected!")
    
    return result

def test_projection_accuracy():
    """Test that projections make sense with new structure."""
    print("\n=== TESTING PROJECTION ACCURACY ===\n")
    
    state = {'total_lessons_completed': 134}
    result = get_tracked_unit_progress(state)
    
    # Calculate remaining work manually
    sections_5_8_units = sum([cfg.SECTION_UNIT_COUNTS[i] for i in range(5, 9)])
    section5_completed = result['section5_units_completed']
    section5_remaining = cfg.SECTION_UNIT_COUNTS[5] - section5_completed
    sections_6_8_total = sum([cfg.SECTION_UNIT_COUNTS[i] for i in range(6, 9)])
    total_remaining_units = section5_remaining + sections_6_8_total
    total_remaining_lessons = total_remaining_units * 7
    
    print("Remaining work calculation:")
    print(f"- Section 5 units remaining: {section5_remaining:.2f}")
    print(f"- Sections 6-8 units total: {sections_6_8_total}")
    print(f"- Total remaining units: {total_remaining_units:.2f}")
    print(f"- Total remaining lessons: {total_remaining_lessons:.0f}")
    print(f"- System calculated remaining: {result['total_lessons_remaining']:.0f}")
    
    match = abs(result['total_lessons_remaining'] - total_remaining_lessons) < 1
    print(f"- Remaining work calculation: {'✅ CORRECT' if match else '❌ INCORRECT'}")
    
    return match

if __name__ == "__main__":
    try:
        tracking_test = test_dual_mode_tracking()
        projection_test = test_projection_accuracy()
        
        if tracking_test and projection_test:
            print(f"\n🎉 ALL TESTS PASSED! Dual-mode system is ready.")
        else:
            print(f"\n❌ Some tests failed. Please review the implementation.")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
