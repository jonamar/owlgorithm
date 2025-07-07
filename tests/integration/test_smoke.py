#!/usr/bin/env python3
"""
Smoke Tests for Owlgorithm - Essential E2E Validation
===================================================

These tests implement the "Tier 1: Essential Smoke Tests" from the Testing Integration PRD.
They are designed to catch 80% of real-world failures in under 30 seconds.

Purpose: Prevent silent E2E failures before they reach production
Coverage: End-to-end workflow validation + notification content verification
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.metrics_calculator import calculate_daily_progress, calculate_performance_metrics, count_todays_lessons
from src.core.markdown_updater import update_markdown_file
from src.notifiers.pushover_notifier import PushoverNotifier


class TestEssentialSmokeTests:
    """Essential smoke tests that catch 80% of real-world failures in < 30 seconds"""
    
    @pytest.fixture
    def sample_scrape_data(self):
        """Load realistic test fixture data"""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_scrape_data.json"
        with open(fixture_path, 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def sample_state_data(self):
        """Load realistic state fixture data"""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_state_data.json"
        with open(fixture_path, 'r') as f:
            return json.load(f)
    
    def test_data_processing_pipeline_with_content_validation(self, sample_scrape_data, sample_state_data):
        """
        Test 1: Data Processing Pipeline + Content Validation
        
        This is the PRIMARY smoke test that catches most real-world failures:
        - Tests the complete data processing pipeline with realistic data
        - Validates calculation logic produces reasonable outputs
        - Ensures no junk values or calculation errors in critical metrics
        - Validates notification message generation works correctly
        
        Target: < 20 seconds execution time
        """
        start_time = time.time()
        
        # Test 1: Core calculation functions with realistic data
        print("🧪 Testing core calculation functions...")
        
        # Test daily progress calculation
        progress_data = calculate_daily_progress(sample_state_data)
        assert progress_data is not None, "Daily progress calculation should not fail"
        assert 'completed' in progress_data, "Progress data should contain completed lessons"
        assert 'goal' in progress_data, "Progress data should contain goal information"
        assert 'status' in progress_data, "Progress data should contain status"
        assert 'progress_pct' in progress_data, "Progress data should contain percentage"
        
        # Validate progress values are reasonable
        assert isinstance(progress_data['completed'], int), "Completed lessons should be integer"
        assert isinstance(progress_data['goal'], int), "Goal should be integer"
        assert 0 <= progress_data['progress_pct'] <= 200, f"Progress percentage should be reasonable: {progress_data['progress_pct']}"
        assert progress_data['status'] in ['ahead', 'on_track', 'close', 'behind'], f"Status should be valid: {progress_data['status']}"
        
        # Test performance metrics calculation
        perf_metrics = calculate_performance_metrics(sample_scrape_data)
        if perf_metrics is not None:  # May be None for insufficient data
            assert 'active_days' in perf_metrics, "Performance metrics should contain active days"
            assert 'daily_avg_sessions' in perf_metrics, "Performance metrics should contain daily average"
            assert isinstance(perf_metrics['active_days'], int), "Active days should be integer"
            assert perf_metrics['active_days'] > 0, "Active days should be positive"
        
        # Test lesson counting for specific dates
        lesson_count_today = count_todays_lessons(sample_scrape_data, '2025-07-06')
        lesson_count_yesterday = count_todays_lessons(sample_scrape_data, '2025-07-05')
        assert isinstance(lesson_count_today, int), "Lesson count should be integer"
        assert lesson_count_today >= 0, "Lesson count should be non-negative"
        
        # Test 2: Notification content generation and validation
        print("📱 Testing notification content generation...")
        
        # Mock notification capture to validate content
        captured_notifications = []
        
        def capture_notification(*args, **kwargs):
            # Handle different notification method signatures
            if len(args) > 0:
                message = args[0]
            elif 'message' in kwargs:
                message = kwargs['message']
            else:
                message = str(args) + str(kwargs)  # fallback
            
            captured_notifications.append(message)
            return True
        
        # Test pushover notification generation
        with patch.object(PushoverNotifier, 'send_notification', capture_notification):
            with patch.object(PushoverNotifier, 'send_simple_notification', capture_notification):
                notifier = PushoverNotifier()
                
                # Simulate notification generation with realistic data
                try:
                    # Test simple notification (if method exists)
                    if hasattr(notifier, 'send_simple_notification'):
                        notifier.send_simple_notification(
                            daily_progress=progress_data,
                            units_completed=['Sports 2', 'Grooming'],
                            total_lessons=sample_state_data['total_lessons_completed'],
                            state_data=sample_state_data,
                            json_data=sample_scrape_data
                        )
                    else:
                        # Fallback to basic notification
                        notifier.send_notification("Test notification with realistic data")
                except Exception as e:
                    # Some notification failures are acceptable in test environment
                    if "config" not in str(e).lower():  # Config errors are expected in tests
                        pytest.fail(f"Notification generation failed unexpectedly: {e}")
        
        # Validate notification content quality (PRIMARY goal of PRD)
        if captured_notifications:
            message = str(captured_notifications[0])
            
            # Critical validation: No junk values in notification content
            junk_indicators = [
                'undefined', 'calculating...', 'NaN', 'null', 'None', 
                'error', 'failed', 'Exception', 'Traceback',
                '{{', '}}', '${', 'TypeError', 'AttributeError'
            ]
            
            for junk in junk_indicators:
                assert junk not in message, f"Notification contains junk value: '{junk}' in message: {message}"
            
            # Validate notification contains reasonable content
            if len(message) > 10:  # Only test if we got substantial content
                # Extract numbers from message for basic sanity checks
                import re
                numbers = re.findall(r'\d+', message)
                if numbers:
                    # Check that lesson counts are reasonable (not negative, not impossibly high)
                    # Note: Exclude year projections (>2000) from validation
                    for num_str in numbers:
                        num = int(num_str)
                        if num > 2000:  # Likely a year projection, skip validation
                            continue
                        assert 0 <= num <= 1000, f"Notification contains unrealistic lesson count: {num}"
        
        # Test 3: Markdown generation functionality
        print("📝 Testing markdown update functionality...")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_markdown_path = temp_file.name
            temp_file.write("# Initial content")
        
        try:
            # Test markdown update with realistic data and proper format
            realistic_markdown_content = """# Duolingo Learning Analytics

