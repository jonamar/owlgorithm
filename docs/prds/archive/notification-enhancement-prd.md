# Notification Enhancement PRD (Updated July 2025)

**📋 STATUS: COMPLETED** (Date: 2025-07-06)  
**🎯 OUTCOME: Enhanced notification format successfully implemented and deployed**

---
*This PRD has been completed and archived for historical reference.*

## 🎯 **Objective**
Transform push notifications from static daily goal tracking to dynamic, motivating progress insights that help users optimize their learning pace and stay on track for their 18-month goal.

## 📊 **Current vs. Enhanced Format**

### **Current Format (as of July 2025)**
```
📊 Duolingo Update
Today: 8/12 lessons (67%)
Total Sessions: 179
Progress: 2 units (37.5 lessons/unit)
Pace: ✅ AHEAD by 4.2 lessons/day
Time: 13:39
```

### **Enhanced Format (Proposed)**
```
8 / 10.4 lessons (77%)
week avg: 11.6 per day
finish: Jul 21, 2026 (5.5 mo early)
```

## 💡 **Key Improvements**

### **1. Dynamic Required Pace ("B" Variable)**
- **Current**: Static 12 lessons/day hardcoded target in notification 
- **Enhanced**: Real-time calculation based on lessons remaining and time left
- **Formula**: `total_lessons_remaining / days_remaining` (already calculated in `get_tracked_unit_progress()`)
- **Current State**: Data exists as `required_lessons_per_day` but notifications use hardcoded 12
- **Benefit**: Creates a "pressure release valve" - doing extra lessons reduces future required pace
- **Motivation**: Users can "drive down" the required daily pace by getting ahead

### **2. Concrete Finish Date**
- **Current**: Vague "ahead of schedule" status
- **Enhanced**: Specific projected completion date with early/late context  
- **Format**: `finish: Jul 21, 2026 (5.5 mo early)`
- **Benefit**: Tangible target date + motivational context of being early/late

### **3. Simplified, Actionable Layout**
- **Current**: 4 lines with emojis and explanatory text
- **Enhanced**: 3 concise lines with essential data
- **Focus**: Facts over encouragement text
- **Benefit**: Quick scan for daily progress gut-check

## 🔧 **Technical Implementation Status**

### **Data Sources (✅ Already Available)**
All required calculations already exist in `src/core/metrics_calculator.py`:
- ✅ `get_tracked_unit_progress()` provides `required_lessons_per_day` 
- ✅ `calculate_performance_metrics()` provides 7-day averages (`recent_avg_sessions`)
- ✅ Projected completion date calculation already implemented (`projected_completion_date`)
- ✅ Early/late calculation available (`months_difference`)

### **Current Implementation**
The notification system (`src/notifiers/pushover_notifier.py`) currently uses:
- `send_simple_notification()` method with hardcoded 12 lesson goal
- Access to full state data and metrics via `get_tracked_unit_progress()`
- All required data available but not used in notification format

### **Calculation Details**

**Line 1: Today's Progress (✅ Simple Implementation)**
```python
# A / B lessons (C%)
today_lessons = state_data.get('daily_lessons_completed', 0)
progress = get_tracked_unit_progress(state_data)  # Already exists!
required_pace = progress['required_lessons_per_day']  # Dynamic!
percentage = (today_lessons / required_pace) * 100 if required_pace > 0 else 0
```

**Line 2: Weekly Average (✅ Already Available)**  
```python
# week avg: X per day
perf_metrics = calculate_performance_metrics(json_data)  # Already exists!
weekly_avg = perf_metrics['recent_avg_sessions']
```

**Line 3: Projected Finish (✅ Already Calculated)**
```python
# finish: DATE (X mo early/late)
progress = get_tracked_unit_progress(state_data)  # Already exists!
projected_date = progress['projected_completion_date']  # Already formatted!
months_diff = progress['months_difference']
early_late = 'early' if months_diff < 0 else 'late' if months_diff > 0 else 'on time'
```

## 📋 **Configuration Requirements**

### **Personal Setup (User)**
- **Goal End Date**: Static `2026-12-23` (18-month goal)
- **Uses existing**: `cfg.TRACKING_START_DATE`, `cfg.GOAL_DAYS`

### **Public Release (Configurable)**
- **Goal End Date**: User-configurable in `app_config.py`
- **Timeline**: Flexible goal duration (not just 18 months)

## 🧮 **Key Calculations**

### **Required Pace Updates Dynamically**
- Updates as lessons are completed and averages become more reliable
- Effect per day is minimal (averaged over remaining timeline)
- More lessons completed = lower future required pace = motivating

### **Lessons Remaining Calculation**
- Uses actual completed units and current average lessons/unit
- Updates as more units complete and average becomes more accurate
- Formula: `remaining_units × current_lessons_per_unit_average`

### **Days Remaining**
- Simple calculation: `(goal_end_date - today).days`
- No weekend/holiday complexity for now
- Can enhance later if needed

