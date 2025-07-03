"""
Shared constants for Owlgorithm project.
Eliminates duplication of common values across modules.
"""

# Browser and HTTP constants
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

# Request headers for web scraping
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
}

# Timing constants  
DEFAULT_REQUEST_TIMEOUT = 15  # seconds
DEFAULT_SCRAPE_DELAY = 12     # seconds between requests
PAGE_LOAD_TIMEOUT = 30        # seconds for page loads
NOTIFICATION_TIMEOUT = 10     # seconds for push notifications
SUBPROCESS_TIMEOUT = 300      # seconds for subprocess operations

# URL patterns
DUOME_BASE_URL = "https://duome.eu"

# Algorithm identifiers (from duome scraper)
ALGORITHM_FIRST_MENTION = "first_mention_with_folding"
ALGORITHM_UNIT_COMPLETION = "unit_completion"

# Time slot identifiers
TIME_SLOT_MORNING = "morning"
TIME_SLOT_MIDDAY = "midday" 
TIME_SLOT_EVENING = "evening"
TIME_SLOT_NIGHT = "night"