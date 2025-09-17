#!/usr/bin/env python3
"""Duolingo informal API data source (skeleton).

Fetches session data using a logged-in HTTP client, and normalizes it to the
same shape used elsewhere in the system.

Normalization schema:
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

NOTE: This is a scaffold. It expects credentials from environment variables
or config, and should be extended to hit the exact endpoints you choose.
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List, Tuple
import os
import time
import json
import requests
from datetime import datetime

from config import app_config as cfg

# Known/legacy endpoints to attempt. Duolingo changes these occasionally; we try a few.
LOGIN_ENDPOINTS: Tuple[str, ...] = (
    "https://www.duolingo.com/2017-06-30/login",
    "https://www.duolingo.com/login",
)


def _try_login(session: requests.Session, user: str, password: str) -> bool:
    """Attempt login using one of the known endpoints. Return True if it looks successful.

    Criteria for success:
    - HTTP 200/204 response
    - And either a JSON with a user or id/token field, or auth cookies set.
    """
    payload_json = {"identifier": user, "password": password}
    payload_form = {"login": user, "password": password}

    for url in LOGIN_ENDPOINTS:
        try:
            # Prefer JSON
            r = session.post(url, json=payload_json, timeout=20)
            if r.status_code in (200, 204):
                # Heuristic checks
                if r.headers.get("set-cookie") or session.cookies.get_dict():
                    print(f"✅ Duolingo login OK via {url} (cookies present)")
                    return True
                try:
                    data = r.json()
                    if isinstance(data, dict) and ("user_id" in data or "jwt" in data or "id" in data):
                        print(f"✅ Duolingo login OK via {url} (token/id present)")
                        return True
                except ValueError:
                    # Non-JSON but success code + cookies may still indicate success
                    pass

            # Fallback to form-encoded if JSON didn't work
            r = session.post(url, data=payload_form, timeout=20)
            if r.status_code in (200, 204):
                if r.headers.get("set-cookie") or session.cookies.get_dict():
                    print(f"✅ Duolingo login OK via {url} (form, cookies present)")
                    return True
                try:
                    data = r.json()
                    if isinstance(data, dict) and ("user_id" in data or "jwt" in data or "id" in data):
                        print(f"✅ Duolingo login OK via {url} (form, token/id present)")
                        return True
                except ValueError:
                    pass

            print(f"ℹ️ Login attempt to {url} returned status {r.status_code}")
        except requests.RequestException as e:
            print(f"⚠️ Login request to {url} failed: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error during login to {url}: {e}")

    return False


def _normalize_sessions(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize raw Duolingo API payload into the tracker schema.

    For now, expects a structure with a list under key 'sessions' or
    any iterable of entries from which we can derive required fields.
    This should be adapted once the exact endpoints are finalized.
    """
    sessions: List[Dict[str, Any]] = []

    # Example placeholder normalization; replace with real mapping.
    # If the raw payload already has sessions, map fields; otherwise return empty.
    raw_sessions = raw.get("sessions", []) if isinstance(raw, dict) else []
    for s in raw_sessions:
        # Derive fields with conservative defaults
        dt = s.get("datetime") or s.get("timestamp") or datetime.now().isoformat()
        try:
            date_only = dt[:10]
        except Exception:
            date_only = datetime.now().strftime("%Y-%m-%d")

        sessions.append({
            "date": date_only,
            "datetime": dt,
            "xp": int(s.get("xp", 0)),
            "is_lesson": bool(s.get("is_lesson", True)),
            "is_unit_completion": bool(s.get("is_unit_completion", False)),
            "unit": s.get("unit"),
        })

    return {"sessions": sessions}


def fetch_sessions(*, username: str) -> Optional[Dict[str, Any]]:
    """Fetch normalized sessions from the Duolingo informal API.

    Returns None on failure. This is a minimal scaffold to be evolved.
    """
    # Resolve credentials (prefer env, fallback to config placeholders)
    user = os.environ.get("DUOLINGO_USERNAME", cfg.DUOLINGO_USERNAME or username)
    password = os.environ.get("DUOLINGO_PASSWORD", cfg.DUOLINGO_PASSWORD)

    if not user or not password:
        print("⚠️ Duolingo API credentials not provided; cannot fetch.")
        return None

    try:
        # Basic session handling
        session = requests.Session()
        session.headers.update({
            "User-Agent": "owlgorithm/1.0 (https://github.com/jonamar/owlgorithm)",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

        # 1) Attempt login
        print("🔐 Attempting Duolingo login...")
        if not _try_login(session, user, password):
            print("❌ Duolingo login failed; cannot proceed to fetch.")
            return None
        print("🔐 Login successful. Proceeding to fetch data...")

        # 2) TODO: Replace with actual data fetch endpoints.
        # Example placeholder payload until we map the real endpoint(s).
        raw_payload = {"sessions": []}

        # Normalize (still empty until real mapping is done)
        normalized = _normalize_sessions(raw_payload)
        return normalized

    except requests.RequestException as e:
        print(f"❌ Network error contacting Duolingo API: {e}")
        return None
    except Exception as e:
        print(f"❌ Error in Duolingo API fetch: {e}")
        return None
