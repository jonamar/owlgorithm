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

### **Lessons Per Unit Calculation - Algorithm 1**

```python
# ALGORITHM 1: "First Mention = Unit Start" with Sub-unit Folding
# 1. Detect unit boundaries: First mention of unit name = unit start
# 2. Assign ALL XP sessions to currently active unit (including practice)
# 3. Fold small units (<8 lessons) into adjacent units when appropriate
lessons_per_unit = calculate_using_first_mention_algorithm(recent_sessions)

# NOT unit review markers (too complex/unreliable)
# NOT static estimates or total_lessons / total_units mixing timeframes
```

**Algorithm Requirements:**
- **Unit Boundaries**: First mention of unit name chronologically
- **Session Assignment**: ALL XP-earning sessions count as lessons for active unit
- **Sub-unit Folding**: Units <8 lessons adjacent to same unit get merged
- **Exclusions**: Skip current incomplete unit and units without reliable start points
- **Target Average**: ~37 lessons/unit (validated: 36.8 from production data)

### **Goal Calculation Chain**

```python
remaining_units = 272 - completed_units
lessons_remaining = remaining_units * recent_lessons_per_unit  
daily_goal = lessons_remaining / days_remaining
```

**Fixed parameters:**
- `TOTAL_UNITS_IN_COURSE = 272`
- `GOAL_DAYS = 548` (18 months)
- `USERNAME = "jonamar"`

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

### **3. Unit Boundary Protection**

```python
# ✅ CORRECT - Only unit review markers
if "unit review" in session_text.lower():
    is_unit_boundary = True

# ❌ WRONG - All legendary sessions
if "legendary" in session_text.lower():
    is_unit_boundary = True  # Includes within-unit legendary
```

## 📈 REQUIRED METRICS

**Core tracking:**
- Total lessons: ALL XP sessions counted
- Units completed: Based on unit review boundaries  
- Recent lessons/unit: From unit boundary analysis
- Required daily pace: Dynamic based on remaining effort

**Notification separation:**
- Hardcoded 15 lessons/day goal in notifications (preserved)
- Dynamic calculations for progress reports only

## ⚠️ BREAKING THESE RULES CORRUPTS PROGRESS TRACKING

**Success criteria:**
- No learning activity excluded from counts
- Projections based on trusted data sources only  
- Unit boundaries accurately detected
- Historical data integrity maintained

---

**🔒 These rules are immutable. Any code changes that conflict with these principles must be rejected.**