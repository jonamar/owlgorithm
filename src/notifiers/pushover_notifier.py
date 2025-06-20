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

    def send_morning_notification(self, daily_goal, current_streak, yesterday_progress=None):
        """Send morning goal-setting notification."""
        title = "🌅 Good Morning! Daily Goal Set"
        
        message = f"Today's Target: {daily_goal} lessons\n"
        message += f"Current Streak: {current_streak} days\n"
        
        if yesterday_progress:
            completed = yesterday_progress.get('completed', 0)
            goal = yesterday_progress.get('goal', daily_goal)
            pct = int((completed / goal) * 100) if goal > 0 else 0
            message += f"Yesterday: {completed}/{goal} lessons ({pct}% of goal)\n"
        
        message += "Keep it up! 💪"
        
        return self.send_notification(title, message, priority=0)
    
    def send_midday_notification(self, daily_progress):
        """Send midday progress check notification."""
        title = "☀️ Midday Check-in"
        
        completed = daily_progress['completed']
        goal = daily_progress['goal']
        remaining = daily_progress['remaining']
        pct = int(daily_progress['progress_pct'])
        
        message = f"Progress: {completed}/{goal} lessons ({pct}%)\n"
        
        if remaining > 0:
            message += f"{remaining} lessons remaining today\n"
            message += "You're on track! 📈" if pct >= 50 else "Time to get going! 🚀"
        else:
            message += "Daily goal achieved! 🎉"
        
        # Use low priority for midday check-ins
        return self.send_notification(title, message, priority=-1)
    
    def send_evening_notification(self, daily_progress):
        """Send evening final push notification."""
        completed = daily_progress['completed']
        goal = daily_progress['goal']
        remaining = daily_progress['remaining']
        pct = int(daily_progress['progress_pct'])
        status = daily_progress['status']
        
        if status in ['ahead', 'on_track']:
            title = "🌆 Evening Update - Crushing It!"
            message = f"Progress: {completed}/{goal} lessons ({pct}%)\n"
            if completed > goal:
                message += "Daily goal exceeded! 🎉\n"
                message += f"Bonus lesson{'s' if completed - goal > 1 else ''} completed!"
            else:
                message += "Daily goal achieved! 🎉"
            priority = 0
        else:
            title = "🌆 Evening Check - Final Push!"
            message = f"Progress: {completed}/{goal} lessons ({pct}%)\n"
            message += f"{remaining} lesson{'s' if remaining > 1 else ''} needed before bed\n"
            message += "You've got this! 🎯"
            priority = 1  # Higher priority when behind
        
        return self.send_notification(title, message, priority=priority)
    
    def send_night_notification(self, daily_progress, units_completed=0, trajectory_info=None):
        """Send night recap notification."""
        completed = daily_progress['completed']
        goal = daily_progress['goal']
        status = daily_progress['status']
        
        if status in ['ahead', 'on_track']:
            title = "🌙 Day Complete - Great Work!"
            message = f"Final Count: {completed}/{goal} lessons ✅\n"
            message += "Daily goal achieved!\n"
            priority = 1
        else:
            title = "🌙 Day Complete - Tomorrow's Fresh Start!"
            message = f"Final Count: {completed}/{goal} lessons\n"
            message += "Don't worry, tomorrow's a new chance! 💪\n"
            priority = 2 if completed == 0 else 1
        
        if units_completed > 0:
            message += f"Units completed: {units_completed} 🎉\n"
        
        if trajectory_info:
            message += f"Overall progress: {trajectory_info.get('progress_pct', 0):.1f}% complete\n"
        
        message += f"Tomorrow's goal: {goal} lessons"
        
        return self.send_notification(title, message, priority=priority)

    def send_daily_update(self, newly_completed_units, total_lessons, lessons_per_day_required, time_per_day_required):
        """
        Send a formatted daily progress update notification.
        DEPRECATED: Use time-specific methods instead.
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