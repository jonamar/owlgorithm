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

## CRITICAL CURRENT STATUS (June 29, 2025)

### AUTOMATION FAILURE DIAGNOSED ⚠️
**ROOT CAUSE**: macOS security restrictions prevent launchd from accessing ~/Documents/ folder
- Manual execution: ✅ Works perfectly (notifications received at 10:55, 11:02)
- Automated execution: ❌ Fails with "Operation not permitted" (exit code 78)
- Firefox browser never opens during automated runs
- All code is working correctly - this is an environment/permissions issue

### SUCCESS CRITERIA 🎯
**Must achieve 5 consecutive automated notifications** before declaring automation "fixed"
- Current status: 0/5 consecutive successes
- Manual tests confirm code works, need environment fix

### PLANNED SOLUTION 📋
**Move entire project out of ~/Documents/** to avoid macOS privacy restrictions
- Target location: `~/Development/owlgorithm/` 
- Update all file paths and configurations
- Validate automation works from new location
- Documents folder has special macOS protections that block launchd access

### COMPLETED WORK ✅
- **Phase 1A**: Core module extraction (615→335 lines, -45%)
- **Phase 1B**: Comprehensive testing infrastructure (29 tests, 99% coverage)
- **Phase 1C**: Automation diagnostics and logging infrastructure
- **Phase 3A**: Algorithm 1 unit counting implementation (36.8 lessons/unit average)
- **Refactoring**: All code successfully modularized and tested
- **Environment diagnosis**: Isolated macOS security as root cause

### ALGORITHM 1 SPECIFICATIONS 📋
**Critical Implementation Requirements:**
- **Hard-coded start date**: Exclude all data before 2025-06-19 (Nightmare unit start)
- **Exclude incomplete units**: On Sale (no reliable start), current active unit
- **Date range**: Only analyze data from first complete unit to last complete unit  
- **Target validation**: Requests = 34 lessons, Grooming+Reflexives = 39 lessons
- **Expected average**: ~35 lessons/unit from complete units only

### PHASE 1 ACHIEVEMENTS
- Extracted `metrics_calculator.py` and `markdown_updater.py` 
- Built comprehensive test suite with fixtures and mocks
- Fixed critical state reconciliation bugs through testing
- Created aggressive 30-min notification schedule for validation
- Simplified notifications to single useful template
- Comprehensive launchd diagnostic work completed

## Important Notes

- Requires active duome.eu profile (username must exist publicly)
- Uses Selenium for auto-refresh functionality
- No Duolingo credentials needed (scrapes public duome.eu data)
- Includes respectful delays and error handling for web scraping
- State management prevents duplicate notifications
- **AUTOMATION CURRENTLY BROKEN**: Use manual execution until migration complete