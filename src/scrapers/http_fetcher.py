"""Simple HTTP fetcher for duome.eu pages.

Provides `fetch_duome_page(username)` which returns the HTML string or `None`
on failure. Designed to be used as a lightweight alternative before falling
back to Selenium-based automation.
"""
from __future__ import annotations

import os
import sys
from typing import Optional
import requests

# Add project root and src to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SRC_DIR)

from utils.constants import DEFAULT_HEADERS, DEFAULT_REQUEST_TIMEOUT

HEADERS = DEFAULT_HEADERS
REQUEST_TIMEOUT = DEFAULT_REQUEST_TIMEOUT


def fetch_duome_page(username: str) -> Optional[str]:
    """Return HTML of `https://duome.eu/<username>` or ``None`` on failure."""
    from utils.path_utils import build_duome_url
    url = build_duome_url(username)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except (requests.RequestException, Exception) as exc:  # broad except ok for network
        print(f"HTTP fetch failed: {exc}")
        return None
