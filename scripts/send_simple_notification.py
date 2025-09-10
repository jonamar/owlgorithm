#!/usr/bin/env python3
"""Send a simple Pushover notification with no progress logic.

This script is intended to be scheduled by cron to send a reminder
message every 30 minutes between 08:30 and 12:00. It is decoupled from
scraping and the daily tracker to prevent duplicate notifications.
"""

import os
import sys
from datetime import datetime

# Ensure project root & src are on path (for imports when run via cron)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SRC_DIR)

from src.notifiers.pushover_notifier import PushoverNotifier  # noqa: E402


def main() -> None:
    notifier = PushoverNotifier()
    if not notifier.is_enabled():
        print("📱 Pushover not configured; skipping send.")
        return

    now = datetime.now().strftime('%-I:%M %p') if sys.platform == 'darwin' else datetime.now().strftime('%I:%M %p').lstrip('0')
    title = "🦉 Duolingo Reminder"
    message = (
        f"Check-in window (08:30–12:00). Time now: {now}.\n"
        "Take a quick lesson or review session."
    )

    ok = notifier.send_notification(title=title, message=message, priority=0)
    print(f"Notification sent: {ok}")


if __name__ == "__main__":
    main()
