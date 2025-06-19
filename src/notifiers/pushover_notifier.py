#!/usr/bin/env python3
"""
Pushover Notification Module
Handles sending push notifications via Pushover API for Duolingo progress updates.
"""

import os
import json
import requests
from config import app_config as cfg
from datetime import datetime

class PushoverNotifier:
    """Handles Pushover API notifications."""
    
    def __init__(self, config_file: str | None = None):
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
        
        url = "https://api.pushover.net/1/messages.json"
        data = {
            'token': self.config['app_token'],
            'user': self.config['user_key'],
            'title': title,
            'message': message,
            'priority': priority,
            'timestamp': int(datetime.now().timestamp())
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('status') == 1:
                print("📱 Push notification sent successfully!")
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
    
    def send_daily_update(self, newly_completed_units, total_lessons, lessons_per_day_required, time_per_day_required):
        """
        Send a formatted daily progress update notification.
        
        Args:
            newly_completed_units (int): Number of newly completed units
            total_lessons (int): Total lessons completed
            lessons_per_day_required (float): Required lessons per day for goal
            time_per_day_required (str): Required time per day for goal
        """
        if newly_completed_units > 0:
            title = f"🎉 Duolingo Progress - {newly_completed_units} Unit{'s' if newly_completed_units > 1 else ''} Completed!"
            message = f"Great work! You completed {newly_completed_units} unit{'s' if newly_completed_units > 1 else ''} today.\n\n"
        else:
            title = "📊 Duolingo Daily Update"
            message = "Daily progress check complete.\n\n"
        
        message += f"📈 Total Lessons: {total_lessons:,}\n"
        message += f"🎯 Daily Target: ~{lessons_per_day_required:.1f} lessons\n"
        message += f"⏰ Time Needed: {time_per_day_required}"
        
        # Use higher priority for unit completions
        priority = 1 if newly_completed_units > 0 else 0
        
        return self.send_notification(title, message, priority)
    
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