"""Central configuration for Duolingo tracker project."""
import os

# --- User / course settings ---
USERNAME: str = "YOUR_USERNAME"  # Your Duolingo username

# --- Course structure constants ---
TOTAL_COURSE_UNITS: int = 272  # Total units in your course (adjust for your language)
UNITS_COMPLETED_BEFORE_TRACKING: int = 0  # Units completed before tracking started
TRACKABLE_TOTAL_UNITS: int = TOTAL_COURSE_UNITS - UNITS_COMPLETED_BEFORE_TRACKING
ACTUALLY_COMPLETED_TOTAL: int = UNITS_COMPLETED_BEFORE_TRACKING  # Historical + tracked units

# --- Goal and timeline constants ---
GOAL_DAYS: int = 548  # Your goal timeline in days (18 months = 548 days)
TRACKING_START_DATE: str = "2025-01-01"  # When you started tracking (YYYY-MM-DD)
ANALYSIS_START_DATE: str = "2025-01-01"  # Analysis start date (YYYY-MM-DD)

# --- Tracked units (tracking-only data model) ---
TRACKED_COMPLETE_UNITS: list = []  # Units completed since tracking started
EXCLUDED_PARTIAL_UNITS: list = []  # Units with partial data to exclude

# --- Calculation constants ---
BASE_LESSONS_PER_UNIT: int = 31  # Average lessons per unit in your course
BASE_MINS_PER_LESSON: float = 7.5  # Average minutes per lesson
DAILY_GOAL_LESSONS: int = 12  # Your daily lesson target

# --- Environment and execution constants ---
VENV_PYTHON_PATH: str = "/path/to/your/project/duolingo_env/bin/python"  # Virtual environment Python path

# --- API endpoints ---
PUSHOVER_API_URL: str = "https://api.pushover.net/1/messages.json"

# --- Timeout Configuration ---
BROWSER_WAIT_TIMEOUT: int = 15          # WebDriver wait timeout in seconds
VALIDATION_WAIT_SECONDS: int = 30       # Headless validation wait time

# --- Time Slot Configuration ---
MORNING_START_HOUR: int = 5             # Morning start (5 AM)
MORNING_END_HOUR: int = 11              # Morning end (11 AM)
MIDDAY_END_HOUR: int = 16               # Midday end (4 PM)
EVENING_END_HOUR: int = 21              # Evening end (9 PM)

# --- Legacy compatibility (DEPRECATED - use TRACKABLE_TOTAL_UNITS) ---
TOTAL_UNITS_IN_COURSE: int = TRACKABLE_TOTAL_UNITS  # For backward compatibility

# --- Primary file paths ---
MARKDOWN_FILE: str = "personal-math.md"  # Your progress report file
STATE_FILE: str = "tracker_state.json"  # Tracker state file

# --- Derived directories (relative to project root) ---
DATA_DIR: str = "data"
LOG_DIR: str = "logs"
CONFIG_DIR: str = "config"

# --- Other file paths ---
NOTIFIER_CONFIG_FILE: str = os.path.join(CONFIG_DIR, "pushover_config.json") 