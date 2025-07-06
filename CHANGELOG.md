# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Updated documentation to emphasize conventional commits and semantic versioning
- Cleaned up outdated planning documents

## [2.1.0] - 2025-07-06

### Added
- Cross-platform automation support (cron-based scheduling)
- Enhanced setup utility with platform detection (`scripts/setup_cron.py`)
- Comprehensive status checking and automation management
- Progress dashboard file renaming for better UX
- Git history cleanup tools and privacy protection

### Changed
- **BREAKING**: Migrated from launchd to cron for cross-platform compatibility  
- **BREAKING**: Renamed progress file from `personal-math.md` to `progress-dashboard.md`
- Removed backward compatibility code for cleaner architecture
- Updated all file references to use new naming convention
- Enhanced error handling in scraper for edge cases (empty sessions)
- Improved cross-platform support for macOS, Linux, and WSL

### Removed
- Deprecated cron scheduling code from archive
- Personal data from git history using BFG Repo-Cleaner
- Archive directory containing development artifacts
- Outdated planning documents (PRD, action plans)
- Backward compatibility migration code

### Fixed
- IndexError in scraper when sessions list is empty
- Environment variable handling in cron automation
- Browser automation process pollution issues

### Documentation
- Added conventional commits guidelines to development workflow
- Enhanced SETUP.md with cross-platform automation instructions  
- Updated CLAUDE.md with current project status
- Created comprehensive troubleshooting guides

## [1.0.0] - 2025-01-07

### Added
- Complete automated Duolingo progress tracking system
- Cross-platform scheduling support (macOS, Linux, WSL)
- Pushover notification integration with time-based smart messaging
- Real-time progress analytics and burn rate analysis
- Headless browser automation with Firefox
- Professional architecture with zero technical debt
- Comprehensive error handling and logging
- Template-based configuration system for privacy
- Interactive setup wizard and automated deployment
- Markdown progress report generation
- State management with atomic operations and backup/recovery

### Features
- **Accurate lesson counting**: ALL learning activities count (lessons, practice, stories, reviews)
- **Smart notifications**: Time-appropriate push alerts with progress updates
- **Burn rate analysis**: Track actual vs required pace toward goals
- **Professional architecture**: Single source of truth design
- **Cross-platform automation**: Runs on macOS, Linux, and WSL
- **Privacy-first**: Local execution, no cloud dependencies
- **Template configuration**: Easy setup while maintaining privacy

### Documentation
- Comprehensive setup guide (SETUP.md)
- Core business logic documentation (CORE_BUSINESS_LOGIC.md)
- Developer commands and status (CLAUDE.md)
- Notification enhancement roadmap (NOTIFICATION_ENHANCEMENT_PRD.md) 