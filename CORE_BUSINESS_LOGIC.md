# CORE BUSINESS LOGIC - CRITICAL PROJECT REQUIREMENTS

**⚠️ WARNING: This document defines the core business logic that MUST NOT be broken by any refactoring or new features. ⚠️**

## 🎯 PROJECT MISSION

**Goal**: Complete the entire French Duolingo course (272 units) within 18 months using data-driven progress tracking.

## 🔢 CORE LESSON COUNTING PRINCIPLE

### **CRITICAL RULE: ALL XP-earning sessions count as lessons**

```python
# ALWAYS TRUE - This logic must NEVER be conditional
is_lesson = True  # Every session that earns XP is a lesson
```

**Why this matters:**
- Historical testing revealed 68% of learning activity was miscounted when only "· lesson" sessions were counted
- "Personalized practice", "story practice", "unit reviews", and "legendary" sessions are ALL legitimate learning activities
- The system must reflect actual learning effort, not arbitrary Duolingo categorization

### **Session Types are Metadata Only**
- Session types (`unit_lesson`, `personalized_practice`, `story_practice`, etc.) are for reporting/analysis
- Session types do NOT affect whether something counts as a lesson
- Even "unknown" session types count as lessons

## 🎯 CRITICAL DATA SOURCE REQUIREMENTS

### **ONLY Trust the Raw Modal Data**
```html
<!-- TRUSTED: Raw modal data from duome.eu -->
<div id="raw" class="hidden fancybox-content" style="display: inline-block;">
  <!-- This contains the ONLY reliable session history -->
</div>
```

**CRITICAL REQUIREMENTS:**
- **ONLY** the `<div id="raw">` modal data is reliable from duome.eu
- **ALL other** duome.eu displayed data is chronically inaccurate and must be ignored
- The raw modal **MUST** be refreshed via "aggiorna" button click or data is stale
- Browser automation with update button click is **REQUIRED** for fresh data

### **Unit Boundary Detection**
```html
<!-- Unit completion marker (unit boundary) -->
<li>2025-06-28 11:10:29 · 120XP  · <span class="cCCC">legendary / unit review</span></li>

<!-- NOT a unit boundary (legendary within unit) -->
<li>2025-06-27 07:24:35 · 90XP  · <span class="cCCC">legendary / story /practice</span></li>
```

**Unit Demarcation Rules:**
- **ONLY "unit review"** sessions mark unit boundaries (end of unit)
- **"legendary"** without "unit review" are regular lessons within a unit
- Count lessons between "unit review" markers to calculate lessons per unit
- Use recent unit boundary analysis for accurate lessons/unit averages

## 📊 DYNAMIC GOAL CALCULATION SYSTEM

### **A) Average Lessons Per Unit (Dynamic)**
```python
# Calculate from actual completion data
lessons_per_unit = total_lessons_completed / total_units_completed
```
- Updates automatically as more units are completed
- Accounts for actual difficulty/practice requirements per unit
- More accurate than static estimates

### **B) Total Estimated Lessons Remaining**
```python
remaining_units = 272 - completed_units  # 272 = total French course units
estimated_remaining_lessons = remaining_units * current_lessons_per_unit_average
```

### **C) Required Daily Lessons**
```python
days_remaining = 548 - days_elapsed  # 548 = 18 months
daily_goal = estimated_remaining_lessons / days_remaining
```
- Recalculates automatically based on current pace
- Accounts for actual performance vs estimates

### **D) Completion Projections**
```python
current_daily_average = total_lessons_completed / days_elapsed
projected_completion_days = total_estimated_lessons / current_daily_average
```

## 🏗️ CRITICAL CONFIG PARAMETERS

### **Fixed Parameters (Do Not Change)**
```python
TOTAL_UNITS_IN_COURSE = 272      # French course total
GOAL_DAYS = 548                  # 18 months = 548 days
USERNAME = "jonamar"             # Target user
```

### **Dynamic Parameters (Auto-calculated)**
```python
# These should be calculated from actual data, not hardcoded
lessons_per_unit = calculate_actual_lessons_per_unit()
daily_goal = calculate_dynamic_daily_goal()
completion_estimate = calculate_completion_projection()
```

## 🚨 DEVELOPER PROTECTION RULES

### **1. Lesson Counting Protection**
```python
# ✅ CORRECT - All sessions count
for session in sessions:
    if session_earns_xp:
        lesson_count += 1

# ❌ WRONG - Conditional counting
for session in sessions:
    if session['type'] == 'lesson':  # This excludes practice!
        lesson_count += 1
```

### **2. Projection Calculation Protection**
- Daily goals must be recalculated based on actual progress data
- Never use static estimates when dynamic data is available
- Always update projections when new lesson data is added

### **3. Data Integrity Protection**
- Never modify lesson counts without understanding retroactive impact
- All changes to lesson counting logic must include historical recalculation
- Progress tracking must maintain consistency across all components

## 📈 REQUIRED METRICS FOR TRACKING

### **Core Progress Metrics**
1. **Total lessons completed** (all session types)
2. **Units completed** (based on unit completion sessions)
3. **Current lessons per unit average** (dynamic calculation)
4. **Days elapsed since project start**
5. **Estimated lessons remaining**
6. **Required daily pace** (updated daily)
7. **Projected completion date** (based on current performance)

### **Performance Analysis Metrics**
1. **Daily lesson completion rate**
2. **Weekly lesson completion trends**
3. **Ahead/behind schedule status**
4. **Course difficulty progression** (lessons per unit over time)

## 🔧 IMPLEMENTATION REQUIREMENTS

### **Automatic Recalculation Triggers**
- When new lesson data is scraped
- When units are completed
- When lesson counting logic changes
- Daily goal reassessment

### **Historical Data Protection**
- Changes to lesson counting must trigger historical recalculation
- State files must be updated to reflect corrected counts
- Progress reports must show accurate historical data

### **Error Prevention**
- Unit tests must verify lesson counting logic
- Integration tests must verify projection calculations
- Any refactoring must validate against known lesson totals

## 🎯 SUCCESS CRITERIA

**The system succeeds when:**
1. All learning activity is accurately counted (no 68% undercounts)
2. Daily goals reflect realistic requirements based on actual data
3. Projections accurately predict course completion timeline
4. Progress tracking motivates consistent daily learning
5. The 18-month goal remains achievable with data-driven adjustments

**The system fails when:**
- Lesson counting excludes legitimate learning activities
- Daily goals become unrealistic due to poor projections
- Historical data becomes inconsistent
- Progress tracking demotivates due to inaccurate metrics

---

**🔒 This document defines immutable business requirements. Any code changes that conflict with these principles must be rejected.**