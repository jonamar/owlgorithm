# 🦉 Owlgorithm: Data-Driven Duolingo Course Completion Tracker

**A sophisticated progress tracking system for completing the entire French Duolingo course (272 units) within 18 months using dynamic goal calculation and accurate lesson counting.**

## 🎯 Project Mission

Complete the French Duolingo course in **18 months** (548 days) using data-driven progress tracking that:
- Accurately counts ALL learning activities (not just "lessons")
- Dynamically adjusts daily goals based on actual performance
- Provides realistic completion projections
- Tracks actual lessons-per-unit averages (varies by difficulty)

## 🔄 How It Works

### **1. Accurate Data Collection**
- Scrapes fresh session data from duome.eu using browser automation
- Clicks the "aggiorna" update button to ensure current data
- **ONLY trusts the raw modal data** - all other duome.eu data is chronically inaccurate
- Counts ALL XP-earning activities as lessons (personalized practice, stories, unit reviews, etc.)
- **No learning activity is excluded from lesson totals**

### **2. Dynamic Goal Calculation**
```
Current Progress → Lessons Per Unit Average → Remaining Lessons Estimate → Required Daily Pace
```

- **Lessons per unit**: Calculated from unit boundary analysis using "unit review" markers (not static estimates)
- **Daily goal**: Recalculated based on remaining time and recent unit completion patterns
- **Projections**: Updated automatically as new unit boundaries are detected

### **3. Smart Progress Tracking**
- **Daily**: Track lessons completed vs dynamic daily goal
- **Weekly**: Analyze trends and adjust pace
- **Overall**: Monitor progress toward 18-month completion target
- **Projections**: Estimate actual completion date based on current performance

## 🚀 Quick Start

### **Prerequisites**
- Python 3.7+
- Firefox browser (for automation)
- duome.eu account access

### **Installation**
```bash
# 1. Set up environment
python -m venv duolingo_env
source duolingo_env/bin/activate  # Windows: duolingo_env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Project setup (one-time)
python scripts/setup.py --all
```

### **Daily Usage**
```bash
# Run complete daily update (recommended via automation)
python scripts/daily_update.py

# Manual scraping only
python src/scrapers/duome_raw_scraper.py --username jonamar

# Analysis only
python scripts/analyze.py
```

## 📊 What You Get

### **Real-Time Progress Tracking**
- **Accurate lesson counts**: All learning activities counted properly
- **Dynamic daily goals**: Adjusted based on actual performance and remaining time
- **Completion projections**: Data-driven estimates of course completion
- **Unit progression**: Track lessons per unit and difficulty progression

### **Automated Reporting**
- **Markdown reports**: Updated progress summaries in `personal-math.md`
- **JSON data files**: Detailed session data for analysis
- **Push notifications**: Daily progress alerts via Pushover
- **Goal adjustments**: Automatic recalculation of required daily pace

### **Key Metrics**
```
📈 Progress Metrics:
   • Total lessons completed: 179 (was 55 before fix!)
   • Units completed: 86 / 272
   • Current pace: X lessons/day
   • Required pace: Y lessons/day
   • Projected completion: Date

📊 Performance Analytics:
   • Lessons per unit average: Z (dynamic)
   • Daily goal achievement rate
   • Weekly progression trends
   • Ahead/behind schedule status
```

## ⚙️ Core Configuration

### **Project Parameters** (`config/app_config.py`)
```python
USERNAME = "jonamar"
TOTAL_UNITS_IN_COURSE = 272    # French course total
GOAL_DAYS = 548                # 18 months
```

### **Dynamic Calculations** (Auto-updated)
- `lessons_per_unit`: Calculated from actual completion data
- `daily_goal`: Based on remaining lessons and time
- `completion_projection`: Estimated finish date

## 🏗️ Architecture

### **Core Components**
- **Scrapers** (`src/scrapers/`): Browser automation, data extraction
- **Core Logic** (`src/core/`): Progress calculation, goal management
- **Notifiers** (`src/notifiers/`): Progress alerts and updates
- **Data Layer** (`src/data/`): State management, atomic operations

### **Key Files**
- `tracker_state.json`: Current progress and goals
- `personal-math.md`: Human-readable progress report
- `CORE_BUSINESS_LOGIC.md`: **Critical business rules (READ THIS)**
- `IMPROVEMENT_ROADMAP.md`: Technical development roadmap

## 🚨 Critical Business Logic

**⚠️ REQUIRED READING**: This project has specific business requirements that must be preserved during any development work.

### **📋 [CORE_BUSINESS_LOGIC.md](CORE_BUSINESS_LOGIC.md) ← READ THIS FIRST**

**Essential Principles:**
1. **ALL XP-earning sessions count as lessons** (no exclusions)
2. **Dynamic goal calculation** based on actual performance data
3. **18-month completion target** with adaptive daily goals
4. **Historical data integrity** when making changes

**Developer Protection Rules:**
- Lesson counting logic must never exclude valid learning activities
- Goal calculations must remain dynamic and data-driven  
- Any changes affecting progress tracking require historical recalculation
- Session types are metadata only - they do NOT affect lesson counting

**⚠️ BREAKING THESE RULES WILL CORRUPT PROGRESS TRACKING ⚠️**

## 🎯 Project Status

**Current Progress** (as of latest run):
- ✅ **179 total lessons** completed (corrected from previous 55)
- ✅ **86 units completed** out of 272 total
- ✅ **Dynamic goal calculation** implemented
- ✅ **Accurate lesson counting** for all session types
- ✅ **Automated daily tracking** via launchd

**Next Milestones**:
- Enhanced progress projections
- Weekly trend analysis
- Completion timeline optimization

## 📚 Documentation

### **Critical Documents**
- **[CORE_BUSINESS_LOGIC.md](CORE_BUSINESS_LOGIC.md)**: ⚠️ **MUST READ** - Immutable business requirements
  
### **Development Documents**  
- **[CLAUDE.md](CLAUDE.md)**: Developer guidance and commands
- **[IMPROVEMENT_ROADMAP.md](IMPROVEMENT_ROADMAP.md)**: Technical development roadmap

## 🤝 Contributing

**For Developers**: 
1. **Read `CORE_BUSINESS_LOGIC.md` first** - contains immutable business requirements
2. Lesson counting logic must never exclude valid learning activities  
3. Goal calculations must remain dynamic and data-driven
4. Any changes affecting progress tracking require historical recalculation

**For Future Maintainers**:
This system tracks progress toward a specific 18-month goal using dynamic calculations. The core lesson counting and goal calculation logic is business-critical and must be preserved during any refactoring or feature additions.

---

*Goal: Complete 272 French units in 548 days using data-driven progress tracking.*