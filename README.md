# Duolingo Daily Lesson Tracker

A Python tool to track your daily Duolingo progress by scraping data from **duome.eu** and computing accurate statistics. The tracker automatically refreshes your duome.eu data, parses your lesson history, and generates detailed progress reports.

## 🎯 What This Does

- **Accurate Lesson Tracking**: Computes total lessons from raw session data (more reliable than duome.eu metrics)
- **Auto-Refresh**: Clicks the update button on duome.eu to refresh your latest progress
- **Session Classification**: Distinguishes between core lessons and practice sessions
- **Progress Markdown**: Updates a markdown file with your progress statistics
- **Push Notifications**: Sends alerts when new lessons are completed
- **Projection Model**: Estimates time needed to complete your language track

## 🚀 Quick Start

### 1. Set Up Virtual Environment
```bash
python -m venv duolingo_env
source duolingo_env/bin/activate  # On Windows: duolingo_env\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install selenium requests beautifulsoup4 argparse
```

### 3. Run the Tracker
```bash
./run_tracker.sh  # On Windows: create a batch file or run: python daily_tracker.py
```

## 📊 What Data You Get

### JSON Output Files
Detailed session data in JSON format with:
- Computed lesson count (core lessons + practice sessions)
- Daily statistics breakdown
- Unit completion tracking
- Session classification (lessons vs. practice)
- Historical timestamps

### Markdown Progress Report
- Updated summary of your language progress
- Completed and remaining units
- Total lessons completed (with core/practice breakdown)
- Lessons per day required to reach goal
- Time needed per day to complete course

## 🔧 Usage Examples

### Running the Scraper Only
```bash
# Activate environment
source duolingo_env/bin/activate

# Just collect raw session data without updating markdown
python duome_raw_scraper.py --username YOUR_USERNAME
```

### Refresh Duome Data Only
```bash
# Force refresh of your duome.eu stats without running full tracker
python duome_raw_scraper.py --username YOUR_USERNAME --update-only
```

## 📁 Output Files

After running the tracker, you'll get:
- `duome_raw_YOUR_USERNAME_TIMESTAMP.json` - Raw session data with computed metrics
- `personal-math.md` - Markdown progress report with updated stats
- `tracker_state.json` - Tracking state to avoid duplicate notifications
- `tracker.log` - Execution logs with detailed output

## 🔁 Scheduling Options

### macOS/Linux (cron)
```bash
# Add to crontab for daily automatic refresh and tracking
0 23 * * * cd /path/to/owlgorithm && ./run_tracker.sh
```

### Windows (Task Scheduler)
Create a daily task that runs:
```bash
cd C:\path\to\owlgorithm && python daily_tracker.py
```

## 🔧️ Requirements

- Python 3.7+
- Selenium WebDriver (Firefox or Chrome)
- Virtual environment with required packages
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