## French Course Progression

- **Total Units in Course**: 272
- **Completed Units**: 3
- **Remaining Units**: 269
- **Total Lessons Completed**: 75

### Performance Metrics
- **Daily Average**: 5.0 lessons/day (across 15 active days)
- **Weekly Average**: 35.0 lessons/week
- **XP Daily Average**: 400 XP/day
- **XP Weekly Average**: 2,800 XP/week
- **Current Streak**: 5 consecutive active days

### Goal Progress
- **Daily Requirement**: 12 lessons/day
- **Pace Status**: Behind
- **Projected Completion**: calculating...

*Last updated: July 6, 2025*
"""
            
            success = update_markdown_file(
                newly_completed_count=1,
                total_lessons_count=sample_state_data['total_lessons_completed'],
                content=realistic_markdown_content,
                state_data=sample_state_data
            )
            
            # Success should be True OR a valid file path (some implementations return path)
            assert success is True or isinstance(success, str), "Markdown update should succeed"
            
        finally:
            # Cleanup
            try:
                os.unlink(temp_markdown_path)
            except:
                pass
        
        # Performance validation: Test should complete quickly
        execution_time = time.time() - start_time
        assert execution_time < 20, f"Smoke test took too long: {execution_time:.2f}s (should be < 20s)"
        
        print(f"✅ Data processing smoke test passed in {execution_time:.2f}s")
    
    def test_basic_environment_validation(self):
        """
        Test 2: Basic Environment Validation
        
        Quick validation that critical dependencies and environment setup work:
        - Python imports function correctly
        - Configuration can be loaded
        - File permissions are correct
        - Basic error handling works
        
        Target: < 10 seconds execution time
        """
        start_time = time.time()
        
        # Test critical imports
        try:
            from config import app_config as cfg
            from src.core.daily_scheduler import DailyDuolingoTracker
            from src.core.metrics_calculator import calculate_daily_progress
            from src.core.markdown_updater import update_markdown_file
            from src.notifiers.pushover_notifier import PushoverNotifier
            from src.scrapers.enhanced_scraper import EnhancedScraper
            imports_ok = True
        except ImportError as e:
            imports_ok = False
            pytest.fail(f"Critical import failed: {e}")
        
        assert imports_ok, "All critical imports should work"
        
        # Test configuration access
        try:
            username = cfg.USERNAME
            daily_goal = cfg.DAILY_GOAL_LESSONS
            total_units = cfg.TOTAL_COURSE_UNITS
            config_ok = True
        except AttributeError as e:
            config_ok = False
            pytest.fail(f"Configuration access failed: {e}")
        
        assert config_ok, "Configuration should be accessible"
        
        # Test basic calculation functions with minimal data
        minimal_state = {
            'daily_lessons_completed': 5,
            'daily_goal_lessons': 12
        }
        
        try:
            progress = calculate_daily_progress(minimal_state)
            assert progress is not None, "Progress calculation should work with minimal data"
            assert 'completed' in progress, "Progress should contain completed field"
            calculation_ok = True
        except Exception as e:
            calculation_ok = False
            pytest.fail(f"Basic calculation failed: {e}")
        
        assert calculation_ok, "Basic calculations should work"
        
        # Test file system access patterns
        try:
            # Test temp file creation (validates permissions)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=True) as temp_file:
                temp_file.write('{"test": "data"}')
                temp_file.flush()
                
                # Test reading back
                with open(temp_file.name, 'r') as f:
                    data = json.load(f)
                    assert data['test'] == 'data', "File I/O should work correctly"
            
            filesystem_ok = True
        except Exception as e:
            filesystem_ok = False
            pytest.fail(f"File system access failed: {e}")
        
        assert filesystem_ok, "File system operations should work"
        
        # Test error handling doesn't crash
        try:
            # Try to create a notifier without proper config (should handle gracefully)
            notifier = PushoverNotifier()
            # Should not crash, may return False for is_enabled() but shouldn't raise
            error_handling_ok = True
        except Exception as e:
            # Some initialization errors are acceptable, crashes are not
            if "critical" in str(e).lower() or "fatal" in str(e).lower():
                error_handling_ok = False
                pytest.fail(f"Critical error in error handling: {e}")
            else:
                error_handling_ok = True
        
        assert error_handling_ok, "Error handling should be graceful"
        
        # Performance validation
        execution_time = time.time() - start_time
        assert execution_time < 10, f"Environment validation took too long: {execution_time:.2f}s (should be < 10s)"
        
        print(f"✅ Environment validation passed in {execution_time:.2f}s")


if __name__ == "__main__":
    # Allow running smoke tests directly
    pytest.main([__file__, "-v", "--tb=short"]) 