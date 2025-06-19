#!/usr/bin/env python3
"""Project setup utility.

Provides interactive helpers to:
1. Verify Python dependencies (simple check that `requirements.txt` packages import).
2. Configure Pushover credentials via `PushoverNotifier` wizard.
3. Create default directories (data, logs, config) if missing.

This script is a convenience wrapper around the existing utilities so new users
can get running with a single command:

    python scripts/setup.py --all

"""
from __future__ import annotations

import importlib
import os
import sys
import argparse
from pathlib import Path

# Make sure project root and src are importable
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_DIR))

from config import app_config as cfg  # noqa: E402
from notifiers.pushover_notifier import PushoverNotifier  # noqa: E402

REQUIRED_PACKAGES = [
    "requests",
    "pandas",
    "bs4",
]


def check_dependencies() -> bool:
    print("🔍 Checking Python dependencies…")
    all_ok = True
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            print(f"✅ {pkg}")
        except ImportError:
            print(f"❌ Missing package: {pkg}")
            all_ok = False
    if not all_ok:
        print("\nPlease install missing packages: pip install -r requirements.txt")
    return all_ok


def ensure_directories() -> None:
    for d in [cfg.DATA_DIR, cfg.LOG_DIR, cfg.CONFIG_DIR]:
        Path(d).mkdir(exist_ok=True)
        print(f"📁 Ensured directory: {d}")


def configure_pushover() -> None:
    notifier = PushoverNotifier()
    if notifier.is_enabled():
        print("✅ Pushover already configured.")
        return

    print("\n🔧 Starting Pushover setup wizard…")
    user_key = input("User Key: ").strip()
    app_token = input("Application Token: ").strip()
    if not user_key or not app_token:
        print("❌ Credentials not provided – skipping setup.")
        return

    notifier.setup_credentials(app_token, user_key)
    notifier.test_notification()


def main() -> None:
    parser = argparse.ArgumentParser(description="Project setup helper")
    parser.add_argument("--deps", action="store_true", help="Check Python dependencies")
    parser.add_argument("--pushover", action="store_true", help="Run Pushover credential setup")
    parser.add_argument("--dirs", action="store_true", help="Ensure data/log/config directories exist")
    parser.add_argument("--all", action="store_true", help="Run everything")
    args = parser.parse_args()

    if args.all or args.dirs:
        ensure_directories()
    if args.all or args.deps:
        check_dependencies()
    if args.all or args.pushover:
        configure_pushover()


if __name__ == "__main__":
    main()
