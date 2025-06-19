#!/usr/bin/env python3
"""Lightweight CLI to run analysis/report only.

Useful when the data has already been scraped (e.g., via scheduler) and you
just want a summary without hitting duome.eu again.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_DIR))

from config import app_config as cfg  # noqa: E402
from src.core.daily_scheduler import DailyDuolingoTracker  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze existing Duolingo data and print a summary report.")
    parser.add_argument("--username", "-u", default=cfg.USERNAME, help="Duolingo username")
    parser.add_argument("--data-dir", "-d", default=cfg.DATA_DIR, help="Directory containing data files")
    args = parser.parse_args()

    tracker = DailyDuolingoTracker(args.username, args.data_dir)
    analysis = tracker.analyze_progress()
    report = tracker.generate_report(analysis)
    print(report)


if __name__ == "__main__":
    main()
