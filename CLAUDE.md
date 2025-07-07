# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Owlgorithm is a Python-based Duolingo progress tracker that scrapes data from duome.eu to provide accurate lesson tracking and progress analytics. It features automated notifications, detailed statistics computation, and scheduled tracking via cron jobs.

## 🤖 AI Agent Workflow Integration

### **Primary Directive: User Impact Focus**
When suggesting changes, commits, or version bumps, always ask:
> "Would a user of this project want to update to get these changes?"

If yes → proceed with version bump. If no → accumulate more changes.

## Development Guidelines

### 📝 Conventional Commits & User Impact Versioning

This project uses **Conventional Commits** with **Semantic Versioning** based on user impact thresholds.

#### **AI Agent Decision Tree for Version Bumps:**

1. **Check recent commits** since last version bump
2. **Identify user-facing changes** (ignore internal refactoring)
3. **Apply "Would I Update?" test**:
   - **Yes, definitely** → MINOR or MAJOR bump
   - **Yes, if easy** → PATCH bump
   - **Meh, not really** → Wait, accumulate more changes
4. **If versioning → Update VERSION + CHANGELOG.md with user benefits**

#### **Commit Format with Version Impact:**
```bash
# Examples with version implications:
feat: add email notification backend          # → MINOR (new feature)
feat(notifiers): implement retry logic        # → MINOR (enhancement)
fix: resolve session parsing crash            # → PATCH (bug fix)
fix(scraper): handle empty sessions gracefully # → PATCH (robustness)
docs: improve setup guide for M1 Macs        # → PATCH (user experience)
BREAKING: migrate from launchd to cron       # → MAJOR (breaking change)
```

#### **Version Bump Decision Framework:**
```bash
# ✅ DO version when accumulated changes include:
- Completed user-facing feature (any size)
- Fixed bug that impacts user experience
- Made setup/configuration easier
- Added documentation that changes workflow
- 3-5+ small improvements that add value
- About to start risky work (stabilize first)
- Any breaking change (immediate MAJOR)

# ❌ DON'T version for:
- Internal refactoring only
- Work-in-progress commits
- Dependency updates (unless user-visible)
- Code formatting/style changes
- Development-only bug fixes
```

#### **Changelog Writing for AI Agents:**
```markdown
# ✅ Good (user-focused):
### Added
- Email notifications as Pushover alternative - setup now works without Pushover account
- Dry-run mode for testing configuration changes safely

### Fixed
- Setup script now works correctly on M1 Macs - no more architecture errors
- Clearer error messages when geckodriver missing - easier troubleshooting

# ❌ Bad (implementation-focused):
### Added
- SMTP client class with TLS support and connection pooling
- --dry-run flag in ArgumentParser with validation logic

### Fixed
- subprocess.run architecture detection for ARM64 systems
- ImportError exception handling in dependency loading
```

### 🏷️ Version Management Workflow

```bash
# AI Agent Version Bump Process:

# 1. Assess accumulated changes since last version
git log --oneline $(git describe --tags --abbrev=0)..HEAD

# 2. Filter for user-facing changes (ignore internal refactoring)

# 3. Apply "Would I Update?" test - is there enough user value?

# 4. If YES, suggest version bump:
echo "2.2.0" > VERSION

# 5. Update CHANGELOG.md with user-focused benefits
vim CHANGELOG.md  # Add user impact, not implementation details

# 6. Commit with conventional format
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 2.2.0 - email notifications and M1 Mac support

### What's New for Users
- Email notifications: No longer requires Pushover account
- M1 Mac compatibility: Setup script now works perfectly on Apple Silicon
- Better error messages: Clearer guidance when things go wrong

These changes make Owlgorithm accessible to more users and easier to debug."

# 7. Test thoroughly before proceeding
python scripts/daily_update.py
```

**Version Bumping Rules:**
- **MAJOR** (`X.0.0`): Breaking changes, API changes, config schema changes
- **MINOR** (`x.Y.0`): New features, enhancements, backward-compatible additions  
- **PATCH** (`x.y.Z`): Bug fixes, documentation, small improvements

**Commit Types with Version Impact:**
- `feat` → **MINOR** bump (new feature)
- `fix` → **PATCH** bump (bug fix)  
- `docs` → **PATCH** bump (if improves user experience)
- `chore` → **PATCH** bump (if user-visible)
- `perf` → **MINOR** bump (user-visible improvement)
- `BREAKING CHANGE` → **MAJOR** bump (always)

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

