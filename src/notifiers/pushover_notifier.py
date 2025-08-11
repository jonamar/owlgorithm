#!/usr/bin/env python3
"""
Pushover Notification Module
Handles sending push notifications via Pushover API for Duolingo progress updates.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add project root and src to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SRC_DIR)

from config import app_config as cfg
# Import will be done locally to avoid circular imports
from utils.constants import NOTIFICATION_TIMEOUT

class PushoverNotifier:
    """Handles Pushover API notifications."""
    
    def __init__(self, config_file=None):
        """Initialize notifier; config path comes from central config unless overridden."""
        if config_file is None:
            config_file = cfg.NOTIFIER_CONFIG_FILE
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self):
        """Load Pushover configuration from file."""
        if not os.path.exists(self.config_file):
            return {
                'app_token': None,
                'user_key': None,
                'enabled': False
            }
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Warning: Could not load Pushover config: {e}")
            return {'app_token': None, 'user_key': None, 'enabled': False}
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"❌ Error saving Pushover config: {e}")
    
    def setup_credentials(self, app_token, user_key):
        """Set up Pushover credentials and enable notifications."""
        self.config['app_token'] = app_token
        self.config['user_key'] = user_key
        self.config['enabled'] = True
        self._save_config()
        print("✅ Pushover credentials configured successfully!")
    
    def is_enabled(self):
        """Check if notifications are enabled and configured."""
        return (self.config.get('enabled', False) and 
                self.config.get('app_token') and 
                self.config.get('user_key'))
    
    def send_notification(self, title, message, priority=0):
        """
        Send a push notification via Pushover.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            priority (int): Priority level (-2 to 2, default 0)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_enabled():
            print("📱 Pushover notifications not configured or disabled")
            return False
        
        url = cfg.PUSHOVER_API_URL
        data = {
            'token': self.config['app_token'],
            'user': self.config['user_key'],
            'title': title,
            'message': message,
            'priority': priority,
            'timestamp': int(datetime.now().timestamp())
        }
        
        try:
            response = requests.post(url, data=data, timeout=NOTIFICATION_TIMEOUT)
            response.raise_for_status()
            
            result = response.json()
            if result.get('status') == 1:
                # Success logging handled by caller for better context
                return True
            else:
                print(f"❌ Pushover API error: {result.get('errors', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error sending notification: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid response from Pushover API: {e}")
            return False

    def _format_notification_message(self, daily_progress, state_data=None, json_data=None):
        """Format the 3-line notification message (pure function for easy testing)."""
        from core.metrics_calculator import get_tracked_unit_progress, calculate_performance_metrics
        from datetime import datetime
        
        completed = daily_progress['completed']
        
        if not state_data:
            goal = daily_progress['goal']
            pct = int(daily_progress['progress_pct'])
            return f"{completed} / {goal} lessons ({pct}%)\nweek avg: calculating...\nfinish: calculating..."
        
        # Get dynamic calculations
        progress = get_tracked_unit_progress(state_data)
        required_pace = progress['required_lessons_per_day']
        pct = int((completed / required_pace) * 100) if required_pace > 0 else 0
        
        # Weekly average (lessons per day)
        weekly_avg = 0
        if json_data:
            perf_metrics = calculate_performance_metrics(json_data)
            if perf_metrics:
                weekly_avg = perf_metrics['recent_avg_lessons']  # Use lessons, not sessions
        
        # Finish date with robust formatting
        finish_line = "finish: calculating..."
        projected_date = progress.get('projected_completion_date')
        months_diff = progress.get('months_difference')
        
        if projected_date and months_diff is not None:
            try:
                date_obj = datetime.strptime(projected_date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%b %d, %Y')
                
                if abs(months_diff) < 0.1:
                    timing = "on time"
                elif months_diff < 0:
                    timing = f"{abs(months_diff):.1f} mo early"
                else:
                    timing = f"{months_diff:.1f} mo late"
                
                finish_line = f"finish: {formatted_date} ({timing})"
            except (ValueError, TypeError):
                finish_line = f"finish: {projected_date}"
        
        # Course completion percentage
        course_progress_pct = progress.get('course_completion_percentage', 0)
        
        # Build 3-line message with course completion percentage
        line1 = f"{completed} / {required_pace:.1f} lessons ({pct}% daily)"
        line2 = f"course: {course_progress_pct:.1f}% • week avg: {weekly_avg:.1f}/day" if weekly_avg > 0 else f"course: {course_progress_pct:.1f}% • week avg: calculating..."
        line3 = finish_line
        
        return f"{line1}\n{line2}\n{line3}"

    def send_simple_notification(self, daily_progress, state_data=None, json_data=None, **kwargs):
        """Send enhanced 3-line notification with dynamic pace and finish date."""
        title = "📊 Duolingo Progress"
        message = self._format_notification_message(daily_progress, state_data, json_data)
        return self.send_notification(title, message, priority=0)
    

    
    def test_notification(self):
        """Send a test notification to verify setup."""
        title = "🧪 Duolingo Tracker Test"
        message = f"Test notification sent at {datetime.now().strftime('%H:%M:%S')}.\n\nYour Pushover setup is working correctly! 🎉"
        return self.send_notification(title, message)

def main():
    """CLI interface for testing and setup."""
    import sys
    
    notifier = PushoverNotifier()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            notifier.test_notification()
        elif sys.argv[1] == 'status':
            if notifier.is_enabled():
                print("✅ Pushover notifications are enabled and configured")
            else:
                print("❌ Pushover notifications are not configured")
                print("   Run setup to configure your credentials")
        else:
            print("Usage: python pushover_notifier.py [test|status]")
    else:
        print("Pushover Notifier Module")
        print("Usage: python pushover_notifier.py [test|status]")

if __name__ == "__main__":
    main() 