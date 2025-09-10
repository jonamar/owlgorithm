#!/usr/bin/env python3
"""Send a rich Pushover notification with live progress (x/12) and weekly avg.

Scheduled by cron (08:30–12:00). This script:
1) Runs the scraper to fetch fresh data
2) Computes today's lessons and weekly average
3) Sends the existing formatted message via PushoverNotifier
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
from src.core.tracker_helpers import run_scraper_and_load_data  # noqa: E402
from src.core.metrics_calculator import count_todays_lessons, calculate_daily_progress, calculate_performance_metrics  # noqa: E402
from config import app_config as cfg  # noqa: E402
from data.repository import AtomicJSONRepository  # noqa: E402


def main() -> None:
    notifier = PushoverNotifier()
    if not notifier.is_enabled():
        print("📱 Pushover not configured; skipping send.")
        return

    # 1) Run scraper and load fresh JSON
    json_data, _ = run_scraper_and_load_data(logger=None)
    if not json_data:
        print("❌ No JSON data available; sending plain reminder instead.")
        now = datetime.now().strftime('%-I:%M %p') if sys.platform == 'darwin' else datetime.now().strftime('%I:%M %p').lstrip('0')
        notifier.send_notification(title="🦉 Duolingo Reminder", message=f"Check-in window (08:30–12:00). Time now: {now}.", priority=0)
        return

    # 2) Load state and compute today's lessons (x/12)
    state_repo = AtomicJSONRepository(cfg.STATE_FILE, auto_migrate=True)
    state_data = state_repo.load({})

    today = datetime.now().strftime('%Y-%m-%d')
    todays_lessons = count_todays_lessons(json_data, today)
    state_data['daily_lessons_completed'] = todays_lessons
    state_data['daily_goal_lessons'] = cfg.DAILY_GOAL_LESSONS

    # 3) Compute daily progress and weekly averages
    daily_progress = calculate_daily_progress(state_data)
    # calculate_performance_metrics is used within notifier formatting, but we compute json_data anyway
    perf = calculate_performance_metrics(json_data)
    _ = perf  # not needed directly here; kept for clarity

    # 4) Send the existing formatted rich message
    ok = notifier.send_simple_notification(
        daily_progress=daily_progress,
        state_data=state_data,
        json_data=json_data,
    )
    print(f"Notification sent: {ok} (completed {todays_lessons}/{cfg.DAILY_GOAL_LESSONS})")


if __name__ == "__main__":
    main()
