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

# Candidate data endpoints (subject to change by Duolingo)
USER_LOOKUP_URL = "https://www.duolingo.com/2017-06-30/users"
USER_DETAIL_URL = "https://www.duolingo.com/2017-06-30/users/{user_id}?fields=calendar,streakData"
ACTIVITY_URLS: Tuple[str, ...] = (
    # historical variants observed in client traffic; may vary
    "https://www.duolingo.com/2017-06-30/activities?username={username}",
    "https://www.duolingo.com/2017-06-30/activity?username={username}",
)

# iOS API host often exposes richer fields like xpGains
IOS_USER_DETAIL_URLS: Tuple[str, ...] = (
    "https://ios-api-2.duolingo.com/2017-06-30/users/{user_id}?fields=xpGains",
    "https://ios-api-2.duolingo.com/2017-06-30/users/{user_id}/xpGains",
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


def _build_sessions_from_activity(activity_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    sessions: List[Dict[str, Any]] = []
    # Try common shapes
    items = []
    if isinstance(activity_payload, dict):
        if isinstance(activity_payload.get("activities"), list):
            items = activity_payload.get("activities")
        elif isinstance(activity_payload.get("events"), list):
            items = activity_payload.get("events")

    for a in items:
        # Pull a timestamp
        dt = (
            a.get("datetime")
            or a.get("creationDate")
            or a.get("timestamp")
            or datetime.now().isoformat()
        )
        date_only = dt[:10] if isinstance(dt, str) and len(dt) >= 10 else datetime.now().strftime("%Y-%m-%d")

        # Determine type and map to lesson boolean
        a_type = (a.get("type") or a.get("eventType") or "").lower()
        is_lesson = any(k in a_type for k in ["lesson", "practice", "story", "review"]) or bool(a.get("is_lesson", False))

        # Unit completion heuristic
        is_unit_completion = any(k in a_type for k in ["unit_complete", "skill_complete", "level_complete"]) or bool(a.get("is_unit_completion", False))

        # Unit/skill name if present
        unit = a.get("unit") or a.get("skillTitle") or a.get("skill") or None

        # XP if present
        xp = 0
        for key in ("xp", "improvement", "gain", "earnedXp"):
            try:
                if key in a and isinstance(a[key], (int, float)):
                    xp = int(a[key])
                    break
            except Exception:
                pass

        sessions.append({
            "date": date_only,
            "datetime": dt if isinstance(dt, str) else datetime.now().isoformat(),
            "xp": xp,
            "is_lesson": is_lesson,
            "is_unit_completion": is_unit_completion,
            "unit": unit,
        })

    return sessions


def _build_sessions_from_calendar(detail_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    sessions: List[Dict[str, Any]] = []
    calendar = {}
    if isinstance(detail_payload, dict):
        calendar = detail_payload.get("calendar") or {}

    # Some payloads have calendar as dict of date->stats
    if isinstance(calendar, dict):
        for d, stats in calendar.items():
            try:
                # If only daily xp available, synthesize a single session entry per day
                xp = 0
                if isinstance(stats, dict):
                    for key in ("xp", "dailyXp", "improvement", "gainedXp"):
                        if key in stats and isinstance(stats[key], (int, float)):
                            xp = int(stats[key])
                            break
                sessions.append({
                    "date": d,
                    "datetime": f"{d}T00:00:00",
                    "xp": xp,
                    "is_lesson": True,
                    "is_unit_completion": False,
                    "unit": None,
                })
            except Exception:
                continue
    return sessions


def _fetch_activity_and_profile(session: requests.Session, username: str) -> Dict[str, Any]:
    """Try multiple endpoints to collect user id, activity, and calendar info."""
    result: Dict[str, Any] = {"sessions": []}

    # 1) User lookup to get user_id
    user_id = None
    try:
        r = session.get(USER_LOOKUP_URL, params={"username": username}, timeout=20)
        print(f"🔎 users?username status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            # Possible shapes: {"users":[{"id":..., "username":...}]} or direct dict
            if isinstance(data, dict):
                if isinstance(data.get("users"), list) and data["users"]:
                    user_id = data["users"][0].get("id") or data["users"][0].get("user_id")
                elif "id" in data:
                    user_id = data.get("id")
    except Exception as e:
        print(f"⚠️ users lookup error: {e}")

    # 2) Try activities endpoints
    for url in ACTIVITY_URLS:
        try:
            u = url.format(username=username)
            ra = session.get(u, timeout=20)
            print(f"📜 activity fetch {u} -> {ra.status_code}")
            if ra.status_code == 200:
                act_data = ra.json()
                sessions = _build_sessions_from_activity(act_data)
                if sessions:
                    result["sessions"].extend(sessions)
                    break
        except Exception as e:
            print(f"⚠️ activity fetch error: {e}")

    # 3) Fallback: calendar from user detail if we have user_id
    if user_id:
        try:
            ud_url = USER_DETAIL_URL.format(user_id=user_id)
            rd = session.get(ud_url, timeout=20)
            print(f"📅 user detail fetch {ud_url} -> {rd.status_code}")
            if rd.status_code == 200:
                detail = rd.json()
                cal_sessions = _build_sessions_from_calendar(detail)
                if cal_sessions:
                    result["sessions"].extend(cal_sessions)
        except Exception as e:
            print(f"⚠️ user detail fetch error: {e}")

        # 4) Try iOS endpoints for xpGains (often most useful for daily increments)
        for ios_url in IOS_USER_DETAIL_URLS:
            try:
                url = ios_url.format(user_id=user_id)
                rx = session.get(url, timeout=20)
                print(f"📈 ios xpGains fetch {url} -> {rx.status_code}")
                if rx.status_code == 200:
                    data = rx.json()
                    # xpGains may be a list or nested
                    gains = []
                    if isinstance(data, dict):
                        if isinstance(data.get('xpGains'), list):
                            gains = data.get('xpGains')
                        elif isinstance(data.get('data'), list):  # fallback shape
                            gains = data.get('data')
                    if gains:
                        # Convert to sessions (one per gain)
                        for g in gains:
                            dt = g.get('creationDate') or g.get('datetime') or g.get('timestamp') or datetime.now().isoformat()
                            date_only = dt[:10] if isinstance(dt, str) and len(dt) >= 10 else datetime.now().strftime('%Y-%m-%d')
                            xp = 0
                            try:
                                xp = int(g.get('xp', 0))
                            except Exception:
                                pass
                            result['sessions'].append({
                                'date': date_only,
                                'datetime': dt if isinstance(dt, str) else datetime.now().isoformat(),
                                'xp': xp,
                                'is_lesson': True,  # minimal assumption for daily count
                                'is_unit_completion': False,
                                'unit': None,
                            })
                        break  # stop after first successful ios endpoint
            except Exception as e:
                print(f"⚠️ ios xpGains fetch error: {e}")

    return result


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

        # 2) Attempt to fetch activity/profile data and normalize
        raw_payload = _fetch_activity_and_profile(session, user)
        # Already mostly in normalized shape; pass through normalizer to ensure keys
        normalized = _normalize_sessions(raw_payload)
        print(f"✅ Normalized {len(normalized.get('sessions', []))} session entries from API")
        return normalized

    except requests.RequestException as e:
        print(f"❌ Network error contacting Duolingo API: {e}")
        return None
    except Exception as e:
        print(f"❌ Error in Duolingo API fetch: {e}")
        return None
