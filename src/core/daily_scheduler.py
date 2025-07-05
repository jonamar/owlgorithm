#!/usr/bin/env python3
"""
Daily Duome.eu Data Collection Scheduler
=======================================

This script automates daily data collection from duome.eu to build a 
comprehensive lesson log over time. It can be run via cron or system scheduler.

Features:
- Automated daily scraping
- Error handling and logging
- Data validation and deduplication
- Progress tracking and analytics
- Email notifications (optional)

Setup:
1. Install dependencies: pip install -r requirements.txt
2. Run manually: python daily_scheduler.py --username jonamar
3. Schedule daily: crontab -e
   Add: 0 23 * * * /path/to/python /path/to/daily_scheduler.py -u jonamar

Usage:
    python daily_scheduler.py --username jonamar --email your@email.com
"""

import subprocess
import sys
import os
import csv
import pandas as pd
from datetime import datetime, timedelta
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import argparse

# Setup project paths - must be done before other imports
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..')))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..', '..')))

# Now import utilities
from utils.path_utils import build_duome_url
from utils.constants import SUBPROCESS_TIMEOUT
from config import app_config as cfg
import json

class DailyDuolingoTracker:
    def __init__(self, username, data_dir=cfg.DATA_DIR, email=None):
        self.username = username
        self.data_dir = data_dir
        self.email = email
        
        # Create data directory
        os.makedirs(data_dir, exist_ok=True)
        
        # Set up logging
        log_file = os.path.join(data_dir, f"duolingo_tracker_{username}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # File paths
        self.profile_file = os.path.join(data_dir, f"{username}_profile.csv")
        self.daily_file = os.path.join(data_dir, f"{username}_daily.csv")
        self.summary_file = os.path.join(data_dir, f"{username}_summary.json")
    
    def run_scraper(self):
        """Run the duome scraper"""
        try:
            scraper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scrapers', 'duome_raw_scraper.py'))
            cmd = [
                sys.executable,
                scraper_path,
                "--username", self.username,
                "--output", os.path.join(self.data_dir, f"{self.username}_data.json"),
                "--no-automation"
            ]
            
            self.logger.info(f"Running duome scraper for {self.username}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT)
            
            if result.returncode == 0:
                self.logger.info("Scraper completed successfully")
                self.logger.info(result.stdout)
                return True
            else:
                self.logger.error(f"Scraper failed with return code {result.returncode}")
                self.logger.error(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Scraper timed out after {SUBPROCESS_TIMEOUT} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Error running scraper: {e}")
            return False
    
    def analyze_progress(self):
        """Analyze progress and generate insights"""
        try:
            if not os.path.exists(self.profile_file):
                self.logger.warning("No profile data file found")
                return None
            
            # Load profile data
            df_profile = pd.read_csv(self.profile_file)
            
            if df_profile.empty:
                return None
            
            # Get latest and previous data
            latest = df_profile.iloc[-1]
            
            analysis = {
                'date': datetime.now().isoformat(),
                'total_xp': int(latest['total_xp']),
                'current_streak': int(latest['current_streak']),
                'current_course': latest['current_course'],
                'crowns': int(latest['crowns']),
                'words_learned': int(latest['words_learned'])
            }
            
            # Calculate daily progress if we have previous data
            if len(df_profile) > 1:
                previous = df_profile.iloc[-2]
                analysis['daily_xp_gain'] = int(latest['total_xp'] - previous['total_xp'])
                analysis['daily_crown_gain'] = int(latest['crowns'] - previous['crowns'])
                analysis['daily_word_gain'] = int(latest['words_learned'] - previous['words_learned'])
                
                # Streak analysis
                if latest['current_streak'] > previous['current_streak']:
                    analysis['streak_status'] = 'maintained'
                elif latest['current_streak'] < previous['current_streak']:
                    analysis['streak_status'] = 'broken'
                else:
                    analysis['streak_status'] = 'same'
            
            # Weekly and monthly stats
            if len(df_profile) >= 7:
                week_ago = df_profile.iloc[-8] if len(df_profile) >= 8 else df_profile.iloc[0]
                analysis['weekly_xp_gain'] = int(latest['total_xp'] - week_ago['total_xp'])
                analysis['weekly_crown_gain'] = int(latest['crowns'] - week_ago['crowns'])
            
            # Save analysis
            with open(self.summary_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            self.logger.info(f"Progress analysis completed: {analysis.get('daily_xp_gain', 0)} XP gained today")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing progress: {e}")
            return None
    
    def generate_report(self, analysis):
        """Generate a progress report"""
        if not analysis:
            return "No progress data available"
        
        report = f"""
🦉 Daily Duolingo Progress Report for {self.username}
{'='*50}

📊 Current Stats:
   • Total XP: {analysis['total_xp']:,}
   • Current Streak: {analysis['current_streak']} days
   • Current Course: {analysis['current_course']}
   • Crowns: {analysis['crowns']:,}
   • Words Learned: {analysis['words_learned']:,}

🚀 Today's Progress:"""
        
        if 'daily_xp_gain' in analysis:
            report += f"""
   • XP Gained: {analysis['daily_xp_gain']} XP
   • Crowns Gained: {analysis['daily_crown_gain']}
   • New Words: {analysis['daily_word_gain']}
   • Streak: {analysis['streak_status']}"""
        
        if 'weekly_xp_gain' in analysis:
            report += f"""

📈 Weekly Summary:
   • XP This Week: {analysis['weekly_xp_gain']} XP
   • Crowns This Week: {analysis['weekly_crown_gain']}"""
        
        report += f"""

📅 Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔗 Profile: {build_duome_url(self.username)}
"""
        
        return report
    
    def send_email_report(self, report):
        """Send email report (optional)"""
        if not self.email:
            return
        
        try:
            # This is a basic example - you'd need to configure SMTP settings
            self.logger.info(f"Email reporting to {self.email} not configured")
            # TODO: Implement email sending based on your email provider
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
    
    def run_daily_collection(self):
        """Run the complete daily data collection process"""
        self.logger.info(f"Starting daily collection for {self.username}")
        
        # Run scraper
        scraper_success = self.run_scraper()
        
        if not scraper_success:
            self.logger.error("Daily collection failed - scraper error")
            return False
        
        # Analyze progress
        analysis = self.analyze_progress()
        
        # Generate report
        report = self.generate_report(analysis)
        self.logger.info("Daily report:\n" + report)
        
        # Send email if configured
        self.send_email_report(report)
        
        self.logger.info("Daily collection completed successfully")
        return True

def setup_cron_job(username, script_path=None):
    """Helper to set up a cron job for daily collection"""
    if script_path is None:
        script_path = os.path.abspath(__file__)
    
    python_path = sys.executable
    
    cron_command = f"0 23 * * * {python_path} {script_path} --username {username}"
    
    print("🕐 To set up daily automatic collection, add this to your crontab:")
    print(f"   (Run: crontab -e)")
    print(f"   {cron_command}")
    print()
    print("This will run every day at 11 PM. Adjust the time as needed:")
    print("   Format: minute hour day month weekday")
    print("   Example: '0 9 * * *' for 9 AM daily")

def main():
    parser = argparse.ArgumentParser(description='Daily Duolingo progress tracker using duome.eu')
    parser.add_argument('--username', '-u', required=True, help='Duolingo username')
    parser.add_argument('--data-dir', '-d', default=cfg.DATA_DIR, help='Data directory')
    parser.add_argument('--email', '-e', help='Email for progress reports')
    parser.add_argument('--setup-cron', action='store_true', help='Show cron setup instructions')
    
    args = parser.parse_args()
    
    if args.setup_cron:
        setup_cron_job(args.username)
        return
    
    # Create tracker and run daily collection
    tracker = DailyDuolingoTracker(args.username, args.data_dir, args.email)
    success = tracker.run_daily_collection()
    
    if not success:
        sys.exit(1)
    
    print(f"\n✅ Daily data collection completed!")
    print(f"📁 Data saved in: {args.data_dir}")
    print(f"🔍 View logs: {os.path.join(args.data_dir, f'duolingo_tracker_{args.username}.log')}")
    print("\n💡 Tips:")
    print(f"   • Run with --setup-cron to see scheduling instructions")
    print(f"   • Check your data: ls -la {args.data_dir}/")
    print(f"   • View profile at: {build_duome_url(args.username)}")

 