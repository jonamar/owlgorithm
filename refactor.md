# Duolingo Tracker Refactoring Plan

## **Current State Analysis**

**What the system does:**
- Scrapes Duolingo progress data from duome.eu
- Tracks French course completion progress  
- Updates a markdown file with analytics and projections
- Sends push notifications via Pushover
- Analyzes daily/weekly lesson patterns

**Key Issues Identified:**
1. **Broken file reference** - `daily_scheduler.py` references non-existent `duome_scraper.py`
2. **File organization** - Root directory cluttered with 16+ Python files
3. **Code duplication** - Files duplicated between root and archive/
4. **Configuration scattered** - Hardcoded values mixed with JSON config
5. **Complex scraping** - Over-engineered Selenium setup for simple data extraction
6. **No clear structure** - Mostly procedural scripts vs organized modules
7. **Inconsistent patterns** - Different error handling and return patterns

## **Refactoring Plan: Quick Wins for Low-Risk Implementation**

### **Phase 0: Critical Bug Fix (15 minutes)**

**Goal:** Fix broken file reference that prevents the system from working

**Issue Found:** `daily_scheduler.py` line 69 references `duome_scraper.py` which doesn't exist in the root directory (only in archive)

**Actions:**
1. **Fix broken reference in `daily_scheduler.py`:**
   ```python
   # Change line 69 from:
   "duome_scraper.py",
   # To:
   "duome_raw_scraper.py",
   ```

**Risk:** Very low - simple one-line fix

**Why do this first:** This ensures the system works before we start refactoring

### **Phase 1: File Organization (1-2 evenings)**

**Goal:** Clean up the project structure without changing functionality

**Actions:**
1. **Create proper directory structure:**
   ```
   owlgorithm/
   ├── src/
   │   ├── core/           # Main business logic
   │   ├── scrapers/       # Data collection
   │   ├── analyzers/      # Data analysis
   │   ├── notifiers/      # Push notifications
   │   └── utils/          # Shared utilities
   ├── config/             # Configuration files
   ├── data/               # Data storage
   ├── logs/               # Log files
   ├── scripts/            # Entry point scripts
   └── tests/              # Future tests
   ```

2. **Move files to appropriate directories:**
   - `pushover_notifier.py` → `src/notifiers/`
   - `duome_raw_scraper.py` → `src/scrapers/`
   - Analysis files → `src/analyzers/`
   - Entry points → `scripts/`

3. **Clean up archive:**
   - Remove duplicate files from archive/
   - Keep only truly archived versions with clear naming

**Risk:** Very low - just moving files and updating import paths

### **Phase 2: Configuration Centralization (1 evening)**

**Goal:** Centralize all configuration in one place

**Actions:**
1. **Create `config/app_config.py`:**
   ```python
   # Centralized configuration
   USERNAME = 'jonamar'
   TOTAL_UNITS_IN_COURSE = 272
   GOAL_DAYS = 548
   BASE_LESSONS_PER_UNIT = 31
   BASE_MINS_PER_LESSON = 7.5
   
   # File paths
   MARKDOWN_FILE = 'personal-math.md'
   STATE_FILE = 'tracker_state.json'
   DATA_DIR = 'data'
   
   # Directories
   LOG_DIR = 'logs'
   CONFIG_DIR = 'config'
   ```

2. **Update all files to import from central config**
3. **Move JSON configs to `config/` directory**

**Risk:** Low - simple search and replace operations

### **Phase 3: Entry Point Simplification (1 evening)**

**Goal:** Create clear, simple entry points

**Actions:**
1. **Create `scripts/daily_update.py`** - Single entry point for daily operations
2. **Create `scripts/setup.py`** - One-time setup script
3. **Create `scripts/analyze.py`** - On-demand analysis
4. **Consolidate duplicate main() functions**

**Examples:**
```python
# scripts/daily_update.py
#!/usr/bin/env python3
"""Single entry point for daily Duolingo tracking."""

def main():
    # Run scraper
    # Update markdown
    # Send notifications
    # All in one place

# scripts/setup.py  
#!/usr/bin/env python3
"""One-time setup for Duolingo tracker."""

def main():
    # Setup directories
    # Configure Pushover
    # Initialize state files
```

**Risk:** Low - mostly reorganizing existing code

### **Phase 4: Scraper Simplification (2 evenings)**

**Goal:** Simplify the over-engineered scraping logic

**Actions:**
1. **Create simple HTTP-first scraper:**
   ```python
   # Try simple requests first, fall back to Selenium only if needed
   def scrape_duome_data(username):
       # Try HTTP first (faster, more reliable)
       try:
           return scrape_with_requests(username)
       except Exception:
           # Fall back to Selenium only if needed
           return scrape_with_selenium(username)
   ```

