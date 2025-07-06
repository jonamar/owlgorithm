# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Owlgorithm is a Python-based Duolingo progress tracker that scrapes data from duome.eu to provide accurate lesson tracking and progress analytics. It features automated notifications, detailed statistics computation, and scheduled tracking via cron jobs.

## Development Guidelines

### 📝 Conventional Commits & Semantic Versioning

This project uses **Conventional Commits** with **Semantic Versioning** for clear history and automatic changelog generation.

**IMPORTANT**: Each significant commit should increment the version in `VERSION` file according to semver rules.

#### Commit Format:
```bash
# Format: <type>(<scope>): <description>

# Examples with version increments:
feat: add cross-platform notification support     # → MINOR version bump (1.0.0 → 1.1.0)
feat(notifiers): implement ntfy backend          # → MINOR version bump
fix: resolve Firefox automation timeout issues   # → PATCH version bump (1.1.0 → 1.1.1)
fix(scraper): handle missing session data        # → PATCH version bump
docs: update README with philosophy section       # → PATCH version bump (documentation)
BREAKING CHANGE: migrate launchd to cron         # → MAJOR version bump (1.x.x → 2.0.0)
```

#### Version Bumping Rules:
- **MAJOR** (`X.0.0`): Breaking changes, API changes, config schema changes
- **MINOR** (`x.Y.0`): New features, enhancements, backward-compatible additions  
- **PATCH** (`x.y.Z`): Bug fixes, documentation, small improvements

#### Required Actions:
1. **Update VERSION file**: `echo "2.1.0" > VERSION`
2. **Update CHANGELOG.md**: Add entries under appropriate version section
3. **Commit with conventional format**: `chore: bump version to 2.1.0`

**Commit Types:**
- `feat`: New features or enhancements → **MINOR** bump
- `fix`: Bug fixes and error corrections → **PATCH** bump  
- `docs`: Documentation updates → **PATCH** bump
- `chore`: Maintenance, dependencies, config → **PATCH** bump
- `test`: Adding or updating tests → **PATCH** bump
- `refactor`: Code improvements without behavior changes → **PATCH** bump
- `perf`: Performance optimizations → **MINOR** bump
- `ci`: CI/CD pipeline changes → **PATCH** bump
- `BREAKING CHANGE`: Any breaking change → **MAJOR** bump

**Scopes (optional):**
- `core`: Core tracking logic
- `scrapers`: Web scraping functionality  
- `notifiers`: Notification systems
- `config`: Configuration management
- `setup`: Setup and installation
- `docs`: Documentation files

### 🏷️ Version Management Workflow

```bash
# 1. Make your changes
# 2. Determine version impact:
#    - Breaking change? → MAJOR (2.0.0 → 3.0.0)
#    - New feature? → MINOR (2.0.0 → 2.1.0)  
#    - Bug fix/docs? → PATCH (2.0.0 → 2.0.1)

# 3. Update version file
echo "2.1.0" > VERSION

# 4. Update CHANGELOG.md with changes
# 5. Commit with conventional format
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 2.1.0

- Add cross-platform automation support
- Implement progress file renaming
- Enhanced documentation and cleanup"

# 6. Test the changes thoroughly
python scripts/daily_update.py
```

## Key Commands

### Setup & Environment
```bash
# Install geckodriver (REQUIRED for browser automation)
brew install geckodriver  # macOS
sudo apt install geckodriver  # Linux

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
3. **Markdown updater** updates `progress-dashboard.md` with progress stats
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
- `progress-dashboard.md`: Markdown progress report (auto-updated)
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

### COMPLETED MAJOR WORK ✅ **PROJECT COMPLETE**
- ✅ **Daily Goal Fix**: Notifications now show "X/12 lessons today" correctly
- ✅ **Clean Data Model**: Tracking-only approach (3 units vs 86 historical confusion)
- ✅ **Calculation Unification**: Single source of truth for all progress calculations
- ✅ **18-Month Goal Tracking**: Comprehensive burn rate analysis and projections
- ✅ **Architecture Consolidation**: Centralized constants and eliminated ALL duplications
- ✅ **Environment Migration**: Successfully moved to ~/Development/owlgorithm
- ✅ **Epic 6 Complete**: All 46 duplications eliminated with ultra-conservative approach
- ✅ **Zero Technical Debt**: Professional-grade codebase with single source of truth

### PROJECT STATUS: FULLY COMPLETE 🎉
**All planned work has been successfully completed.** The system now provides complete, automated Duolingo progress tracking with professional-grade architecture and zero technical debt. See `plan.md` for optional future enhancements.

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