### Deployment & Automation
```bash
# Check cron automation status
python scripts/setup_cron.py status

# Setup cross-platform automation
python scripts/setup_cron.py setup

# Test automation without scheduling
python scripts/setup_cron.py test

# View automation logs
tail -f logs/automation.log
```

## Architecture

### Core Components
- **Scrapers** (`src/scrapers/`): Web scraping with Selenium, auto-refresh duome.eu stats
- **Core Logic** (`src/core/`): Daily tracking orchestration and lesson computation
- **Notifiers** (`src/notifiers/`): Push notifications with time-based smart logic
- **Utils** (`src/utils/`): Shared utilities and configuration management

### Configuration
- **Central config**: `config/app_config.py` - Username, course metrics, file paths
- **Notification config**: `config/pushover_config.json` - API keys and settings
- **State tracking**: `tracker_state.json` - Persistent state for daily progress

### Data Flow
1. **Scraper** auto-refreshes duome.eu and extracts session data
2. **Core tracker** computes lesson metrics and progress calculations
3. **Markdown updater** updates `progress-dashboard.md` with progress stats
4. **Notifier** sends time-appropriate notifications (morning goals, evening progress, etc.)

### Key Features
- **Accurate lesson counting**: ALL XP-earning sessions count as lessons (no exceptions)
- **Enhanced notifications**: Dynamic progress insights with required pace, weekly averages, and projected finish dates
- **Cross-platform automation**: Cron-based scheduling (macOS, Linux, WSL)
- **Auto-refresh**: Clicks duome.eu update button before scraping
- **Headless browser automation**: Firefox with enhanced error handling
- **Template configuration**: Privacy-first setup with example configs

## File Structure

### Scripts
- `scripts/daily_update.py`: Main entry point for daily operations
- `scripts/setup.py`: One-time setup and dependency checking
- `scripts/setup_cron.py`: Cross-platform automation setup utility
- `scripts/analyze.py`: Data analysis utilities

### Data Files
- `data/duome_raw_USERNAME_TIMESTAMP.json`: Raw scraped session data
- `progress-dashboard.md`: Markdown progress report (auto-updated)
- `tracker_state.json`: Persistent state for daily tracking
- `logs/`: Execution logs and debugging output

### Configuration Notes
- Username and course settings in `config/app_config.py`
- Notification credentials in `config/pushover_config.json` (not committed)
- Automation schedule via cron (every 30 minutes, 6am-11:30pm + midnight)

## Dependencies

Core: Selenium, requests, beautifulsoup4, pandas
Browser: Firefox with geckodriver (auto-installed)
Environment: Python 3.7+, virtual environment recommended

## CURRENT PROJECT STATUS (July 2025) ✅

### SYSTEM FULLY OPERATIONAL 🎉
**All major issues resolved and system working perfectly:**
- ✅ **Automation**: Cron-based scheduling working reliably (every 30 minutes)
- ✅ **Notifications**: Correct daily goal display and time-appropriate messaging
- ✅ **Scraping**: Headless Firefox working reliably with auto-refresh
- ✅ **Data Processing**: Accurate lesson counting and progress tracking
- ✅ **Architecture**: Clean, maintainable codebase with single source of truth
- ✅ **Cross-platform**: Works on macOS, Linux, and WSL
- ✅ **Privacy**: Template configuration system for public use

### COMPLETED MAJOR WORK ✅ **PROJECT COMPLETE**
- ✅ **Version 2.1.0**: Cross-platform migration (launchd → cron)
- ✅ **Progress File Renaming**: personal-math.md → progress-dashboard.md  
- ✅ **Git History Cleanup**: Removed all personal data from repository history
- ✅ **Documentation**: Comprehensive setup guides and troubleshooting
- ✅ **Architecture**: Professional-grade codebase with zero technical debt
- ✅ **Conventional Commits**: Proper versioning and changelog practices

### PROJECT STATUS: PRODUCTION READY 🎉
**All planned work has been successfully completed.** The system provides complete, automated Duolingo progress tracking with professional-grade architecture, cross-platform support, and user-focused versioning practices.

## Important Notes

