"""
Unit tests for notification throttling logic in daily_tracker.py
Tests the 2.5-hour throttling behavior when no data changes occur.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.core.daily_tracker import send_time_based_notification


class TestNotificationThrottling:
    """Test notification throttling logic"""
    
    def test_notification_sent_with_data_changes(self):
        """Test notification is sent when data changes are detected"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data without last notification timestamp
        state_data = {}
        
        # Call with data changes
        result = send_time_based_notification(
            notifier, 'morning', state_data, 
            has_new_lessons=True, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Should send notification
        assert result is True
        assert notifier.send_simple_notification.called
        assert 'last_notification_timestamp' in state_data
    
    def test_notification_sent_with_unit_changes(self):
        """Test notification is sent when units are completed"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data without last notification timestamp
        state_data = {}
        
        # Call with unit changes
        result = send_time_based_notification(
            notifier, 'evening', state_data, 
            has_new_lessons=False, has_new_units=True, 
            units_completed=3, json_data={}
        )
        
        # Should send notification
        assert result is True
        assert notifier.send_simple_notification.called
        assert 'last_notification_timestamp' in state_data
    
    def test_notification_sent_no_changes_no_previous_notification(self):
        """Test notification is sent when no changes but no previous notification"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data without last notification timestamp
        state_data = {}
        
        # Call without data changes
        result = send_time_based_notification(
            notifier, 'midday', state_data, 
            has_new_lessons=False, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Should send notification (no previous timestamp)
        assert result is True
        assert notifier.send_simple_notification.called
        assert 'last_notification_timestamp' in state_data
    
    def test_notification_throttled_within_25_hours(self):
        """Test notification is throttled when within 2.5 hours and no changes"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data with recent notification timestamp (1 hour ago)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        state_data = {
            'last_notification_timestamp': one_hour_ago.isoformat()
        }
        
        # Call without data changes
        result = send_time_based_notification(
            notifier, 'afternoon', state_data, 
            has_new_lessons=False, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Should NOT send notification (throttled)
        assert result is False
        assert not notifier.send_simple_notification.called
        # Timestamp should not be updated
        assert state_data['last_notification_timestamp'] == one_hour_ago.isoformat()
    
    def test_notification_sent_after_25_hours(self):
        """Test notification is sent after 2.5 hours even without changes"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data with old notification timestamp (3 hours ago)
        three_hours_ago = datetime.now() - timedelta(hours=3)
        state_data = {
            'last_notification_timestamp': three_hours_ago.isoformat()
        }
        
        # Call without data changes
        result = send_time_based_notification(
            notifier, 'evening', state_data, 
            has_new_lessons=False, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Should send notification (throttle period passed)
        assert result is True
        assert notifier.send_simple_notification.called
        # Timestamp should be updated
        assert state_data['last_notification_timestamp'] != three_hours_ago.isoformat()
    
    def test_notification_sent_with_changes_despite_recent_timestamp(self):
        """Test notification is sent with changes even if recent timestamp exists"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data with very recent notification timestamp (10 minutes ago)
        ten_minutes_ago = datetime.now() - timedelta(minutes=10)
        state_data = {
            'last_notification_timestamp': ten_minutes_ago.isoformat()
        }
        
        # Call WITH data changes
        result = send_time_based_notification(
            notifier, 'morning', state_data, 
            has_new_lessons=True, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Should send notification (data changes override throttling)
        assert result is True
        assert notifier.send_simple_notification.called
        # Timestamp should be updated
        assert state_data['last_notification_timestamp'] != ten_minutes_ago.isoformat()
    
    def test_notification_timestamp_updated_correctly(self):
        """Test that notification timestamp is updated to current time"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data
        state_data = {}
        
        # Call with data changes
        result = send_time_based_notification(
            notifier, 'midday', state_data, 
            has_new_lessons=True, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Check that notification was sent and timestamp was set
        assert result is True
        assert 'last_notification_timestamp' in state_data
        
        # Check timestamp format (ISO 8601 format)
        timestamp = state_data['last_notification_timestamp']
        assert len(timestamp) > 19  # Should be ISO format like '2025-07-15T14:30:00.123456'
        assert 'T' in timestamp  # Should contain 'T' separator
        assert '-' in timestamp  # Should contain date separators
        
        # Check that timestamp is recent (within last few seconds)
        from datetime import datetime
        parsed_timestamp = datetime.fromisoformat(timestamp)
        time_diff = datetime.now() - parsed_timestamp
        assert time_diff.total_seconds() < 5  # Should be very recent
    
    def test_throttle_duration_exactly_25_hours(self):
        """Test behavior exactly at 2.5 hour boundary"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data with notification timestamp exactly 2.5 hours ago
        exactly_25_hours_ago = datetime.now() - timedelta(hours=2.5)
        state_data = {
            'last_notification_timestamp': exactly_25_hours_ago.isoformat()
        }
        
        # Call without data changes
        result = send_time_based_notification(
            notifier, 'evening', state_data, 
            has_new_lessons=False, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Should send notification (boundary condition - time passed)
        assert result is True
        assert notifier.send_simple_notification.called
    
    @patch('src.core.daily_tracker.calculate_daily_progress')
    def test_notification_content_passed_correctly(self, mock_calculate_progress):
        """Test that notification function receives correct parameters"""
        # Mock dependencies
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        mock_calculate_progress.return_value = {
            'completed': 8, 'goal': 12, 'remaining': 4
        }
        
        # State data
        state_data = {'computed_total_sessions': 150}
        json_data = {'test': 'data'}
        
        # Call with data changes
        result = send_time_based_notification(
            notifier, 'morning', state_data, 
            has_new_lessons=True, has_new_units=False, 
            units_completed=3, json_data=json_data
        )
        
        # Check function was called with correct parameters
        assert result is True
        mock_calculate_progress.assert_called_once_with(state_data)
        notifier.send_simple_notification.assert_called_once_with(
            daily_progress={'completed': 8, 'goal': 12, 'remaining': 4},
            units_completed=3,
            total_lessons=150,
            state_data=state_data,
            json_data=json_data
        )
    
    def test_notification_with_corrupted_timestamp(self):
        """Test notification handling when timestamp is corrupted/malformed"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data with corrupted timestamp
        state_data = {
            'last_notification_timestamp': 'not-a-valid-timestamp'
        }
        
        # Call without data changes
        result = send_time_based_notification(
            notifier, 'midday', state_data, 
            has_new_lessons=False, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Should send notification (corrupted timestamp treated as no previous notification)
        assert result is True
        assert notifier.send_simple_notification.called
        # Timestamp should be updated with valid timestamp
        assert 'last_notification_timestamp' in state_data
        new_timestamp = state_data['last_notification_timestamp']
        assert new_timestamp != 'not-a-valid-timestamp'
        assert 'T' in new_timestamp  # Should be valid ISO format
    
    def test_notification_with_empty_timestamp(self):
        """Test notification handling when timestamp is empty string"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data with empty timestamp
        state_data = {
            'last_notification_timestamp': ''
        }
        
        # Call without data changes
        result = send_time_based_notification(
            notifier, 'evening', state_data, 
            has_new_lessons=False, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Should send notification (empty timestamp treated as no previous notification)
        assert result is True
        assert notifier.send_simple_notification.called
    
    def test_notification_with_very_old_timestamp(self):
        """Test notification handling with very old timestamp (years ago)"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # State data with very old timestamp (2 years ago)
        two_years_ago = datetime.now() - timedelta(days=730)
        state_data = {
            'last_notification_timestamp': two_years_ago.isoformat()
        }
        
        # Call without data changes
        result = send_time_based_notification(
            notifier, 'morning', state_data, 
            has_new_lessons=False, has_new_units=False, 
            units_completed=2, json_data={}
        )
        
        # Should send notification (very old timestamp means throttle period has passed)
        assert result is True
        assert notifier.send_simple_notification.called
        # Timestamp should be updated
        assert state_data['last_notification_timestamp'] != two_years_ago.isoformat()
    
    def test_notification_with_none_state_data(self):
        """Test notification handling when state_data is None or missing keys"""
        # Mock notifier
        notifier = Mock()
        notifier.send_simple_notification = Mock()
        
        # None state data
        state_data = None
        
        # Call without data changes - should handle gracefully
        with patch('src.core.daily_tracker.calculate_daily_progress') as mock_calc:
            mock_calc.return_value = {'completed': 0, 'goal': 12, 'remaining': 12}
            
            result = send_time_based_notification(
                notifier, 'midday', state_data, 
                has_new_lessons=False, has_new_units=False, 
                units_completed=0, json_data={}
            )
        
        # Should handle gracefully and send notification (no previous timestamp)
        assert result is True
        assert notifier.send_simple_notification.called 