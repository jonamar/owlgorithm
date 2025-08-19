#!/usr/bin/env python3
"""Convenient entry-point script to perform a full daily Duolingo update.

Runs the end-to-end workflow: scrape → parse → update markdown → notifications.
Internally delegates to `src.core.daily_tracker.main()` to avoid code duplication.
"""

from __future__ import annotations

import argparse
import os
import sys
import fcntl

# Ensure project root & src are on path (needed when the script is executed
# from an arbitrary working directory or via cron).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SRC_DIR)

from config import app_config as cfg  # noqa: E402
from src.core.daily_tracker import main as tracker_main  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the full daily Duolingo update (scrape + report update)"
    )
    parser.add_argument(
        "--username",
        "-u",
        default=cfg.USERNAME,
        help="Duolingo username (overrides value in config if given)",
    )
    args = parser.parse_args()

    # Allow overriding username at runtime without editing config file.
    if args.username != cfg.USERNAME:
        cfg.USERNAME = args.username

    # Single-instance lock to prevent overlapping runs (cron/manual)
    lock_path = "/tmp/owlgorithm_daily_tracker.lock"
    # Ensure the lock file exists and acquire a non-blocking exclusive lock
    with open(lock_path, "w") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_file.write(str(os.getpid()))
            lock_file.flush()
        except BlockingIOError:
            print("⚠️ Another owlgorithm daily update is already running. Skipping this run.")
            return

        # Run the tracker while holding the lock
        tracker_main()


if __name__ == "__main__":
    main()