- Requires active duome.eu profile (username must exist publicly)
- Uses Selenium for auto-refresh functionality (runs headless by default)
- No Duolingo credentials needed (scrapes public duome.eu data)
- Includes respectful delays and error handling for web scraping
- State management prevents duplicate notifications
- **Daily goal**: Hardcoded to 12 lessons/day (prevents calculation bugs)
- **Automation status**: ✅ Working with cron-based cross-platform scheduling

## Development Principles for AI Agents

### **Quality Gates Before Version Bumps:**
- [ ] Can I explain why users would want this version in one sentence?
- [ ] Does the changelog read like "user benefits" not "code changes"?
- [ ] Are breaking changes clearly highlighted with migration notes?
- [ ] Has the system been tested end-to-end recently?

### **Commit Quality Standards:**
- [ ] Uses conventional commit format with clear scope
- [ ] Describes user impact, not just implementation details  
- [ ] Could be understood by someone who didn't write the code
- [ ] Is atomic (one logical change) and specific

### **User-Focused Development:**
- Always lead with user benefits when documenting changes
- Test changes thoroughly before suggesting version bumps
- Maintain backward compatibility unless there's compelling user benefit
- Write error messages and documentation for actual users, not developers

**Remember: If you think you should version bump, apply the "Would I Update?" test first. Only suggest version bumps when users would genuinely benefit from updating.** 

## Testing Requirements ⚠️ **MANDATORY FOR AI AGENTS**

### **Critical Testing Rules - MUST FOLLOW**

#### **When to Run Tests (MANDATORY):**
- ✅ **ALWAYS** run `make test-smoke` before ANY commit affecting `src/` or `scripts/`
- ✅ **ALWAYS** run tests before suggesting version bumps
- ✅ **NEVER** commit if tests fail - fix issues first
- ✅ **ALWAYS** report test results in commit messages

#### **Test Commands (Quick Reference):**
```bash
# MANDATORY before commits to src/ or scripts/
make test-smoke      # Essential smoke tests (< 30 seconds)

# Optional additional testing
make test-unit       # Unit tests only
make test-all        # Complete test suite
make coverage        # Tests with coverage report
```

#### **Failure Protocol:**
1. **If `make test-smoke` fails**: DO NOT proceed with commit
2. **Fix the issue first**, then re-run tests
3. **If you can't fix it**: Stop and inform the user of the issue
4. **Never commit broken code** - this protects the production pipeline

#### **What Smoke Tests Validate:**
- ✅ **Data processing pipeline**: Core calculations work correctly
- ✅ **Notification content**: No junk values like "undefined", "calculating...", "NaN"
- ✅ **Environment setup**: Critical imports and configuration access
- ✅ **File operations**: Basic I/O and error handling
- ✅ **Performance**: Tests complete in < 30 seconds

#### **Integration with Development Workflow:**

```bash
# EXAMPLE: Proper AI agent workflow
# 1. Make code changes
git add src/core/metrics_calculator.py

# 2. MANDATORY: Run smoke tests
make test-smoke
# ✅ Tests passed in 0.4s

# 3. Only then commit
git commit -m "fix(core): improve lesson counting accuracy

- Fixed edge case in daily lesson calculation
- Smoke tests: ✅ Passed (0.4s)
- No breaking changes"

# 4. Consider version bump if user-facing
echo "2.0.1" > VERSION
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 2.0.1 - lesson counting fix"
```

#### **AI Agent Testing Checklist:**
- [ ] Did I run `make test-smoke` before suggesting commits?
- [ ] Did tests pass completely (no failures, no errors)?
- [ ] Did I report test results in commit message?
- [ ] If tests failed, did I fix issues before proceeding?
- [ ] Am I testing ANY changes to `src/` or `scripts/` directories?

#### **Why These Tests Matter:**
- **Prevents silent failures**: User gets broken notifications with junk data
- **Catches calculation errors**: Ensures lesson counts and progress are accurate  
- **Validates integrations**: Components work together correctly
- **Protects production**: Real automation depends on code quality
- **Saves debugging time**: Issues caught before they reach users

### **Test File Locations:**
- `tests/integration/test_smoke.py` - Essential smoke tests
- `tests/unit/` - Unit tests for individual components
- `tests/fixtures/` - Realistic test data
- `Makefile` - Unified test interface

### **Remember:**
🚨 **Testing is not optional** - it's mandatory for maintaining system reliability. Users depend on the automated daily notifications working correctly. A failed test means a potential silent failure in production.

## Memories
- Changelog is in /docs/changelog.md