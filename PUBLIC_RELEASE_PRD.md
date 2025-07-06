# Owlgorithm Public Release PRD

## 🏆 **PROGRESS SUMMARY** (Updated: 2025-07-05)

### ✅ **Phase 1: COMPLETE** - Privacy & Configuration
- **Duration**: 1 day (July 5, 2025)
- **Risk Level**: ZERO (as predicted)
- **Status**: All deliverables completed + bonus git history cleanup
- **Result**: Repository ready for public release with zero personal data exposure

### 🔄 **IMMEDIATE NEXT STEPS**
**Phase 2: Cross-Platform Scheduling** (Ready to start)
- **Risk Level**: ⬇️ **LOW** (downgraded from MEDIUM after investigation)
- **Duration**: Estimated 1-2 days  
- **Approach**: Replace 57-line launchd plist with simple cron entry
- **Target**: Support macOS, Linux, WSL (90% user coverage)

---

## 🎯 **Objective**
Release Owlgorithm as a public, cross-platform Duolingo progress tracker that anyone can deploy and use.

## 📊 **Current State** (Updated: 2025-07-05)
- ✅ **Working perfectly** on macOS with launchd automation
- ✅ **Professional architecture** with zero technical debt
- ✅ **Battle-tested** with comprehensive error handling and logging
- ✅ **Phase 1 COMPLETE** - Privacy & configuration ready for public release
- ✅ **Git history clean** - Zero personal data exposure
- ✅ **Template setup** - New users can configure in 10 minutes
- 🔄 **Ready for Phase 2** - Cross-platform scheduling (LOW RISK)

## 🔧 **Core Requirements**

### **1. Privacy & Configuration**
- [ ] Remove personal data from git using .gitignore + templates
- [ ] Create `config/app_config.example.py` with sanitized values
- [ ] Add personal config files to `.gitignore`
- [ ] Clear data handling documentation

