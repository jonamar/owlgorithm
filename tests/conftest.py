"""
Pytest configuration and fixtures for Owlgorithm tests
"""

import pytest
import os
import sys
import json
from datetime import datetime

# Add src to path for importing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        'sessions': [
            {
                'datetime': '2025-06-28T10:30:00',
                'date': '2025-06-28',
                'time': '10:30:00',
                'xp': 15,
                'session_type': 'unit_lesson',
                'unit': 'Requests',
                'is_lesson': True,
                'is_unit_completion': False,
                'raw_text': 'sample lesson'
            },
            {
                'datetime': '2025-06-28T11:00:00',
                'date': '2025-06-28',
                'time': '11:00:00',
                'xp': 10,
                'session_type': 'personalized_practice',
                'unit': 'Requests',
                'is_lesson': False,
                'is_unit_completion': False,
                'raw_text': 'sample practice'
            },
            {
                'datetime': '2025-06-27T15:30:00',
                'date': '2025-06-27',
                'time': '15:30:00',
                'xp': 20,
                'session_type': 'unit_completion',
                'unit': 'Grooming',
                'is_lesson': True,
                'is_unit_completion': True,
                'raw_text': 'unit completion'
            }
        ],
        'unit_stats': {
            'Grooming': {
                'total_combined_lessons': 25,
                'total_lessons': 12,
                'total_practice': 13,
                'session_types': {'unit_completion': 1, 'unit_lesson': 12, 'personalized_practice': 13}
            },
            'Requests': {
                'total_combined_lessons': 15,
                'total_lessons': 8,
                'total_practice': 7,
                'session_types': {'unit_lesson': 8, 'personalized_practice': 7}
            }
        },
        'computed_total_sessions': 3,
        'computed_lesson_count': 2,
        'computed_practice_count': 1
    }


@pytest.fixture
def sample_state_data():
    """Sample state data for testing"""
    return {
        'processed_units': ['Nightmare', 'Grooming'],
        'total_completed_units': 86,
        'total_lessons_completed': 163,
        'computed_total_sessions': 163,
        'computed_lesson_count': 49,
        'computed_practice_count': 114,
        'daily_lessons_completed': 9,
        'daily_goal_lessons': 15,
        'last_daily_reset': '2025-06-28',
        'last_scrape_date': '2025-06-28'
    }


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing"""
    return """# Duolingo Learning Analytics

## French Course Progression

- **Total Units in Course**: 272
- **Completed Units**: 86
- **Remaining Units**: 186
- **Total Lessons Completed**: 163

### Performance Metrics
- **Daily Average**: 10.9 lessons/day (across 15 active days)
- **Weekly Average**: 76.1 lessons/week
- **XP Daily Average**: 590 XP/day
- **XP Weekly Average**: 4,129 XP/week
- **Current Streak**: 15 consecutive active days
- **Recent Performance** (last 7 days): 12.6 lessons/day, 762 XP/day

### Goal Progress
- **Daily Requirement**: 8.8 lessons/day (based on 3 completed units, 26.0 avg lessons/unit)
- **Pace Status**: ✅ AHEAD by 2.0 lessons/day
- **Projected Completion**: 14.6 months (3.4 months early)
- **Total Lessons Needed**: 4,836 lessons (186 remaining units)

*Last updated: June 28, 2025*
"""