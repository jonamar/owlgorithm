# 🦉 Owlgorithm: Automated Duolingo Progress Tracker

**Complete automated progress tracking system for Duolingo with real-time analytics, simple reminders, and goal management.**

> 🎯 **Current Focus**: French course (272 units) with 18-month completion goal

## ✨ Key Features

- **📊 Accurate Progress Tracking**: Counts ALL learning activities (lessons, practice, stories, reviews)
- **🤖 Automated**: Scrape-on-demand, with a simple morning reminder window
- **📱 Simple Notifications**: Short Pushover reminders sent at fixed times (08:30–12:00)
- **📈 Goal Analytics**: Track pace, burn rate, and completion projections
- **🔒 Privacy-First**: All data stays local on your machine

## 🚀 Quick Start

**Prerequisites**: Python 3.8+, Firefox, geckodriver

```bash
git clone https://github.com/yourusername/owlgorithm.git
cd owlgorithm
python scripts/setup.py --all  # Interactive setup wizard
```

**📋 For complete setup instructions, see [Setup Guide](docs/setup.md)**

The setup guide includes:
- ✅ Platform-specific installation details
- ✅ Course configuration examples  
- ✅ Automation setup (cron/Task Scheduler)
- ✅ Troubleshooting common issues

## 📊 How It Works

1. **Scrapes** fresh data from duome.eu using headless Firefox
2. **Processes** lesson data with professional-grade algorithms
3. **Calculates** progress toward your completion goal
4. **Sends** simple morning reminders independent of scraping
5. **Updates** your progress dashboard

## 🔄 Dual-Mode Tracking System

Owlgorithm uses an intelligent dual-mode tracking system that adapts to Duolingo's course structure changes:

### Legacy Mode (Sections 1-4)
- **Variable lessons per unit** (~31 average)
- **Complex unit boundary detection** using session timing patterns
- **Historical accuracy** for completed sections

### Simplified Mode (Sections 5+)
- **Fixed 7 lessons per unit** (Duolingo's new structure)
- **Known unit counts** per section (255, 245, 180, 185)
- **Simple lesson counting** for accurate projections

### Why Dual-Mode?
Duolingo restructured their B1/B2 content (Sections 5-8) by splitting multi-lesson units into smaller single-lesson units. This 5x increase in unit count required a new tracking approach while preserving historical data integrity.

**Transition Point**: Lesson #89 (start of Section 5)
- **Before**: Complex tracking preserves accurate unit completion data
- **After**: Simplified tracking uses fixed ratios for reliable projections

## 📊 Versioning & Updates

Owlgorithm follows user-focused versioning:

- **New versions** are released when there's genuine value for users (new features, important fixes, easier setup)
- **Check CHANGELOG.md** for user-friendly release notes explaining what's new and why you'd want to update
- **Semantic versioning**: MAJOR.MINOR.PATCH based on impact to your workflow
- **No forced cadence**: Updates happen when they're worth your time, not on artificial schedules

**Current Version**: See [VERSION](VERSION) file and [CHANGELOG.md](CHANGELOG.md) for latest improvements.

## 📱 Notification Behavior

Notifications are intentionally simple and fixed-time:
- Sent at 08:30, every 30 minutes through 12:00 (08:30, 09:00, 09:30, 10:00, 10:30, 11:00, 11:30, 12:00)
- Content is a short reminder message (customize in `scripts/send_simple_notification.py`)

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