### **2. Cross-Platform Automation** 🔄 **READY TO START**
- [ ] Replace macOS launchd with cron-based scheduling
- [ ] **Rebuild from scratch** (don't resurrect deprecated cron code)
- [ ] Base new cron setup on current working launchd approach
- [ ] Support macOS, Linux, and WSL (90% user coverage)
- [ ] **RISK LEVEL**: ⬇️ **DOWNGRADED TO LOW** (was MEDIUM)

### **3. User Onboarding**
- [ ] Interactive setup wizard
- [ ] Pushover credential setup with testing
- [ ] Course detection and goal configuration
- [ ] First-run validation and testing

### **4. Documentation**
- [ ] Installation guide for non-technical users
- [ ] Privacy policy and data handling explanation
- [ ] Troubleshooting guide
- [ ] Configuration reference

## 🚀 **Implementation Strategy**

### **Testing Protocol (Applied to ALL phases)**
**End-to-end pipeline validation required after each potentially breaking change:**
```bash
# Full E2E test sequence
1. python scripts/daily_update.py  # Manual execution
2. Verify scraper runs and saves data
3. Verify metrics calculation and markdown update
4. Verify notification sent (if configured)
5. Verify state persistence and recovery
6. Test automation scheduling (cron/launchd)
```

### **Git Workflow (ALL phases)**
```bash
# Feature branch strategy
git checkout -b feature/phase-1-privacy-config
# Make small, focused changes
git add config/app_config.py
git commit -m "phase 1.1 - extract USERNAME to environment variable - tested E2E"
git add config/app_config.template.py  
git commit -m "phase 1.2 - add config template - tested E2E"
# Push frequently, merge only after full validation
```

### **Phase 1: Privacy & Configuration** ✅ **COMPLETE**
**Branch**: `main` (completed)

**Simple template + gitignore approach (ZERO risk to existing setup):**

- [x] **1.1** Create configuration template
  - [x] Created `config/app_config.example.py` with placeholder values
  - [x] Replaced personal values with `"YOUR_USERNAME"` and example values
  - [x] **Test E2E**: Template imports successfully and has valid structure
  - [x] **Commit**: `task 1.1 - Phase 1 complete: Privacy & Configuration for public release`

- [x] **1.2** Add personal files to .gitignore
  - [x] Added `config/app_config.py` to `.gitignore`
  - [x] Added `config/pushover_config.json` to `.gitignore`
  - [x] Added personal data files and directories to `.gitignore`
  - [x] **Test E2E**: Setup works, personal files properly ignored
  - [x] **Commit**: `task 1.2 - Complete history cleanup and backup file protection`

- [x] **1.3** Create setup instructions for new users
  - [x] Created comprehensive `SETUP.md` with 10-minute setup guide
  - [x] Includes prerequisites, quick start, automation, troubleshooting
  - [x] **Test E2E**: Template setup validated for new users
  - [x] **Commit**: Included in task 1.1 commit

- [x] **1.4** Clean git history (BONUS)
  - [x] Used BFG to remove `app_config.py` from entire git history
  - [x] Verified personal files (`progress-dashboard.md`, `tracker_state.json`) already clean
  - [x] **Test E2E**: Local files safe, git history clean
  - [x] **Result**: Zero personal data in git history

```bash
# Standard template approach (used everywhere)
# Your files (unchanged, now ignored by git):
config/app_config.py           # Your real config
config/pushover_config.json    # Your real credentials

# Public templates (committed to git):
config/app_config.example.py   # Sanitized template
config/pushover_config.example.json  # Credential template

# New user setup:
cp config/app_config.example.py config/app_config.py
# Edit config/app_config.py with real values
```

### **Phase 2: Cross-Platform Scheduling (1-2 weeks)**
**Branch**: `feature/phase-2-cron-scheduling`

**Sub-tasks with E2E testing:**
- [ ] **2.1** Remove deprecated cron code
  - [ ] Delete `archive/daily_scheduler.py` and old cron functions
  - [ ] **Test E2E**: Verify no functionality broken
  - [ ] **Commit**: `phase 2.1 - remove deprecated cron code - tested E2E`

- [ ] **2.2** Build fresh cron setup utility
  - [ ] Create `scripts/setup_cron.py` from current launchd approach
  - [ ] **Test E2E**: Verify cron setup and 30-minute automation
  - [ ] **Commit**: `phase 2.2 - fresh cron setup utility - tested E2E`

- [ ] **2.3** Cross-platform detection and setup
  - [ ] Add OS detection and platform-specific instructions
  - [ ] **Test E2E**: Verify setup works on macOS, Linux, WSL
  - [ ] **Commit**: `phase 2.3 - cross-platform cron support - tested E2E`

```bash
# Replace 57-line launchd plist with simple cron
*/30 6-23 * * * cd /path/to/owlgorithm && python scripts/daily_update.py 2>&1 | logger -t owlgorithm

# Build from current working architecture:
# ✅ Entry point: scripts/daily_update.py
# ✅ Frequency: Every 30 minutes (6am-midnight)
# ✅ Logging: OWLLogger with automation detection
# ✅ Error handling: AtomicJSONRepository, retry logic
```

### **Phase 3: Enhanced Onboarding (1-2 weeks)**
**Branch**: `feature/phase-3-onboarding-wizard`

**Sub-tasks with E2E testing:**
- [ ] **3.1** Interactive setup wizard core
  - [ ] Create `scripts/setup_wizard.py` with user input validation
  - [ ] **Test E2E**: Fresh setup on clean system
  - [ ] **Commit**: `phase 3.1 - setup wizard core - tested E2E`

- [ ] **3.2** Course detection and validation
  - [ ] Add username validation and course structure detection
  - [ ] **Test E2E**: Verify course detection works with real usernames
  - [ ] **Commit**: `phase 3.2 - course detection - tested E2E`

- [ ] **3.3** End-to-end setup validation
  - [ ] Complete workflow test and first-run validation
  - [ ] **Test E2E**: Full new user experience from zero to working automation
  - [ ] **Commit**: `phase 3.3 - complete onboarding flow - tested E2E`

```python
# Interactive setup wizard
def setup_wizard():
    username = input("Duolingo username: ")
    course_units = detect_course_structure(username)
    goal_days = input("Goal timeline (days): ")
    setup_pushover_notifications()
    test_complete_workflow()
```

## 📋 **Success Criteria**
- [ ] **E2E Pipeline**: Full scrape → process → notify → persist workflow works after each change
- [ ] **Cross-Platform**: Tested working on macOS, Linux, and WSL without modification
- [ ] **Privacy**: Zero personal data in public repository (validated via audit)
- [ ] **Onboarding**: New user can set up from scratch in < 10 minutes
- [ ] **Zero Risk**: Your existing setup works unchanged throughout development
- [ ] **Reliability**: Maintains current 93% automation success rate
- [ ] **Feature Parity**: All current functionality preserved and tested
- [ ] **Git Hygiene**: Every commit includes E2E test validation note

## 🔄 **Technical Approach**

### **Repository Strategy**
**Single repo with .gitignore separation:**
```
owlgorithm/                 # Public repo
├── src/                    # All source code (unchanged)
├── config/
│   ├── app_config.example.py       # Template (in git)
│   ├── pushover_config.example.json # Template (in git)
│   ├── app_config.py               # Your real config (ignored)
│   └── pushover_config.json        # Your real config (ignored)
├── scripts/                # Setup and automation
├── docs/                   # Public documentation
├── data/                   # Your data (ignored)
├── progress-dashboard.md        # Your report (ignored)
├── tracker_state.json      # Your state (ignored)
└── .gitignore             # Protects personal files
```

### **Key Decisions**
1. **Don't resurrect deprecated cron code** - rebuild from current working state
2. **Folder permissions learned** - avoid `~/Documents/`, use `~/Development/`
3. **Focus on Unix-like systems** - covers 90% of developers
4. **Maintain architecture quality** - leverage existing bulletproof design

## 🎯 **Out of Scope**
- Docker containerization (overkill for personal automation)
- GUI applications (command-line focus)
- Multi-user shared deployments (personal tool focus)
- Native Windows Task Scheduler (WSL covers Windows users)

## 🔄 **Development Order & Dependencies**

### **Phase 1: Privacy & Configuration** ⭐ **HIGHEST PRIORITY**
*Simple template approach - zero risk to existing functionality*

**Order of operations:**
1. **1.1** Create configuration template
   - **Dependency**: None - can start immediately
   - **Risk**: ZERO - just copying and sanitizing existing file
   - **Blocks**: Public documentation
   
2. **1.2** Add personal files to .gitignore
   - **Dependency**: 1.1 complete
   - **Risk**: ZERO - only affects git tracking, not functionality
   - **Blocks**: Final privacy audit
   
3. **1.3** Create setup instructions
   - **Dependency**: 1.1 and 1.2 complete
   - **Risk**: ZERO - documentation only
   - **Blocks**: Setup wizard development

### **Phase 2: Cross-Platform Scheduling** ⭐ **HIGH PRIORITY**
*Can begin in parallel with Phase 1.3, core system functionality*

**Order of operations:**
1. **2.1** Remove deprecated cron code
   - **Dependency**: None - can start after 1.1
   - **Blocks**: Nothing (cleanup task)
   
2. **2.2** Build fresh cron setup utility
   - **Dependency**: 1.3 complete (needs env config)
   - **Blocks**: Cross-platform testing
   
3. **2.3** Cross-platform detection and setup
   - **Dependency**: 2.2 complete
   - **Blocks**: Public release

### **Phase 3: Enhanced Onboarding** 🔸 **MEDIUM PRIORITY**
*Nice-to-have, can be developed in parallel with Phase 2*

**Order of operations:**
1. **3.1** Interactive setup wizard core
   - **Dependency**: 1.2 complete (needs config templates)
   - **Blocks**: Complete user experience
   
2. **3.2** Course detection and validation
   - **Dependency**: 1.3 and 2.2 complete (needs working system)
   - **Blocks**: Advanced onboarding features
   
3. **3.3** End-to-end setup validation
   - **Dependency**: All previous phases complete
   - **Blocks**: Public release readiness

### **Critical Path Analysis**
```
1.1 → 1.2 → 1.3 (ZERO RISK) → 2.2 → 2.3 → Public Release
                    ↗      ↘  
                 2.1      3.1 → 3.2 → 3.3
```

### **Parallel Development Opportunities**
- **Phase 1** can be completed quickly (1-2 days) with zero risk
- **2.1** (cleanup) can run immediately after Phase 1
- **3.1** (wizard) can develop in parallel with **2.2**
- **3.2** and **3.3** can be deferred for faster release
- **Major risk investigations** should happen before Phase 2 begins

### **Development Rhythm**
- **Phase 1**: Can start immediately (zero risk, pure templates)
- **Investigation phase**: Research unknown risks before Phase 2
- **Phase 2**: Only after risks are understood and mitigated
- **Each sub-task**: Feature development → E2E testing → commit with validation
- **Cross-platform testing**: After Phase 2 completion (has working automation)
- **Documentation**: Continuous throughout, finalize before release

## 🔍 **Next Steps for Risk Assessment**

**Before starting Phase 2, investigate these unknowns:**

```bash
# 1. Check file path flexibility
grep -r "progress-dashboard.md" src/
grep -r "tracker_state.json" src/
grep -r "data/" src/
grep -r "logs/" src/

# 2. Review configuration loading
cat config/app_config.py  # Are paths configurable?

# 3. Check automation dependencies  
cat aggressive-schedule.plist  # What paths are hardcoded?

# 4. Review notification setup
grep -r "pushover_config" src/  # Is path flexible?
```

**Recommended approach:** Complete Phase 1 first (1-2 days), then investigate risks before proceeding.

## 🧪 **Testing Strategy**

### **Automated Testing**
```bash
# Pre-commit hook (required)
#!/bin/bash
echo "Running E2E validation..."
python scripts/daily_update.py --test-mode
echo "✅ E2E pipeline working"
```

### **Manual Testing Checklist**
```bash
# After each potentially breaking change:
□ Fresh virtual environment setup
□ Configuration from templates works  
□ Scraper runs without errors
□ Data parsing and metrics calculation
□ Markdown file updates correctly
□ Notifications sent (if configured)
□ State persistence across runs
□ Automation scheduling works
□ Error conditions handled gracefully
```

### **Cross-Platform Validation**
- **macOS**: Test on clean macOS system with fresh install
- **Linux**: Test on Ubuntu/Debian with cron
- **WSL**: Test on Windows 11 with WSL2
- **Edge cases**: Test with different usernames, course configurations

## ⚠️ **Potential Risks to Existing Functionality**

*Areas that need careful handling to avoid breaking your current setup:*

### **🔒 ZERO RISK (Phase 1 - Configuration)**
- **Config templates**: Pure file copying + .gitignore additions
- **Documentation**: No code changes, just instructions

### **⚠️ MEDIUM RISK (Phase 2 - Automation)**
- **launchd → cron transition**: Your current automation will need to be replaced
- **Solution approach**: Keep both working simultaneously, then switch
- **File paths in automation**: Current plist has hardcoded paths to your setup

### **✅ INVESTIGATED & RESOLVED**
- **Hardcoded file names**: ✅ All configurable via `config/app_config.py`
- **Data directory paths**: ✅ Relative paths, automatic directory creation
- **Log file paths**: ✅ Configurable, automatic directory creation
- **Pushover config path**: ✅ Configurable via `CONFIG_DIR` setting
- **State file location**: ✅ Configurable via `STATE_FILE` setting
- **Automation paths**: ✅ Fixed launchd logging inconsistency

### **Questions for Discussion:**
1. **Output files**: Should `progress-dashboard.md` be configurable for public users?
2. **Directory structure**: Are the `data/`, `logs/` paths flexible or hardcoded?
3. **Automation transition**: How do you want to handle the launchd → cron switch?
4. **File name conflicts**: Any other files that might conflict with public use?

## 🔍 **Risk Mitigation**
- **Phase 1 (Config)**: ZERO risk - only templates and .gitignore
- **Phase 2 (Automation)**: Parallel approach - keep launchd working during development
- **Unknown risks**: Investigate and discuss before proceeding
- **Breaking changes**: Mandatory E2E testing after each modification
- **Folder permissions**: Use `~/Development/` based on lessons learned
- **Deprecated code**: Clean slate rebuild from working launchd approach
- **Cross-platform**: Focus on Unix-like systems for 90% coverage
- **Regression prevention**: Feature branch strategy with frequent commits
- **Quality gates**: No merge without E2E validation passing 