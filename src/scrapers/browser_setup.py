"""WebDriver factory functions for Duolingo tracker.

Currently supports Chrome and Firefox via webdriver-manager. Centralising these
helpers avoids duplicated setup logic in scraper modules.
"""
from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


__all__ = ["get_chrome_driver", "get_firefox_driver"]


def get_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    """Return a ready-to-use Chrome WebDriver."""
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def get_firefox_driver(headless: bool = True) -> webdriver.Firefox:
    """Return a ready-to-use Firefox WebDriver."""
    options = FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    service = FirefoxService(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)
