# Plan: Future Enhancements - Goal Tracking & Data Model Improvements

## 🎯 Objective
**After urgent fix is complete**, implement comprehensive goal tracking, burn rate analysis, and clean up data model architecture.

**Prerequisites**: `plan-urgent-fix.md` must be completed first.

## 📊 Enhanced Features

### Epic 1: Calculation Logic Unification
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

### Epic 2: 18-Month Goal Tracking & Burn Rate Analysis
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

### Epic 3: Clean Data Model Architecture
**Objective**: Remove historical data confusion permanently

**Data Model Restructure:**
```json
{
  "tracking_metadata": {
    "start_date": "2025-06-23",
    "tracked_complete_units": ["Requests", "Grooming", "Protest"],
    "excluded_partial_units": ["Nightmare"],
    "current_incomplete_unit": "Dining Out"
  },
  "daily_progress": {
    "lessons_completed": 9,
    "daily_goal": 12,  // Hardcoded from urgent fix
    "last_daily_reset": "2025-07-02"
  },
  "historical_reference": {
    "note": "89 units completed before tracking started (2025-06-23)",
    "total_course_progress": 93  // 89 + 1 + 3 (for reference only)
  }
}
```

### Epic 4: Advanced Analytics
**Objective**: Rich progress insights and trend analysis

**New Analytics:**
1. **Weekly/Monthly Trends**: Lesson completion patterns
2. **Velocity Analysis**: Acceleration/deceleration detection  
3. **Goal Adjustment Recommendations**: Dynamic goal suggestions based on performance
4. **Milestone Tracking**: Unit completion celebrations

## 🔍 Implementation Priority

### High Priority (Next Sprint)
1. **Epic 1**: Calculation Logic Unification 
   - Fixes consistency issues between notifications and markdown
   - Low risk, high value

### Medium Priority  
2. **Epic 2**: 18-Month Goal Tracking
   - Adds valuable progress insights
   - Builds on constants from urgent fix

### Lower Priority
3. **Epic 3**: Data Model Restructure
   - Architectural improvement  
   - Can be done incrementally

4. **Epic 4**: Advanced Analytics
   - Nice-to-have features
   - Requires stable foundation first

## ✅ Success Criteria

### Epic 1 Complete
- [ ] Notifications and personal-math.md show identical progress data
- [ ] Single source of truth for all calculations
- [ ] No logic duplication

### Epic 2 Complete  
- [ ] 18-month goal progress displayed in personal-math.md
- [ ] Burn rate analysis shows if on track for goal
- [ ] Historical vs required pace comparison

### Epic 3 Complete
- [ ] Clear separation of tracked vs historical data
- [ ] No more confusion about unit counts
- [ ] Clean, maintainable data model

### Epic 4 Complete
- [ ] Rich progress analytics and insights
- [ ] Trend analysis and predictions
- [ ] Goal optimization recommendations

## 🚨 Prerequisites

**MUST COMPLETE FIRST:**
- `plan-urgent-fix.md` - Daily goal notifications working correctly
- Verify urgent fix is stable and not breaking automation

**THEN PROCEED WITH:**
- Epic 1 (high value, low risk)
- Epic 2 (goal tracking)  
- Epic 3 & 4 as time permits

## 📋 Estimated Effort

- **Epic 1**: 2-3 days (calculation unification)
- **Epic 2**: 3-4 days (goal tracking + burn rate)  
- **Epic 3**: 2-3 days (data model cleanup)
- **Epic 4**: 4-5 days (advanced analytics)

**Total**: 11-15 days of development work

This represents significant enhancements but should only be undertaken after the urgent notification fix is proven stable.