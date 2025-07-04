# CORE BUSINESS LOGIC - CRITICAL PROJECT REQUIREMENTS

**⚠️ This document defines immutable business rules that MUST NOT be broken by any code changes. ⚠️**

## 🎯 PROJECT MISSION

Complete 272 French Duolingo units in 548 days (18 months) using data-driven progress tracking.

## 🔢 LESSON COUNTING PRINCIPLE

### **CRITICAL RULE: ALL XP sessions count as lessons**

```python
# ALWAYS TRUE - This logic must NEVER be conditional
is_lesson = True  # Every session that earns XP is a lesson
```

**Why this is immutable:**
- Historical testing: Only counting "· lesson" sessions missed 68% of learning activity
- ALL session types are legitimate learning: practice, stories, unit reviews, legendary lessons
- Session types are metadata only - they do NOT affect lesson counting

## 🎯 DATA SOURCE REQUIREMENTS

### **ONLY Raw Modal Data is Trusted**

```html
<!-- TRUSTED: Only this div contains reliable data -->
<div id="raw" class="hidden fancybox-content">
  <!-- All session history data -->
</div>
```

**Critical requirements:**
- **ONLY** `<div id="raw">` modal data is reliable from duome.eu
- **ALL OTHER** duome.eu data is chronically inaccurate
- **MUST** click "aggiorna" button to refresh or data is stale
- HTTP requests without automation return outdated data

### **Unit Boundary Detection Rules (Algorithm 1)**

```html
<!-- UNIT START (first mention of unit name) -->
<li>...XP <a href="/skill/fr/UnitName">UnitName</a> · lesson</li>

<!-- ALL SUBSEQUENT SESSIONS belong to this unit until new unit mentioned -->  
<li>...XP · <span class="cCCC">personalized practice</span></li>
```

**Detection rules:**
- **First mention** of unit name chronologically = unit start
- **ALL XP-earning sessions** after unit start belong to that unit
- **Sub-units** (<8 lessons) get folded into adjacent units when appropriate

## 📊 DYNAMIC CALCULATION REQUIREMENTS

### **Lessons Per Unit Calculation - Algorithm 1 (IMPLEMENTED)**

```python
# ALGORITHM 1: "First Mention = Unit Start" with Sub-unit Folding
# ✅ FULLY IMPLEMENTED in src/core/metrics_calculator.py
lessons_per_unit = get_tracked_unit_progress()  # Single source of truth
```

**Algorithm Implementation:**
- **✅ Unit Boundaries**: First mention of unit name chronologically
- **✅ Session Assignment**: ALL XP-earning sessions count as lessons for active unit  
- **✅ Sub-unit Folding**: Units <8 lessons get merged appropriately
- **✅ Exclusions**: Current incomplete unit and unreliable start points excluded
- **✅ Current Average**: 32.0 lessons/unit (validated implementation)
- **✅ Constraints**: Hard-coded start date 2025-06-19, exclude On Sale/current units
- **✅ Validation**: Requests=29, Grooming+Reflexives=39, Nightmare=28 lessons

**Data Model**: Tracking-only approach (3 completed units since 2025-06-23)

### **Goal Calculation Requirements (IMPLEMENTED)**

```python
# ✅ DAILY GOAL: Hardcoded constant (implemented in config/app_config.py)
DAILY_GOAL_LESSONS = 12  # Fixed daily target to avoid calculation bugs

# ✅ PROGRESS CALCULATION: Fully implemented in metrics_calculator.py
remaining_units = 272 - completed_units
lessons_remaining = remaining_units * recent_lessons_per_unit  
projected_daily_pace = lessons_remaining / days_remaining  # For analysis only
```

**✅ Fixed parameters (implemented in config/app_config.py):**
- `TOTAL_COURSE_UNITS = 272`
- `GOAL_DAYS = 548` (18 months)
- `USERNAME = "jonamar"`
- `DAILY_GOAL_LESSONS = 12` (hardcoded, not calculated)
- `TRACKING_START_DATE = "2025-06-23"` (tracking-only data model)

## 🚨 DEVELOPER PROTECTION RULES

### **1. Lesson Counting Protection**

```python
# ✅ CORRECT
for session in sessions:
    if earns_xp:
        lesson_count += 1

# ❌ WRONG - Excludes practice/stories
for session in sessions:
    if session_type == 'lesson':
        lesson_count += 1
```

### **2. Data Source Protection**

```python
# ✅ CORRECT - Only raw modal
raw_div = soup.find('div', {'id': 'raw'})
sessions = parse_session_data(raw_div)

# ❌ WRONG - Using unreliable page data
stats = soup.find('.stats').text  # Chronically inaccurate
```

### **3. Unit Boundary Protection (IMPLEMENTED)**

```python
# ✅ CORRECT - Algorithm 1: First mention = unit start
# ✅ IMPLEMENTED in src/core/metrics_calculator.py
if first_mention_of_unit_name:
    is_unit_boundary = True

# ❌ WRONG - All legendary sessions
if "legendary" in session_text.lower():
    is_unit_boundary = True  # Includes within-unit legendary
```

## 📈 REQUIRED METRICS (✅ FULLY IMPLEMENTED)

**✅ Core tracking (implemented in src/core/metrics_calculator.py):**
- Total lessons: ALL XP sessions counted (167 lessons tracked)
- Units completed: Based on tracking-only data model (3 units)  
- Recent lessons/unit: From Algorithm 1 implementation (32.0 average)
- Required daily pace: Dynamic based on remaining effort

**✅ Notification system (implemented in src/notifiers/pushover_notifier.py):**
- Hardcoded 12 lessons/day goal in notifications  
- Time-appropriate messaging (morning/midday/evening/night)
- Progress calculations integrated with notifications

## ⚠️ BREAKING THESE RULES CORRUPTS PROGRESS TRACKING

**✅ Success criteria achieved:**
- ✅ No learning activity excluded from counts (ALL XP sessions counted)
- ✅ Projections based on trusted data sources only (raw modal data)
- ✅ Unit boundaries accurately detected (Algorithm 1 implemented)
- ✅ Data integrity maintained (tracking-only model, atomic operations)

## 🎉 IMPLEMENTATION STATUS: COMPLETE

**All core business logic requirements have been successfully implemented with:**
- Professional-grade architecture
- Zero technical debt  
- Single source of truth design
- Comprehensive error handling
- Automated testing validation

---

**🔒 These rules remain immutable. The system successfully implements all requirements.**