# Plan: Final Deduplication & Utility Consolidation (Epic 6)

## 🎯 Objective
Complete the deduplication effort by eliminating remaining scattered configuration, duplicate utility patterns, and hidden constants discovered in comprehensive audit.

## 📊 Audit Results Summary
**23 remaining duplication instances** found across the codebase:
- **15 High Priority**: Critical duplications affecting maintainability
- **8 Medium Priority**: Moderate impact scattered configuration
- **Low Priority**: Style/organization improvements

## 🚨 High Priority Issues (Phase 1)

### Issue 1: Date Constant Duplication
**Problem**: `TRACKING_START_DATE` in config but `ANALYSIS_START_DATE` in scraper
**Files**: 
- `config/app_config.py:15` - `TRACKING_START_DATE = "2025-06-23"`
- `src/scrapers/duome_raw_scraper.py:641` - `ANALYSIS_START_DATE = "2025-06-"`
**Fix**: Use `cfg.TRACKING_START_DATE` consistently

### Issue 2: User-Agent Header Duplication  
**Problem**: Identical browser headers defined twice
**Files**:
- `src/scrapers/duome_raw_scraper.py:390-395`
- `src/scrapers/http_fetcher.py:13-24`
**Fix**: Extract to shared constants in `src/utils/constants.py`

### Issue 3: URL Construction Repeated 4+ Times
**Problem**: `https://duome.eu/{username}` pattern built manually everywhere
**Files**:
- `src/scrapers/duome_raw_scraper.py:112,247,385`
- `src/scrapers/http_fetcher.py:31`
**Fix**: Create `build_duome_url(username)` utility function

### Issue 4: sys.path Manipulation in 9 Files
**Problem**: Every script has similar path setup code
**Files**: `scripts/`, `src/core/`, multiple locations
**Fix**: Create shared `setup_project_paths()` function

### Issue 5: Virtual Environment Path Hardcoded
**Problem**: `'duolingo_env/bin/python'` should be config constant
**Files**: `src/core/daily_tracker.py:104`
**Fix**: Move to config as `VENV_PYTHON_PATH`

## 📋 Medium Priority Issues (Phase 2)

### Issue 6: API URLs Hardcoded
**Problem**: `"https://api.pushover.net/1/messages.json"` hardcoded
**Files**: `src/notifiers/pushover_notifier.py:78`
**Fix**: Move to config as `PUSHOVER_API_URL`

### Issue 7: Timing Values Scattered
**Problem**: Sleep/timeout values hardcoded in multiple places
**Files**:
- `src/scrapers/duome_raw_scraper.py:130,319` - `time.sleep(12)`
- `src/scrapers/http_fetcher.py:26` - `REQUEST_TIMEOUT = 15`
**Fix**: Create timing constants section in config

### Issue 8: File Validation Duplication
**Problem**: Similar file existence checking patterns repeated
**Fix**: Create file validation utilities

## 🔧 Implementation Plan

### Phase 1: Critical Consolidation (2-3 hours)

#### Step 1.1: Create Utility Constants
```python
# src/utils/constants.py
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
DUOME_BASE_URL = "https://duome.eu"
DEFAULT_REQUEST_TIMEOUT = 15
DEFAULT_SCRAPE_DELAY = 12
```

#### Step 1.2: Create Path Utilities  
```python
# src/utils/path_utils.py
def setup_project_paths():
    """Standard project path setup for all scripts"""
    
def build_duome_url(username: str) -> str:
    """Build duome.eu profile URL"""
    
def get_data_file_path(filename: str) -> str:
    """Get full path to data file"""
```

#### Step 1.3: Update Config with Missing Constants
```python
# config/app_config.py additions
VENV_PYTHON_PATH: str = "duolingo_env/bin/python"
PUSHOVER_API_URL: str = "https://api.pushover.net/1/messages.json"
```

#### Step 1.4: Replace All Duplicated Usage
- Update scrapers to use shared constants
- Replace hardcoded paths with utility functions
- Remove duplicate sys.path manipulation

### Phase 2: Secondary Consolidation (1-2 hours)

#### Step 2.1: Extract Configuration Values
- Move timing constants to config
- Extract browser configuration settings
- Consolidate algorithm identifiers

#### Step 2.2: Create Validation Utilities
```python
# src/utils/validation.py
def ensure_file_exists(filepath: str) -> bool:
def ensure_directory_exists(dirpath: str) -> bool:
```

## ✅ Success Criteria

### Phase 1 Complete
- [ ] No duplicate User-Agent definitions
- [ ] Single `build_duome_url()` function used everywhere
- [ ] All scripts use `setup_project_paths()`
- [ ] No hardcoded date constants outside config
- [ ] Virtual environment path in config only

### Phase 2 Complete  
- [ ] All API URLs in config
- [ ] Timing values centralized in config
- [ ] File validation uses shared utilities
- [ ] No scattered configuration remaining

## 📊 Files to Modify

### Phase 1 (Critical)
- `config/app_config.py` - Add missing constants
- `src/utils/constants.py` - **NEW FILE** - Shared constants
- `src/utils/path_utils.py` - **NEW FILE** - Path utilities
- `src/scrapers/duome_raw_scraper.py` - Remove duplications
- `src/scrapers/http_fetcher.py` - Use shared constants
- `src/core/daily_tracker.py` - Use config for venv path
- `scripts/*.py` - Use shared path setup

### Phase 2 (Secondary)
- `src/utils/validation.py` - **NEW FILE** - Validation utilities
- `src/notifiers/pushover_notifier.py` - Use config for API URL
- Update timing usage across scraper files

## 🎯 Expected Results

**Before**: 23 duplication instances, scattered configuration
**After**: Single source of truth for ALL constants and utilities

**Impact**:
- **Maintainability**: Change URLs/timeouts in one place
- **Consistency**: Impossible to have conflicting values
- **Reliability**: Shared utilities reduce bugs
- **Clarity**: Clear separation of config vs code

## 📋 Estimated Effort
- **Phase 1**: 2-3 hours (high impact, critical fixes)
- **Phase 2**: 1-2 hours (cleanup and polish)
- **Total**: 3-5 hours

This represents the **final cleanup** to achieve a truly consolidated, maintainable codebase with zero duplication.