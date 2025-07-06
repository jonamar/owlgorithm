# Notification Enhancement PRD

## 🎯 **Objective**
Transform push notifications from static daily goal tracking to dynamic, motivating progress insights that help users optimize their learning pace and stay on track for their 18-month goal.

## 📊 **Current vs. Enhanced Format**

### **Current Format**
```
🎯 Daily Goal Progress
✅ 10 lessons completed (83% of 12 lesson goal)
📈 Weekly average: 14.6 lessons/day
🔥 Keep it up! You're ahead of schedule.
```

### **Enhanced Format**
```
15 / 12 lessons (125%)
week avg: 14.6 per day
finish: Jul 21, 2026 (5.5 mo early)
```

## 💡 **Key Improvements**

### **1. Dynamic Required Pace ("B" Variable)**
- **Current**: Static 12 lessons/day hardcoded target
- **Enhanced**: Real-time calculation based on lessons remaining and time left
- **Formula**: `total_lessons_remaining / days_remaining`
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

## 🔧 **Technical Implementation**

### **Data Sources**
All required calculations already exist in `src/core/metrics_calculator.py`:
- `get_tracked_unit_progress()` provides `required_lessons_per_day`
- `calculate_performance_metrics()` provides 7-day averages
- Projected completion date calculation already implemented

### **Calculation Details**

**Line 1: Today's Progress**
```python
# A / B lessons (C%)
today_lessons = state_data.get('daily_lessons_completed', 0)
required_pace = total_lessons_remaining / days_remaining  # Dynamic!
percentage = (today_lessons / required_pace) * 100
```

**Line 2: Weekly Average**
```python
# week avg: X per day
weekly_avg = calculate_performance_metrics(json_data)['recent_avg_sessions']
```

**Line 3: Projected Finish**
```python
# finish: DATE (X mo early/late)
projected_date = today + timedelta(days=lessons_remaining / current_pace)
months_difference = (projected_date - goal_end_date).days / 30.44
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

### **Dependencies**
- **Wait for Phase 2 completion**: Cross-platform scheduling branch (`feature/phase-2-cross-platform-scheduling`) is actively working on notification systems
- **Avoid merge conflicts**: Notification improvements safer after Phase 2 automation changes are stable

### **Recommended Approach**
1. **Phase 2 completes** (appears close based on commit history)
2. **Create feature branch** from updated main: `feature/notification-enhancement`
3. **Implement enhancement** using existing `metrics_calculator.py` functions
4. **Update README** to explain notification ethos and philosophy
5. **Test thoroughly** with various scenarios (ahead/behind/on-track)
6. **Deploy** with standard E2E validation

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

## 🎯 **Success Criteria**
- [x] **Dynamic required pace**: Daily target adjusts down as user gets ahead
- [x] **Concrete finish date**: Specific date instead of vague "ahead of schedule"
- [x] **Simplified format**: 3-line, scannable, fact-focused
- [x] **Motivational mechanics**: Getting ahead reduces future pressure
- [x] **Accurate projections**: Updates as course averages become more reliable
- [x] **Clean implementation**: Uses existing calculation infrastructure

## 🚀 **Future Enhancements**
- **Time-based adjustments**: Exclude weekends/holidays from days remaining
- **Color coding**: Red/green for behind/ahead (if requested later)
- **Multiple goals**: Support different timeline configurations
- **Advanced averaging**: More sophisticated pace calculations
- **Streak integration**: Incorporate consecutive day achievements

---

**This enhancement transforms notifications from static encouragement to dynamic progress insights that help users optimize their learning pace and stay motivated through concrete, actionable data.**