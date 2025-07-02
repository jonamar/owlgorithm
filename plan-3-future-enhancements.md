# Plan: Future Enhancements - Goal Tracking & Data Model Improvements

## 🎯 Objective
**After urgent fix is complete**, implement comprehensive goal tracking, burn rate analysis, and clean up data model architecture.

**Prerequisites**: `plan-urgent-fix.md` must be completed first.

## 📊 Enhanced Features

### Epic 1: Clean Historical Data (PRIORITY: HIGH)
**Objective**: Remove historical data confusion and establish clean tracking-only foundation

**Problem**: `total_completed_units: 86` mixes historical + tracking data, causing wrong progress calculations
**Solution**: Update to tracking-only unit count and fix affected calculations

**Audit Results**: Only 2 active files affected (manageable blast radius)
- `src/core/metrics_calculator.py` - projection calculations  
- `src/core/markdown_updater.py` - progress updates

**Files to modify:**
- `tracker_state.json` - Update `total_completed_units: 86 → 3` (tracking-only count)  
- `src/core/metrics_calculator.py` - Handle new unit count in projections
- `src/core/markdown_updater.py` - Handle new unit count in progress display

**Changes:**
```python
# Use tracking-only unit count (no historical data)
TRACKING_ONLY_COMPLETED_UNITS = 3  # Requests, Grooming, Protest
remaining_units = TOTAL_COURSE_UNITS - TRACKING_ONLY_COMPLETED_UNITS  # 272 - 3 = 269
```

### Epic 2: Calculation Logic Unification  
**Objective**: Single source of truth for all progress calculations

**Problem**: Currently notifications and personal-math.md use different calculation paths
**Solution**: Centralize all calculations in `metrics_calculator.py`

**Files to modify:**
- `src/core/metrics_calculator.py` - Centralize all unit calculations
- `src/core/markdown_updater.py` - Remove duplicate logic, use centralized functions
- `src/notifiers/pushover_notifier.py` - Use centralized calculations

**Changes:**
```python
# Single calculation functions used by both notifications and markdown
def get_tracked_unit_progress():
    """Return progress based on 3 tracked complete units only"""
    return {
        'completed_units': len(TRACKED_COMPLETE_UNITS),
        'total_lessons': get_lessons_since_tracking_start(),
        'lessons_per_unit': get_lessons_since_tracking_start() / len(TRACKED_COMPLETE_UNITS),
        'remaining_units': TOTAL_COURSE_UNITS - len(TRACKED_COMPLETE_UNITS)
    }
```

### Epic 3: 18-Month Goal Tracking & Burn Rate Analysis
**Objective**: Track progress against 18-month goal with performance analysis

**New Features:**

1. **Goal Timeline Tracking**:
   ```python
   # Based on TRACKING_START_DATE = "2025-06-23"
   goal_start_date = datetime(2025, 6, 23)
   goal_end_date = datetime(2026, 12, 23)  # 18 months later
   days_elapsed = (today - goal_start_date).days
   days_remaining = (goal_end_date - today).days
   completion_percentage = days_elapsed / (18 * 30) * 100
   ```

2. **Burn Rate Analysis**:
   ```python
   # Historical pace (actual performance since tracking started)
   actual_units_per_day = len(TRACKED_COMPLETE_UNITS) / days_elapsed
   actual_lessons_per_day = total_tracked_lessons / days_elapsed
   
   # Required pace (to meet 18-month goal)
   required_units_per_day = remaining_units / days_remaining
   required_lessons_per_day = (remaining_units * lessons_per_unit) / days_remaining
   
   # Pace comparison
   pace_status = "ON TRACK" if actual_units_per_day >= required_units_per_day else "BEHIND"
   pace_difference = actual_units_per_day - required_units_per_day
   ```

3. **Enhanced Progress Display**:
   ```markdown
   ### 18-Month Goal Progress (Started 2025-06-23)
   - **Goal End Date**: December 23, 2026
   - **Days Elapsed**: X of 540 days (Y% complete)
   - **Historical Pace**: X.X units/day, Y.Y lessons/day  
   - **Required Pace**: X.X units/day, Y.Y lessons/day
   - **Status**: ON TRACK / BEHIND by X.X units/day
   - **Projected Completion**: Month Year (X months early/late)
   ```

### Epic 4: Advanced Analytics
**Objective**: Rich progress insights and trend analysis

**New Analytics:**
1. **Weekly/Monthly Trends**: Lesson completion patterns
2. **Velocity Analysis**: Acceleration/deceleration detection  
3. **Goal Adjustment Recommendations**: Dynamic goal suggestions based on performance
4. **Milestone Tracking**: Unit completion celebrations

## 🔍 Implementation Priority (UPDATED)

### Highest Priority (Do First)  
1. **Epic 1**: Clean Historical Data
   - **Critical**: Fixes wrong progress calculations (86 vs 3 units)
   - **Low risk**: Only 2 files affected, manageable blast radius
   - **Foundation**: Required for all other work

### High Priority  
2. **Epic 2**: Calculation Logic Unification
   - Fixes consistency issues between notifications and markdown  
   - Single source of truth for calculations
   - Builds on clean data from Epic 1

### Medium Priority
3. **Epic 3**: 18-Month Goal Tracking & Burn Rate Analysis
   - Advanced goal tracking features
   - Valuable progress insights
   - Builds on unified calculations from Epic 2

### Lower Priority
4. **Epic 4**: Advanced Analytics
   - Nice-to-have features
   - Requires stable foundation from Epics 1-3

## ✅ Success Criteria

### Epic 1 Complete (Clean Historical Data)
- [x] `total_completed_units` updated from 86 to 3 (tracking-only)
- [x] personal-math.md shows correct "Completed Units: 3" 
- [x] Projection calculations use correct remaining units (269)
- [x] No historical data confusion

### Epic 2 Complete (Calculation Unification)
- [ ] Notifications and personal-math.md show identical progress data
- [ ] Single source of truth for all calculations
- [ ] No logic duplication

### Epic 3 Complete (Goal Tracking)
- [ ] 18-month goal progress displayed in personal-math.md
- [ ] Burn rate analysis shows if on track for goal
- [ ] Historical vs required pace comparison

### Epic 4 Complete
- [ ] Rich progress analytics and insights
- [ ] Trend analysis and predictions
- [ ] Goal optimization recommendations

## 🚨 Prerequisites

**MUST COMPLETE FIRST:**
- `plan-urgent-fix.md` - Daily goal notifications working correctly
- Verify urgent fix is stable and not breaking automation

**THEN PROCEED WITH:**
- Epic 1 (critical foundation, low risk)
- Epic 2 (calculation unification)  
- Epic 3 & 4 as time permits

## 📋 Estimated Effort (UPDATED)

- **Epic 1**: 30 minutes (clean historical data - small blast radius)
- **Epic 2**: 2-3 days (calculation unification)
- **Epic 3**: 3-4 days (goal tracking + burn rate)  
- **Epic 4**: 4-5 days (advanced analytics)

**Total**: 9-12 days of development work

This represents significant enhancements but should only be undertaken after the urgent notification fix is proven stable.