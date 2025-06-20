"""Simple HTTP fetcher for duome.eu pages.

Provides `fetch_duome_page(username)` which returns the HTML string or `None`
on failure. Designed to be used as a lightweight alternative before falling
back to Selenium-based automation.
"""
from __future__ import annotations

from typing import Optional
import requests


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif," "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

REQUEST_TIMEOUT = 15  # seconds


def fetch_duome_page(username: str) -> Optional[str]:
    """Return HTML of `https://duome.eu/<username>` or ``None`` on failure."""
    url = f"https://duome.eu/{username}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except (requests.RequestException, Exception) as exc:  # broad except ok for network
        print(f"HTTP fetch failed: {exc}")
        return None
