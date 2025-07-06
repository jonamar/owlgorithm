# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.2.0] - 2025-07-06

### Added
- Created comprehensive documentation index (`docs/README.md`)
- Organized project structure following FOSS best practices
- Added clear documentation navigation and standards

### Changed
- **BREAKING**: Moved all documentation files to `docs/` directory
- **BREAKING**: Renamed `CORE_BUSINESS_LOGIC.md` to `docs/core-business-logic.md`
- **BREAKING**: Renamed `CLAUDE.md` to `docs/claude.md`
- **BREAKING**: Renamed `SETUP.md` to `docs/setup.md`
- **BREAKING**: Renamed `CHANGELOG.md` to `docs/changelog.md`
- **BREAKING**: Renamed `NOTIFICATION_ENHANCEMENT_PRD.md` to `docs/notification-enhancement-prd.md`
- Moved `owlgorithm-backup.bundle` to `backups/` directory
- Significantly improved README.md for new user experience
- Updated all documentation references throughout the codebase
- Streamlined root directory to reduce noise and improve navigation

### Fixed
- Updated all file path references in source code and documentation
- Fixed documentation links in README.md and .cursorrules
- Ensured all automation and setup scripts work with new structure

### Documentation
- Complete restructuring of documentation for better organization
- New user-friendly README.md with clear quick start guide
- Comprehensive documentation index with navigation guidance
- Updated all cross-references to use new file locations

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