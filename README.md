# 🦉 Owlgorithm: Data-Driven Duolingo Course Completion Tracker

**Complete the French Duolingo course (272 units) in 18 months using accurate progress tracking and dynamic goal calculation.**

## 🎯 What It Does

- **Accurate lesson counting**: ALL learning activities count (practice, stories, reviews, etc.)
- **Dynamic projections**: Real-time calculation of required daily pace based on actual performance
- **Fresh data**: Browser automation ensures up-to-date progress from duome.eu
- **Smart goals**: Adjusts completion estimates as you progress through units

## 🔄 How It Works

1. **Scrapes** fresh session data from duome.eu (with automatic page refresh)
2. **Analyzes** unit boundaries using completion markers to calculate lessons-per-unit
3. **Projects** remaining effort: 186 units × 19.0 lessons/unit = realistic daily goals
4. **Tracks** progress toward 18-month target with data-driven adjustments

## 🚀 Quick Start

```bash
# Setup
python -m venv duolingo_env
source duolingo_env/bin/activate
pip install -r requirements.txt
python scripts/setup.py --all

# Daily usage (automated via launchd)
python scripts/daily_update.py
```

## 📊 Current Status

- **179 lessons** completed (accurate count of all learning activity)
- **86 units** completed out of 272 total (31.6% progress)
- **19.0 lessons/unit** average (based on recent unit boundary analysis)
- **6 lessons/day** required pace (achievable goal)

## ⚙️ Configuration

**Key Parameters** (`config/app_config.py`):
```python
USERNAME = "jonamar"
TOTAL_UNITS_IN_COURSE = 272
GOAL_DAYS = 548  # 18 months
```

**Automated Schedule**: 4x daily via launchd (6am, 12pm, 5pm, 10pm)

## 🏗️ Architecture

- **Scrapers**: Browser automation for fresh data collection
- **Core Logic**: Progress calculation and goal management  
- **Notifiers**: Daily progress alerts via Pushover
- **Data Layer**: Atomic operations with corruption recovery

## 🚨 For Developers

**⚠️ CRITICAL**: Read [CORE_BUSINESS_LOGIC.md](CORE_BUSINESS_LOGIC.md) before making changes.

**Essential Rules**:
- ALL XP sessions count as lessons (no exceptions)
- Only raw modal data from duome.eu is trusted
- Unit boundaries detected via "unit review" markers only
- Dynamic calculations must use recent unit analysis

## 📚 Documentation

- **[CORE_BUSINESS_LOGIC.md](CORE_BUSINESS_LOGIC.md)**: Critical developer requirements
- **[CLAUDE.md](CLAUDE.md)**: Development commands and guidance
- **[IMPROVEMENT_ROADMAP.md](IMPROVEMENT_ROADMAP.md)**: Technical roadmap

---

*Goal: Complete 272 French units in 548 days using data-driven progress tracking.*