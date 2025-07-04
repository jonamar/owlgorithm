# 🦉 Owlgorithm: Automated Duolingo Progress Tracker

**Complete automated progress tracking system for Duolingo French course (272 units) with 18-month goal timeline, real-time analytics, and push notifications.**

## 🎯 What It Does

- **Accurate lesson counting**: ALL learning activities count (lessons, practice, stories, reviews, etc.)
- **Real-time progress tracking**: Automated scraping with browser automation every 30 minutes
- **Smart notifications**: Time-appropriate push alerts with progress updates
- **Burn rate analysis**: Track actual vs required pace toward 18-month goal
- **Professional architecture**: Zero technical debt, single source of truth design

## 🔄 How It Works

1. **Scrapes** fresh session data from duome.eu every 30 minutes (6am-midnight)
2. **Processes** data using tracking-only model (3 completed units since 2025-06-23)
3. **Calculates** progress toward 18-month goal with burn rate analysis
4. **Notifies** via Pushover with time-appropriate messages
5. **Updates** markdown progress report automatically

## 🚀 Quick Start

```bash
# Setup
python -m venv duolingo_env
source duolingo_env/bin/activate
pip install -r requirements.txt
python scripts/setup.py --all

# Configure notifications
python scripts/setup_pushover.py

# Manual run (automated via launchd)
python scripts/daily_update.py
```

## 📊 Current Status (Live Data)

- **167 lessons** completed (tracking period: 2025-06-23 to present)
- **3 units** completed (Requests, Nightmare, Grooming)
- **12 lessons/day** current pace (hardcoded daily goal)
- **179 units remaining** toward completion goal
- **32.0 lessons/unit** average (Algorithm 1 calculation)

## ⚙️ Configuration

**Key Parameters** (`config/app_config.py`):
```python
USERNAME = "jonamar"
TOTAL_COURSE_UNITS = 272
GOAL_DAYS = 548  # 18 months
DAILY_GOAL_LESSONS = 12  # Hardcoded daily target
TRACKING_START_DATE = "2025-06-23"
```

**Automated Schedule**: Every 30 minutes (6am-midnight) via macOS launchd

## 🏗️ Architecture

```
📁 owlgorithm/
├── 🔧 config/app_config.py          # Single source of truth
├── 📊 src/core/metrics_calculator.py # Centralized calculations  
├── 🛠️  src/utils/                    # Shared utilities
├── 🕷️  src/scrapers/                 # Headless browser automation
├── 📱 src/notifiers/                # Push notifications
└── 📈 personal-math.md              # Auto-updated progress
```

**Core Features:**
- **Headless scraping**: Firefox automation with error handling
- **State management**: Atomic operations with backup/recovery
- **Time-based notifications**: Morning goals, evening progress
- **Data validation**: Comprehensive error detection and handling

## 🎉 Project Status: COMPLETE

**✅ All planned work finished:**
- Phase 1: Fixed notification daily goal display
- Epic 1: Clean historical data model
- Epic 2: Unified calculation logic
- Epic 3: 18-month goal tracking with burn rate analysis
- Epic 5: Architecture consolidation
- Epic 6: Final deduplication (all 46 duplications eliminated)

**System provides complete automated tracking with zero technical debt.**

## 🚨 For Developers

**⚠️ CRITICAL**: Read [CORE_BUSINESS_LOGIC.md](CORE_BUSINESS_LOGIC.md) before making changes.

**Essential Rules**:
- ALL XP sessions count as lessons (no exceptions)
- Only raw modal data from duome.eu is trusted
- Tracking-only data model (excludes historical pre-2025-06-23)
- Hardcoded daily goal prevents calculation bugs

## 📚 Documentation

- **[CORE_BUSINESS_LOGIC.md](CORE_BUSINESS_LOGIC.md)**: Immutable business rules
- **[CLAUDE.md](CLAUDE.md)**: Development commands and project status
- **[plan.md](plan.md)**: Optional future enhancements

---

*🎯 Goal: Complete 272 French units in 548 days using fully automated progress tracking.*