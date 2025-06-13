#!/usr/bin/env python3
"""
Pushover Setup Script
Interactive setup for Pushover notifications in the Duolingo tracker.
"""

from pushover_notifier import PushoverNotifier

def main():
    """Interactive setup for Pushover credentials."""
    print("🔧 Pushover Notification Setup")
    print("=" * 40)
    print()
    print("To set up push notifications, you'll need:")
    print("1. A Pushover account (https://pushover.net)")
    print("2. The Pushover app on your phone")
    print("3. Your User Key (from your Pushover dashboard)")
    print("4. An Application Token (create one at https://pushover.net/apps/build)")
    print()
    
    # Check current status
    notifier = PushoverNotifier()
    if notifier.is_enabled():
        print("✅ Pushover is already configured!")
        choice = input("Do you want to reconfigure? (y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            print("Setup cancelled.")
            return
        print()
    
    # Get credentials
    print("📱 Enter your Pushover credentials:")
    print()
    
    user_key = input("User Key (32 characters): ").strip()
    if len(user_key) != 30:
        print("⚠️  Warning: User Key should be 30 characters long")
    
    app_token = input("Application Token (30 characters): ").strip()
    if len(app_token) != 30:
        print("⚠️  Warning: Application Token should be 30 characters long")
    
    if not user_key or not app_token:
        print("❌ Both User Key and Application Token are required!")
        return
    
    # Save credentials
    notifier.setup_credentials(app_token, user_key)
    
    # Test the setup
    print()
    print("🧪 Testing notification...")
    success = notifier.test_notification()
    
    if success:
        print()
        print("🎉 Setup complete! You'll now receive daily Duolingo progress notifications.")
        print("   Notifications will be sent after each daily data update.")
    else:
        print()
        print("❌ Test failed. Please check your credentials and try again.")
        print("   Make sure you have the Pushover app installed on your phone.")

if __name__ == "__main__":
    main() 