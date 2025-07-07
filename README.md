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
4. **Notifies** you with smart, time-appropriate messages
5. **Updates** your progress dashboard automatically

## 📊 Versioning & Updates

Owlgorithm follows user-focused versioning:

- **New versions** are released when there's genuine value for users (new features, important fixes, easier setup)
- **Check CHANGELOG.md** for user-friendly release notes explaining what's new and why you'd want to update
- **Semantic versioning**: MAJOR.MINOR.PATCH based on impact to your workflow
- **No forced cadence**: Updates happen when they're worth your time, not on artificial schedules

**Current Version**: See [VERSION](VERSION) file and [CHANGELOG.md](CHANGELOG.md) for latest improvements.

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