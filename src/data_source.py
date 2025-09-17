#!/usr/bin/env python3
"""Data source dispatcher for fetching session data.

Provides a single function `fetch_sessions(backend, username)` that returns
normalized JSON used by downstream metrics, markdown updates, and notifications.

Schema contract for returned JSON:
{
  "sessions": [
    {
      "date": "YYYY-MM-DD",
      "datetime": "YYYY-MM-DDTHH:MM:SS",
      "xp": int,
      "is_lesson": bool,
      "is_unit_completion": bool,
      "unit": str | None
    },
    ...
  ]
}
"""
from __future__ import annotations

from typing import Optional, Dict, Any

from config import app_config as cfg


def fetch_sessions(*, backend: str, username: str) -> Optional[Dict[str, Any]]:
    """Dispatch to the selected backend and return normalized JSON.

    Args:
        backend: "duome" or "duolingo_api"
        username: Duolingo username
    Returns:
        dict with key "sessions" or None on failure
    """
    backend = (backend or "duome").lower()
    if backend == "duolingo_api":
        try:
            from src.data_sources.duolingo_api_source import fetch_sessions as fetch_duolingo
            return fetch_duolingo(username=username)
        except Exception as e:
            print(f"❌ Duolingo API backend failed: {e}")
            return None
    else:
        # For duome backend, we return None here and allow existing scraper path to run.
        # This keeps minimal churn and avoids circular imports with tracker_helpers.
        return None
