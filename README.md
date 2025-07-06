# 🦉 Owlgorithm: Automated Duolingo Progress Tracker

**Complete automated progress tracking system for Duolingo with real-time analytics, smart notifications, and goal management.**

> 🎯 **Current Focus**: French course (272 units) with 18-month completion goal

## ✨ Key Features

- **📊 Accurate Progress Tracking**: Counts ALL learning activities (lessons, practice, stories, reviews)
- **🤖 Fully Automated**: Scrapes progress every 30 minutes with zero manual intervention
- **📱 Smart Notifications**: Time-appropriate push alerts via Pushover
- **📈 Goal Analytics**: Track pace, burn rate, and completion projections
- **🔒 Privacy-First**: All data stays local on your machine

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Firefox browser
- [geckodriver](https://github.com/mozilla/geckodriver/releases) (for browser automation)

### Installation
```bash
# 1. Clone and setup
git clone https://github.com/yourusername/owlgorithm.git
cd owlgorithm
python -m venv duolingo_env
source duolingo_env/bin/activate  # On Windows: duolingo_env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run setup wizard
python scripts/setup.py --all

# 4. Configure notifications (optional)
python scripts/setup_pushover.py

# 5. Test the system
python scripts/daily_update.py
```

### Automation Setup
```bash
# Set up automated tracking (every 30 minutes)
python scripts/setup_cron.py setup
```

That's it! Your system will now automatically track your progress and send notifications.

## 📊 How It Works

1. **Scrapes** fresh data from duome.eu using headless Firefox
2. **Processes** lesson data with professional-grade algorithms
3. **Calculates** progress toward your completion goal
4. **Notifies** you with smart, time-appropriate messages
5. **Updates** your progress dashboard automatically

## ⚙️ Configuration

Edit `config/app_config.py` to customize:

```python
# Your Duolingo username
USERNAME = "your_username"

# Course configuration
TOTAL_COURSE_UNITS = 272  # Adjust for your target language
GOAL_DAYS = 548          # 18 months = 548 days
DAILY_GOAL_LESSONS = 12  # Target lessons per day

# Notification settings
PUSHOVER_ENABLED = True
MORNING_START_HOUR = 6
EVENING_END_HOUR = 23
```

## 📈 Current Status

- **Architecture**: Complete with zero technical debt
- **Automation**: Fully functional cross-platform setup
- **Data Model**: Tracking-only approach (clean, reliable)
- **Notifications**: Time-based intelligent messaging
- **Goal Tracking**: Dynamic burn rate analysis

## 🏗️ Project Structure

```
owlgorithm/
├── 📁 config/           # Configuration files
├── 📁 docs/             # All documentation
├── 📁 scripts/          # Setup and automation scripts
├── 📁 src/              # Source code
│   ├── 📁 core/         # Business logic
│   ├── 📁 scrapers/     # Web scraping
│   ├── 📁 notifiers/    # Push notifications
│   └── 📁 utils/        # Shared utilities
├── 📁 tests/            # Test suite
├── 📄 README.md         # This file
├── 📄 requirements.txt  # Python dependencies
└── 📄 VERSION           # Current version
```

## 📚 Documentation

- **[📋 Documentation Index](docs/README.md)** - Overview of all documentation
- **[🚀 Setup Guide](docs/setup.md)** - Complete installation and configuration
- **[🚨 Core Business Logic](docs/core-business-logic.md)** - System rules and constraints
- **[🔧 Developer Guide](docs/claude.md)** - Development commands and workflow
- **[📝 Changelog](docs/changelog.md)** - Project history and version changes

## 🤝 Contributing

1. **Read First**: [Core Business Logic](docs/core-business-logic.md) contains immutable rules
2. **Follow Conventions**: Use [Conventional Commits](https://www.conventionalcommits.org/)
3. **Update Version**: Bump version in `VERSION` file for significant changes
4. **Test Changes**: Run `python scripts/daily_update.py` to verify functionality

### Commit Message Format
```bash
# Examples
feat: add ntfy notification backend support
fix: improve Firefox automation reliability  
docs: update setup guide with troubleshooting
chore: bump dependencies to latest versions
```

## 🎯 Philosophy

**Data-Driven Learning**: Objective progress tracking reveals patterns that intuition might miss.

**Automation First**: Set it and forget it. Consistency beats perfection.

**Privacy & Control**: Your data stays yours. No cloud dependencies, no accounts required.

**Gentle Motivation**: Facts over guilt. Actionable insights, not judgmental pressure.

## 📜 License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

---

*🎯 Complete your language learning goals with automated progress tracking and smart analytics.*