## 🎨 **Design Decisions**

### **Simplicity First**
- **Colors**: None (keep simple, no dynamic logic)
- **Emojis**: None (clean, fact-focused)
- **Length**: 3 lines maximum
- **Language**: Direct, no motivational fluff

### **Edge Cases**
- **Zero lessons**: Show `0 / 12 lessons (0%)` - clear and works out of box
- **Behind schedule**: Show `3 / 12 lessons (25%)` and `finish: Jan 15, 2027 (2.3 mo late)`
- **Exactly on pace**: Show `finish: Dec 23, 2026 (on time)`

## 📅 **Implementation Timeline**

### **Dependencies (Updated)**
- ✅ **Phase 2 completed**: Cross-platform cron scheduling successfully implemented (v2.1.0)
- ✅ **Architecture stable**: All major refactoring completed, no merge conflicts expected
- ✅ **Calculation infrastructure**: All required data sources available in current codebase

### **Recommended Approach (Updated)**
1. ✅ **System stable** - Ready to implement notification enhancement
2. **Create feature branch** from current main: `feature/notification-enhancement`
3. **Modify `send_simple_notification()`** to use existing `get_tracked_unit_progress()` data
4. **Replace hardcoded 12** with dynamic `required_lessons_per_day`
5. **Add weekly average** from `calculate_performance_metrics()`  
6. **Add finish date** from existing `projected_completion_date` + `months_difference`
7. **Update documentation** to explain notification philosophy
8. **Test thoroughly** with various scenarios (ahead/behind/on-track)
9. **Version bump** to v2.2.0 (user-facing feature enhancement)

### **README Documentation Task**
Add a "Notification Philosophy" section explaining:
- **Dynamic vs. Static Goals**: How required pace adjusts based on progress
- **Facts Over Encouragement**: Actionable data instead of motivational messages  
- **Pressure Release Valve**: Getting ahead reduces future daily requirements
- **Concrete Targets**: Real dates instead of vague "on track" status
- **3-Line Principle**: Scannable, essential information only

## 🧪 **Testing Scenarios**

### **Ahead of Schedule**
```
18 / 12 lessons (150%)
week avg: 14.6 per day  
finish: Jul 21, 2026 (5.5 mo early)
```

### **Behind Schedule** 
```
3 / 12 lessons (25%)
week avg: 8.2 per day
finish: Jan 15, 2027 (2.3 mo late)
```

### **Exactly On Track**
```
12 / 12 lessons (100%)
week avg: 12.0 per day
finish: Dec 23, 2026 (on time)
```

### **Zero Lessons Day**
```
0 / 12 lessons (0%)
week avg: 11.2 per day
finish: Jan 3, 2027 (1.8 mo late)
```

## 🎯 **Success Criteria (Updated Status)**
- ✅ **Data infrastructure ready**: All calculations exist in `metrics_calculator.py`
- ✅ **Architecture stable**: No refactoring conflicts expected  
- ✅ **Cross-platform support**: Works with current cron automation
- ⏳ **Dynamic required pace**: Daily target adjusts down as user gets ahead (ready to implement)
- ⏳ **Concrete finish date**: Specific date instead of vague "ahead of schedule" (ready to implement)
- ⏳ **Simplified format**: 3-line, scannable, fact-focused (ready to implement)
- ⏳ **Motivational mechanics**: Getting ahead reduces future pressure (ready to implement)
- ⏳ **Clean implementation**: Uses existing calculation infrastructure (ready to implement)

## 🚀 **Future Enhancements**
- **Time-based adjustments**: Exclude weekends/holidays from days remaining
- **Color coding**: Red/green for behind/ahead (if requested later)
- **Multiple goals**: Support different timeline configurations
- **Advanced averaging**: More sophisticated pace calculations
- **Streak integration**: Incorporate consecutive day achievements

## 📋 **Implementation Summary (July 2025)**

**Status: ✅ COMPLETED & DEPLOYED**
- ✅ Enhanced notification format fully implemented
- ✅ Single notification system (no legacy fallbacks)
- ✅ All tests updated and passing
- ✅ Real-world testing completed successfully

**Actual Effort:** 2 hours development + testing + documentation
**Impact:** ✅ Delivered - notifications now provide dynamic progress insights
**Risk:** ✅ Zero - uses existing, tested calculation infrastructure

**Final Implementation:**
- `send_enhanced_notification()` provides 3-line dynamic format
- `send_simple_notification()` routes to enhanced format (single system)
- Removed all legacy notification methods for cleaner codebase
- Graceful handling of missing state data with "calculating..." placeholders

**Example Enhanced Notification:**
```
8 / 10.4 lessons (76%)
week avg: 10.4 per day
finish: Aug 13, 2026 (4.8 mo early)
```

---

✅ **ENHANCEMENT COMPLETE**: This feature successfully transforms notifications from static encouragement to dynamic progress insights that help users optimize their learning pace and stay motivated through concrete, actionable data.