2. **Extract browser setup into separate utility**
3. **Reduce complexity by removing rarely-used fallback browsers**
4. **Separate concerns:**
   - Data fetching
   - Data parsing  
   - Browser management

**Risk:** Medium - involves external dependencies, but has clear fallback

### **Phase 5: Basic Error Handling Standardization (1 evening)**

**Goal:** Consistent error handling patterns

**Actions:**
1. **Create `src/utils/exceptions.py`** with custom exceptions:
   ```python
   class DuolingoTrackerError(Exception): 
       """Base exception for Duolingo tracker."""
       pass
   
   class ScrapingError(DuolingoTrackerError): 
       """Raised when scraping fails."""
       pass
   
   class ConfigError(DuolingoTrackerError): 
       """Raised when configuration is invalid."""
       pass
   
   class DataError(DuolingoTrackerError):
       """Raised when data processing fails."""
       pass
   ```

2. **Standardize return patterns** - Either return data or raise exception (no more None returns)
3. **Add basic logging configuration in `src/utils/logging.py`**

**Risk:** Low - mostly adding, not changing existing logic

## **Implementation Priority**

**Start here** (highest impact, lowest risk):
0. **Phase 0** - Critical bug fix (do this first!)
1. **Phase 1** - File organization 
2. **Phase 2** - Configuration centralization
3. **Phase 3** - Entry point simplification

**Then continue with:**
4. **Phase 5** - Error handling
5. **Phase 4** - Scraper simplification

## **Detailed Implementation Steps**

### **Phase 0 Implementation:**

1. Open `daily_scheduler.py`
2. Find line 69 with the broken reference
3. Change `"duome_scraper.py",` to `"duome_raw_scraper.py",`
4. Save the file
5. Test that `daily_scheduler.py` runs without file not found errors

### **Phase 1 Implementation:**

1. Create new directory structure:
   ```bash
   mkdir -p src/{core,scrapers,analyzers,notifiers,utils}
   mkdir -p {config,data,logs,scripts,tests}
   ```

2. Move files systematically:
   ```bash
   # Move scrapers
   mv duome_raw_scraper.py src/scrapers/
   
   # Move notifiers  
   mv pushover_notifier.py src/notifiers/
   
   # Move main logic
   mv daily_tracker.py src/core/
   mv daily_scheduler.py src/core/
   
   # Move utilities
   mv setup_pushover.py scripts/
   ```

3. Update imports in each moved file
4. Test that everything still works

### **Phase 2 Implementation:**

1. Create `config/app_config.py` with all hardcoded values
2. Create `config/__init__.py` to make it a package
3. Update imports: `from config.app_config import USERNAME, TOTAL_UNITS_IN_COURSE`
4. Move JSON config files to `config/` directory
5. Update file paths in code

### **Phase 3 Implementation:**

1. Create main entry points in `scripts/`
2. Import and call existing functions
3. Remove old main() functions from moved modules
4. Update any cron jobs or automation to use new entry points

## **Benefits After Refactoring**

- **Maintainability:** Clear project structure and separation of concerns
- **Reliability:** Centralized config reduces hardcoded values and errors  
- **Debuggability:** Better error handling and logging
- **Extensibility:** Modular structure makes adding features easier
- **Testability:** Clear modules can be tested independently
- **Onboarding:** New contributors can understand the structure quickly

## **What NOT to Change (Keep Stable)**

- Core scraping logic (just reorganize it)
- Data formats and file structures
- External integrations (Pushover, markdown updates)
- Business logic and calculations
- The actual algorithms and data processing

## **Testing Strategy**

After each phase:
1. Run the daily update process manually
2. Verify markdown file gets updated correctly
3. Check that notifications still work
4. Confirm data files are created in expected locations

## **Migration Notes**

- Keep backups before each phase
- Test thoroughly before moving to next phase
- Update any external scripts or cron jobs that reference moved files
- Consider creating symlinks temporarily during transition if needed

## **Future Phases (Beyond Initial Refactoring)**

Once these quick wins are complete, consider:
- Adding proper unit tests
- Creating a proper CLI interface
- Adding configuration validation
- Implementing better data storage (SQLite?)
- Adding visualization capabilities
- Creating a simple web dashboard

---

## **Updated Status (December 2024)**

✅ **Plan Validated:** Recent codebase review confirms all issues remain and plan is still completely relevant

🔍 **New Issue Found:** Critical bug with broken file reference that prevents system from working - added as Phase 0

📅 **Timeline:** 5-7 evenings of focused work (plus 15 minutes for Phase 0)
**Risk Level:** Low to Medium  
**Impact:** High - Much more maintainable and extensible codebase

**Next Steps:** Start with Phase 0 to fix the broken reference, then proceed with the original plan. 