# Safe Migration Plan: Drag-and-Drop Method

**Goal**: Move entire owlgorithm project from Documents to avoid macOS security restrictions  
**Method**: User drag-and-drop to ensure complete file preservation and avoid duplication

## PRE-MIGRATION SAFETY CHECKS

### 1. Stop All Automation First
```bash
# CRITICAL: Disable launchd job to prevent conflicts during migration
launchctl bootout gui/$(id -u)/com.owlgorithm.duolingo
launchctl remove com.owlgorithm.duolingo 2>/dev/null || true
```

### 2. Commit Current State
```bash
cd ~/Documents/owlgorithm
git status  # Verify everything is committed
git log --oneline -5  # Note latest commit hash for verification
```

### 3. Identify All Project Dependencies
- **Main project**: `~/Documents/owlgorithm/` (entire folder)
- **Runner script**: `~/bin/owlgorithm-daily-runner`
- **LaunchAgent**: `~/Library/LaunchAgents/com.owlgorithm.duolingo.plist`
- **Virtual environment**: `~/Documents/owlgorithm/duolingo_env/` (included in main folder)

## MIGRATION STEPS

### Step 1: Create Target Location
```bash
sudo mkdir -p /usr/local/
sudo chown jonamar:staff /usr/local/
# Verify you can write to /usr/local/
touch /usr/local/test && rm /usr/local/test
```

### Step 2: User Drag-and-Drop
**USER ACTION REQUIRED:**
1. Open Finder
2. Navigate to `/Users/jonamar/Documents/`
3. Select the entire `owlgorithm` folder
4. Drag to `/usr/local/` 
5. **Choose "Move"** (not copy) when prompted
6. Verify folder now exists at `/usr/local/owlgorithm/`

### Step 3: Verify Complete Migration
```bash
# Verify git repo intact
cd /usr/local/owlgorithm
git status
git log --oneline -5  # Should match pre-migration hash

# Verify all files moved
ls -la /usr/local/owlgorithm/
ls -la /usr/local/owlgorithm/.git/
ls -la /usr/local/owlgorithm/duolingo_env/

# CRITICAL: Verify old location is EMPTY
ls -la ~/Documents/owlgorithm/ 2>/dev/null && echo "ERROR: Old folder still exists!" || echo "✅ Old folder removed"
```

## POST-MIGRATION UPDATES

### Step 4: Update Runner Script
```bash
# Update /Users/jonamar/bin/owlgorithm-daily-runner
# Change ALL instances of:
# '/Users/jonamar/Documents/owlgorithm' 
# TO:
# '/usr/local/owlgorithm'

# Also update sys.path.insert lines
sed -i.bak 's|/Users/jonamar/Documents/owlgorithm|/usr/local/owlgorithm|g' /Users/jonamar/bin/owlgorithm-daily-runner
```

### Step 5: Update LaunchAgent
```bash
# Update ~/Library/LaunchAgents/com.owlgorithm.duolingo.plist
# No path changes needed if using /tmp/ for logs
# But verify StandardErrorPath and StandardOutPath are accessible
```

### Step 6: Test New Location
```bash
# Test manual execution from new location
cd /usr/local/owlgorithm
python scripts/daily_update.py
# Should receive notification if successful

# Test runner script
/Users/jonamar/bin/owlgorithm-daily-runner
# Should receive notification if successful
```

## VALIDATION AND ACTIVATION

### Step 7: Reload Automation
```bash
# Load launchd job
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.owlgorithm.duolingo.plist

# Verify job loaded
launchctl print gui/$(id -u)/com.owlgorithm.duolingo | grep "state ="

# Schedule should resume at next 30-minute interval
```

### Step 8: Monitor First Automated Run
- Wait for next 30-minute interval (XX:00 or XX:30)
- Watch for notification
- Check logs in /tmp/ if configured
- Verify Firefox browser opens during automation

## DUPLICATION PREVENTION

### Critical Safeguards:
1. **MOVE, don't copy** - Ensures single instance
2. **Verify old location empty** - Prevents duplicate execution
3. **Single runner script** - Only one script calls the project
4. **Single launchd job** - Only one scheduled task

### If Duplication Detected:
```bash
# Emergency: Disable ALL automation
launchctl bootout gui/$(id -u)/com.owlgorithm.duolingo
pkill -f owlgorithm

# Verify only one project location exists
find /Users -name "daily_tracker.py" 2>/dev/null
find /usr -name "daily_tracker.py" 2>/dev/null
```

## SUCCESS CRITERIA

✅ **Migration Complete When:**
- Old location completely empty: `~/Documents/owlgorithm/` doesn't exist
- New location working: `/usr/local/owlgorithm/` fully functional
- Git repo intact: All commits and history preserved
- Manual execution works from new location
- Runner script works from new location
- **FIRST automated notification received** (breakthrough!)

✅ **Automation Fixed When:**
- 5 consecutive automated notifications work perfectly
- No "Operation not permitted" errors
- Firefox browser opens during automated runs
- Logs show successful execution

## ROLLBACK PLAN

If migration fails:
1. **Stop automation**: `launchctl bootout gui/$(id -u)/com.owlgorithm.duolingo`
2. **Move project back**: Drag `/usr/local/owlgorithm/` back to `~/Documents/`
3. **Restore runner script**: `mv /Users/jonamar/bin/owlgorithm-daily-runner.bak /Users/jonamar/bin/owlgorithm-daily-runner`
4. **Use manual execution** until resolved

## NEXT STEPS AFTER SUCCESS

Once 5 consecutive notifications work:
1. Reduce frequency back to 4x daily
2. Merge feature branch to main
3. Continue with Phase 2 of improvement roadmap
4. Update documentation with new paths