# Plan: Urgent Daily Goal Notification Fix

## 🚨 Problem Statement
Notifications show "completed X/1 lessons today" where "1" should be "12". This is breaking daily goal tracking and making notifications useless.

## 🎯 Objective
**Fix daily goal to show 12 lessons/day immediately** with minimal risk to existing automation.

## 📊 Root Cause
```json
// Current (Broken)
{
  "daily_goal_lessons": 1  // ← Wrong due to calculation mixing historical + tracking data
}

// Target (Fixed)
{
  "daily_goal_lessons": 12  // ← Hardcoded, no calculation
}
```

## 🗂️ Implementation Plan

### Phase 1: Emergency Notification Fix (Same Day)
**Objective**: Get "X/12 lessons today" working immediately

**Files to modify:**
- `src/core/metrics_calculator.py` - Add hardcoded constant
- `src/notifiers/pushover_notifier.py` - Use hardcoded goal  
- `src/core/daily_tracker.py` - Remove dynamic goal calculation

**Changes:**
```python
# In metrics_calculator.py
DAILY_GOAL_LESSONS = 12  # Hardcoded daily target (no calculation)

def calculate_daily_lesson_goal(state_data):
    """Return hardcoded daily goal - no dynamic calculation"""
    return DAILY_GOAL_LESSONS

# Remove all complex calculation logic
```

**Success Criteria:**
- [ ] Notifications show "X/12 lessons today"
- [ ] No "1 lesson/day" messages
- [ ] Existing automation continues working

### Phase 2: Basic Data Model Cleanup (Next Day)
**Objective**: Add constants for future use, no logic changes

**Files to modify:**
- `src/core/metrics_calculator.py` - Add tracking constants

**Changes:**
```python
# Add constants for clarity (used by future enhancements)
TRACKING_START_DATE = "2025-06-23"  # Official tracking began (Grooming unit start) 
TRACKED_COMPLETE_UNITS = ["Requests", "Grooming", "Protest"]  # 3 units since start
EXCLUDED_PARTIAL_UNITS = ["Nightmare"]  # Pre-tracking, partial data
TOTAL_COURSE_UNITS = 272  # Total units in French course
DAILY_GOAL_LESSONS = 12  # Hardcoded daily target
```

**Success Criteria:**
- [ ] Constants defined for future use
- [ ] No logic changes, no risk to existing functionality
- [ ] Documentation improved for next developers

### Phase 3: Documentation Update (Same Day as Phase 2)
**Objective**: Document the simplified approach

**Files to modify:**
- `CORE_BUSINESS_LOGIC.md` - Update daily goal section
- `CLAUDE.md` - Update current status

**Changes:**
1. **Document hardcoded daily goal approach**
2. **Remove references to dynamic goal calculation**
3. **Explain tracking-only unit model (for future reference)**

## 🔍 Implementation Order
1. **Hour 1**: Phase 1 (Emergency fix)
2. **Test**: Verify notifications work correctly  
3. **Hour 2**: Phase 2 (Constants) + Phase 3 (Documentation)

## ✅ Success Criteria

### Immediate Success
- [ ] Notifications show "X/12 lessons today" (not "X/1")
- [ ] Daily goal calculation no longer breaks
- [ ] Existing automation continues working unchanged

### Code Quality
- [ ] Clean constants defined for future use
- [ ] Documentation updated to match implementation
- [ ] No technical debt introduced

## 🚨 Risk Mitigation

**Risk**: Breaking existing notification automation
**Mitigation**: Minimal changes to notification logic, only change the goal calculation

**Risk**: State file corruption
**Mitigation**: No state file structure changes in Phase 1

**Risk**: Logic inconsistency
**Mitigation**: Use same hardcoded constant everywhere, no complex calculations

## 📋 Files Changed (Minimal Set)

### Phase 1 (Critical)
- `src/core/metrics_calculator.py` - Hardcode daily goal
- `src/notifiers/pushover_notifier.py` - Use hardcoded goal
- `src/core/daily_tracker.py` - Remove dynamic calculation

### Phase 2 & 3 (Low Risk)  
- `src/core/metrics_calculator.py` - Add constants for clarity
- `CORE_BUSINESS_LOGIC.md` - Document approach
- `CLAUDE.md` - Update status

**Total Impact**: 6 files, focused on immediate problem resolution with minimal risk.

## 🎯 Key Principle
**Fix first, optimize later.** Get notifications working correctly, then tackle broader improvements in a separate epic.