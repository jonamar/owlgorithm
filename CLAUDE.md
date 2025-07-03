# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Owlgorithm is a Python-based Duolingo progress tracker that scrapes data from duome.eu to provide accurate lesson tracking and progress analytics. It features automated notifications, detailed statistics computation, and scheduled tracking via cron jobs.

## Key Commands

### Setup & Environment
```bash
# Create and activate virtual environment
python -m venv duolingo_env
source duolingo_env/bin/activate  # On Windows: duolingo_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# One-time project setup
python scripts/setup.py --all
```

### Daily Operations
```bash
# Run complete daily update (scrape + analysis + notifications)
python scripts/daily_update.py

# Override username
python scripts/daily_update.py --username USERNAME

# Run scraper only
python src/scrapers/duome_raw_scraper.py --username USERNAME

# Force refresh duome.eu stats  
python src/scrapers/duome_raw_scraper.py --username USERNAME --update-only

# Validate headless scraping functionality
python src/scrapers/duome_raw_scraper.py --validate-headless --username USERNAME
```

### Deployment
```bash
# Check launchd service status
launchctl list | grep owlgorithm

# Load/reload launchd service (if needed)
launchctl load ~/Library/LaunchAgents/com.owlgorithm.duolingo.plist

# Manual tracker execution
./run_tracker.sh
```

## Architecture

### Core Components
- **Scrapers** (`src/scrapers/`): Web scraping with Selenium, auto-refresh duome.eu stats
- **Core Logic** (`src/core/`): Daily tracking orchestration and lesson computation
- **Notifiers** (`src/notifiers/`): Pushover notifications with time-based smart logic
- **Analyzers** (`src/analyzers/`): Data analysis and statistics computation

### Configuration
- **Central config**: `config/app_config.py` - Username, course metrics, file paths
- **Notification config**: `config/pushover_config.json` - API keys and settings
- **State tracking**: `tracker_state.json` - Persistent state for daily progress

### Data Flow
1. **Scraper** auto-refreshes duome.eu and extracts session data
2. **Core tracker** computes lesson metrics (core vs practice sessions)
3. **Markdown updater** updates `personal-math.md` with progress stats
4. **Notifier** sends time-appropriate notifications (morning goals, evening progress, etc.)

### Key Features
- **Accurate lesson counting**: Distinguishes core lessons from practice sessions
- **Smart notifications**: Different messages for morning/midday/evening/night
- **Daily progress tracking**: Reset counters, track streaks, compute projections
- **Auto-refresh**: Clicks duome.eu update button before scraping
- **Firefox-only browser automation**: Simplified, reliable browser setup with enhanced error handling
- **launchd scheduling**: Runs 4x daily (6am, 12pm, 5pm, 10pm) via macOS native scheduler

## File Structure

### Scripts
- `scripts/daily_update.py`: Main entry point for daily operations
- `scripts/setup.py`: One-time setup and dependency checking
- `scripts/analyze.py`: Data analysis utilities
- `scripts/setup_pushover.py`: Notification setup

### Data Files
- `data/duome_raw_USERNAME_TIMESTAMP.json`: Raw scraped session data
- `personal-math.md`: Markdown progress report (auto-updated)
- `tracker_state.json`: Persistent state for daily tracking
- `logs/`: Execution logs and debugging output

### Configuration Notes
- Username and course settings in `config/app_config.py`
- Notification credentials in `config/pushover_config.json` (not committed)
- launchd schedule in `~/Library/LaunchAgents/com.owlgorithm.duolingo.plist` (4 times daily)

## Dependencies

Core: Selenium, requests, beautifulsoup4, pandas, webdriver-manager
Browser: Firefox with geckodriver (auto-installed)
Environment: Python 3.7+, virtual environment recommended

## CURRENT PROJECT STATUS (July 2025) ✅

### SYSTEM FULLY OPERATIONAL 🎉
**All major issues resolved and system working perfectly:**
- ✅ **Automation**: Running successfully every 30 minutes (6am-midnight)
- ✅ **Notifications**: Correct daily goal display ("X/12 lessons today")
- ✅ **Scraping**: Headless Firefox working reliably with auto-refresh
- ✅ **Data Processing**: Accurate lesson counting and progress tracking
- ✅ **Architecture**: Clean, maintainable codebase with single source of truth

### COMPLETED MAJOR WORK ✅
- ✅ **Daily Goal Fix**: Notifications now show "X/12 lessons today" correctly
- ✅ **Clean Data Model**: Tracking-only approach (3 units vs 86 historical confusion)
- ✅ **Calculation Unification**: Single source of truth for all progress calculations
- ✅ **18-Month Goal Tracking**: Comprehensive burn rate analysis and projections
- ✅ **Architecture Consolidation**: Centralized constants and eliminated major duplications
- ✅ **Environment Migration**: Successfully moved to ~/Development/owlgorithm
- ✅ **Comprehensive Testing**: 103/112 tests passing, full pipeline validation

### DEVELOPMENT PLAN 📋
See `plan.md` for complete development roadmap and remaining work.

**Next Priority**: Epic 6 (Final Deduplication) - 3-5 hours to achieve perfect codebase
- Eliminate remaining 46 duplication instances
- Complete utilization of created utility modules
- Replace remaining magic numbers with named constants

## Important Notes

- Requires active duome.eu profile (username must exist publicly)
- Uses Selenium for auto-refresh functionality (now runs headless by default)
- No Duolingo credentials needed (scrapes public duome.eu data)
- Includes respectful delays and error handling for web scraping
- State management prevents duplicate notifications
- **Daily goal**: Hardcoded to 12 lessons/day (no dynamic calculation to avoid bugs)
- **Automation status**: ✅ Working with headless scraping

## Development Principles

- If you think you fixed broken functionality, assume you are wrong until you have proof. First level proof is running a manual end-to-end test of the real system. Second level proof is when prescheduled automation runs successfully. The user can confirm whether they have received a notification in both cases.