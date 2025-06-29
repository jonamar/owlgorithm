# Project Migration Checklist

**Migrating from**: `~/Documents/owlgorithm/`  
**Migrating to**: `~/Development/owlgorithm/`  
**Reason**: Bypass macOS security restrictions blocking launchd automation

## Pre-Migration Status
- ✅ Phase 1 refactoring complete (615→335 lines, -45%)
- ✅ Comprehensive test suite (29 tests, 99% coverage)
- ✅ Manual execution works perfectly
- ❌ Automation blocked by macOS Documents folder security
- **Goal**: 5 consecutive automated notifications

## Migration Steps

### 1. Target Location Ready
```bash
# Development folder already created by user
ls -la ~/Development/
```

### 2. Drag-and-Drop Migration
```bash
# User drags ~/Documents/owlgorithm/ to ~/Development/
# Choose "Move" when prompted to avoid duplication
```

### 3. Update File Paths

**Files requiring path updates:**
- `/Users/jonamar/bin/owlgorithm-daily-runner` (Python paths)
- `config/app_config.py` (if using absolute paths)
- `~/Library/LaunchAgents/com.owlgorithm.duolingo.plist` (log paths)

**Path Changes:**
- `/Users/jonamar/Documents/owlgorithm/` → `/Users/jonamar/Development/owlgorithm/`

### 4. Update Runner Script
```bash
# Edit /Users/jonamar/bin/owlgorithm-daily-runner
# Change all instances of:
# '/Users/jonamar/Documents/owlgorithm' 
# TO:
# '/Users/jonamar/Development/owlgorithm'
```

### 5. Update LaunchAgent
```bash
# Edit ~/Library/LaunchAgents/com.owlgorithm.duolingo.plist
# Update StandardErrorPath and StandardOutPath to accessible locations
# Test that current script paths are correct
```

### 6. Test Migration
```bash
# Test manual execution from new location
cd ~/Development/owlgorithm
python scripts/daily_update.py

# Test runner script
/Users/jonamar/bin/owlgorithm-daily-runner

# Reload launchd job
launchctl bootout gui/$(id -u)/com.owlgorithm.duolingo
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.owlgorithm.duolingo.plist
```

### 7. Validation
- [ ] Manual execution works from new location
- [ ] Runner script works from new location  
- [ ] LaunchAgent job loads without errors
- [ ] First automated notification received
- [ ] 5 consecutive automated notifications achieved

## Post-Migration
- Update any documentation referencing old paths
- Remove old Documents folder copy (after validation)
- Update CLAUDE.md with new location
- Continue with Phase 2 of improvement roadmap

## Rollback Plan
If migration fails:
1. Restore ~/Library/LaunchAgents/com.owlgorithm.duolingo.plist from git
2. Reset /Users/jonamar/bin/owlgorithm-daily-runner paths
3. Use manual execution until resolved

## Success Criteria
**AUTOMATION FIXED**: 5 consecutive automated notifications working perfectly
- Notification 1: ⏳ Pending
- Notification 2: ⏳ Pending  
- Notification 3: ⏳ Pending
- Notification 4: ⏳ Pending
- Notification 5: ⏳ Pending

**When achieved**: Reduce notification frequency back to 4x daily, merge to main branch