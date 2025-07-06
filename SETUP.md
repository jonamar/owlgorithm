# Owlgorithm Setup Guide

This guide will help you set up your own Duolingo progress tracker in under 10 minutes.

## 📋 Prerequisites

- Python 3.8+ installed on your system
- Firefox browser (for web scraping)
- A Duolingo account with some progress
- Optional: Pushover account for notifications

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone https://github.com/yourusername/owlgorithm.git
cd owlgorithm
```

### 2. Create Virtual Environment
```bash
python -m venv duolingo_env
source duolingo_env/bin/activate  # On Windows: duolingo_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your Settings
```bash
# Copy the template configuration
cp config/app_config.example.py config/app_config.py

# Edit your personal configuration
nano config/app_config.py  # or use your preferred editor
```

**Required changes in `config/app_config.py`:**
- `USERNAME`: Your Duolingo username
- `TOTAL_COURSE_UNITS`: Total units in your course (check duome.eu/USERNAME)
- `UNITS_COMPLETED_BEFORE_TRACKING`: Units you've already completed
- `VENV_PYTHON_PATH`: Update path to your project location
- `TRACKING_START_DATE`: Today's date (YYYY-MM-DD format)

### 5. Optional: Setup Notifications
```bash
# Run the interactive Pushover setup
python scripts/setup_pushover.py
```

### 6. Test Your Setup
```bash
# Run a complete test
python scripts/daily_update.py
```

If successful, you'll see:
- A new `personal-math.md` file with your progress
- Data files in the `data/` directory
- Logs in the `logs/` directory

## 🔧 Course-Specific Configuration

### Finding Your Course Information

1. **Visit duome.eu/YOUR_USERNAME** to see your course structure
2. **Count total units** in your target language
3. **Count completed units** (if you've already started)

### Common Course Configurations

**French Course (272 units):**
```python
TOTAL_COURSE_UNITS: int = 272
BASE_LESSONS_PER_UNIT: int = 31
```

**Spanish Course (~200 units):**
```python
TOTAL_COURSE_UNITS: int = 200
BASE_LESSONS_PER_UNIT: int = 28
```

**German Course (~180 units):**
```python
TOTAL_COURSE_UNITS: int = 180
BASE_LESSONS_PER_UNIT: int = 30
```

## 📅 Setting Up Automation

### macOS (launchd)
```bash
# Copy and edit the plist template
cp automation/schedule.plist.example ~/Library/LaunchAgents/com.owlgorithm.duolingo.plist

# Edit the plist file with your project path
nano ~/Library/LaunchAgents/com.owlgorithm.duolingo.plist

# Load the service
launchctl load ~/Library/LaunchAgents/com.owlgorithm.duolingo.plist
```

### Linux/WSL (cron)
```bash
# Add to crontab (runs every 30 minutes, 6am-11:30pm)
crontab -e

# Add this line:
*/30 6-23 * * * cd /path/to/owlgorithm && ./duolingo_env/bin/python scripts/daily_update.py
```

## 🎯 Customization

### Adjusting Goals
```python
# In config/app_config.py
GOAL_DAYS: int = 365  # 1 year goal
DAILY_GOAL_LESSONS: int = 15  # Increase daily target
```

### Changing Notification Times
```python
# In config/app_config.py
MORNING_START_HOUR: int = 7   # Start notifications at 7 AM
EVENING_END_HOUR: int = 22    # End notifications at 10 PM
```

### Custom Progress Reports
Edit the notification messages in `src/notifiers/pushover_notifier.py`

## 🔍 Troubleshooting

### Firefox Issues
```bash
# Test Firefox automation
python src/scrapers/duome_raw_scraper.py --validate-headless --username YOUR_USERNAME
```

### Virtual Environment Path
```bash
# Find your virtual environment path
which python  # While virtual environment is activated
```

### Permission Issues (macOS)
- Grant Firefox permissions in System Preferences > Security & Privacy
- If using ~/Documents, move project to ~/Development to avoid permission issues

### Log Analysis
```bash
# Check recent logs
tail -f logs/tracker.log

# Automation logs (macOS)
tail -f logs/launchd-*.log
```

## 📊 Understanding Your Data

### Progress Report (`personal-math.md`)
- **Current Progress**: Units completed, lessons done today
- **Goal Analysis**: Days remaining, required pace
- **Projections**: Estimated completion date

### State File (`tracker_state.json`)
- **Persistent tracking**: Maintains progress between runs
- **Automatic backups**: Previous versions saved automatically

### Data Files (`data/`)
- **Raw scrapes**: Timestamped data from duome.eu
- **Automatic cleanup**: Old files removed automatically

## 🆘 Getting Help

1. **Check logs**: `tail -f logs/tracker.log`
2. **Validate setup**: `python scripts/setup.py --all`
3. **Test manually**: `python scripts/daily_update.py`
4. **Common issues**: See troubleshooting section above

## 🎉 Success!

Once configured, your tracker will:
- ✅ Automatically scrape progress every 30 minutes
- ✅ Update your progress report
- ✅ Send smart notifications based on time of day
- ✅ Track your goal progress and pace
- ✅ Provide detailed analytics and projections

Happy learning! 🦉 