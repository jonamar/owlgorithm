# Duolingo Daily Lesson Tracker

A Python tool to track your daily Duolingo progress by scraping data from **duome.eu** - the comprehensive Duolingo statistics platform.

## 🎯 What This Does

- **Daily Lesson Logging**: Automatically tracks your daily XP, lessons, and progress
- **Historical Data**: Collects detailed activity records going back weeks
- **CSV Export**: Saves data in easy-to-analyze spreadsheet format
- **Automated Collection**: Can run daily via scheduler to build comprehensive logs
- **No API Blocking**: Uses duome.eu instead of blocked official Duolingo API

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Manual Collection
```bash
python duome_scraper.py --username YOUR_DUOLINGO_USERNAME
```

### 3. Set Up Daily Automation
```bash
python daily_scheduler.py --username YOUR_DUOLINGO_USERNAME --setup-cron
```

## 📊 What Data You Get

### Profile Summary (`username_profile.csv`)
- Total XP and current streak
- Course level and progress
- Total crowns and words learned
- Timestamp of each collection

### Daily Activity (`username_daily.csv`)
- Date-by-date XP gains
- Estimated lessons completed
- Multiple sessions per day
- Historical activity records

## 🔧 Usage Examples

### Basic Data Collection
```bash
# Collect current stats
python duome_scraper.py --username jonamar

# Save to specific file
python duome_scraper.py --username jonamar --output my_progress.csv
```

### Automated Daily Tracking
```bash
# Run daily collection with analysis
python daily_scheduler.py --username jonamar

# Set up automatic scheduling
python daily_scheduler.py --username jonamar --setup-cron
```

## 📁 Output Files

After running, you'll get:
- `username_profile.csv` - Daily profile snapshots
- `username_daily.csv` - Detailed daily activity
- `duolingo_tracker_username.log` - Execution logs

## 🔄 Scheduling Options

### macOS/Linux (cron)
```bash
# Add to crontab for daily 11 PM collection
0 23 * * * /path/to/python /path/to/daily_scheduler.py -u YOUR_USERNAME
```

### Windows (Task Scheduler)
Create a daily task that runs:
```
python daily_scheduler.py --username YOUR_USERNAME
```

## 🛠️ Requirements

- Python 3.7+
- Internet connection
- Public duome.eu profile (username must exist on duome.eu)

## 📈 Data Analysis

Import the CSV files into:
- **Excel/Google Sheets**: For charts and pivot tables
- **Python/Pandas**: For advanced analysis
- **Tableau/Power BI**: For dashboards

## ❓ Troubleshooting

### Profile Not Found
- Verify your username exists at `https://duome.eu/YOUR_USERNAME`
- Ensure your Duolingo profile is public

### No Daily Data
- duome.eu may need time to collect your activity
- Try running the scraper after completing some lessons

### Rate Limiting
- The scraper includes respectful delays
- If blocked, wait and try again later

## 🔗 Related Links

- [duome.eu](https://duome.eu) - Duolingo statistics platform
- [Your Profile](https://duome.eu/jonamar) - View your stats online

## 📝 Notes

This tool scrapes publicly available data from duome.eu and does not require Duolingo credentials. It's designed to be respectful of duome.eu's servers with appropriate delays between requests.

The unofficial Duolingo API is currently blocked (2024-2025), making duome.eu the best alternative for detailed progress tracking. 