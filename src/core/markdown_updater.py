#!/usr/bin/env python3
"""
Markdown Updater
Handles all markdown file formatting and updates.
Extracted from daily_tracker.py for better organization and testability.
"""

import re
from datetime import datetime
from config import app_config as cfg
from .metrics_calculator import calculate_performance_metrics

# Import configuration constants
MARKDOWN_FILE = cfg.MARKDOWN_FILE
TOTAL_UNITS_IN_COURSE = cfg.TOTAL_UNITS_IN_COURSE
GOAL_DAYS = cfg.GOAL_DAYS  # 18 months
BASE_LESSONS_PER_UNIT = cfg.BASE_LESSONS_PER_UNIT
BASE_MINS_PER_LESSON = cfg.BASE_MINS_PER_LESSON


def update_markdown_file(newly_completed_count, total_lessons_count, content, core_lessons=None, practice_sessions=None, json_data=None, state_data=None):
    """Reads, updates, and writes the personal-math.md file.
    
    Args:
        newly_completed_count: Number of newly completed units
        total_lessons_count: Total lessons and practice sessions completed
        content: Content of the markdown file
        core_lessons: Optional number of core lessons (without practice)
        practice_sessions: Optional number of practice sessions
        json_data: Optional session data for calculating performance metrics
        state_data: Optional state data for calculating goal progress
    """
    print(f"📈 Updating stats...")
    
    # --- Read existing values ---
    try:
        # More robust regex that handles markdown formatting, bullet points, etc.
        completed_units_match = re.search(r"\*\*Completed Units\*\*:?\s*(\d+)", content)
        if not completed_units_match:
            # Try alternative formats
            completed_units_match = re.search(r"Completed Units:?\s*(\d+)", content)
        
        if not completed_units_match:
            # Last resort: just look for the number after 'Completed Units'
            completed_units_match = re.search(r"Completed Units.*?(\d+)", content)
            
        if not completed_units_match:
            raise ValueError("Could not locate the 'Completed Units' pattern in the file")
            
        completed_units_old = int(completed_units_match.group(1))
        print(f"Found completed units: {completed_units_old}")
    except (AttributeError, ValueError) as e:
        print(f"❌ Could not parse 'Completed Units' from {MARKDOWN_FILE}: {e}")
        return False

    # --- Calculate new values using baseline constants ---
    new_completed_units = completed_units_old + newly_completed_count
    new_remaining_units = TOTAL_UNITS_IN_COURSE - new_completed_units
    total_lessons_remaining = new_remaining_units * BASE_LESSONS_PER_UNIT
    lessons_per_day_required = total_lessons_remaining / GOAL_DAYS
    time_per_day_required_mins = lessons_per_day_required * BASE_MINS_PER_LESSON
    
    hours = int(time_per_day_required_mins // 60)
    minutes = int(time_per_day_required_mins % 60)
    time_per_day_str = f"~{hours} hour {minutes} minutes"

    # --- Update content with new values ---
    # Handle both "Completed Units:" and "**Completed Units**:" formats
    content = re.sub(r"(\*\*Completed Units\*\*:\s*)(\d+)", rf"\g<1>{new_completed_units}", content)
    content = re.sub(r"(Completed Units:\s*)(\d+)", rf"\g<1>{new_completed_units}", content)
    
    content = re.sub(r"(\*\*Remaining Units\*\*:\s*)(\d+)", rf"\g<1>{new_remaining_units}", content)
    content = re.sub(r"(Remaining Units:\s*)(\d+)", rf"\g<1>{new_remaining_units}", content)
    
    # Update total lessons with computed totals (handle markdown bold formatting)
    content = re.sub(r"(\*\*Total Lessons Completed\*\*:\s*)(\d+)", rf"\g<1>{total_lessons_count}", content)
    
    # Add detail about core lessons vs practice (if available)
    if core_lessons is not None and practice_sessions is not None:
        # Check if we already have a breakdown line, if so update it
        if re.search(r"\(Core: \d+, Practice: \d+\)", content):
            content = re.sub(r"\(Core: \d+, Practice: \d+\)", 
                          f"(Core: {core_lessons}, Practice: {practice_sessions})", content)
        else:
            # Insert after the Total Lessons Completed line
            content = re.sub(r"(Total Lessons Completed:\s*\d+)\s*", 
                          f"\\1 (Core: {core_lessons}, Practice: {practice_sessions})\n", content)
    
    content = re.sub(r"(Total Lessons Remaining:\s*)~?[\d,]+", rf"\g<1>~{total_lessons_remaining:,.0f}", content)
    content = re.sub(r"(Lessons Per Day Required:\s*)\*\*~?[\d.]+\*\*", rf"\g<1>**~{lessons_per_day_required:.1f} lessons**", content)
    content = re.sub(r"(Time Per Day Required:\s*)\*\*~?[\w\s]+\*\*", rf"\g<1>**{time_per_day_str}**", content)
    
    # Update performance metrics if we have session data
    if json_data:
        metrics = calculate_performance_metrics(json_data)
        if metrics:
            # Update daily average
            content = re.sub(r"(\*\*Daily Average\*\*:\s*)[\d.]+\s*lessons/day.*", 
                          rf"\g<1>{metrics['daily_avg_sessions']:.1f} lessons/day (across {metrics['active_days']} active days)", content)
            
            # Update weekly average
            content = re.sub(r"(\*\*Weekly Average\*\*:\s*)[\d.]+\s*lessons/week", 
                          rf"\g<1>{metrics['weekly_avg_sessions']:.1f} lessons/week", content)
            
            # Update XP daily average
            content = re.sub(r"(\*\*XP Daily Average\*\*:\s*)[\d,]+\s*XP/day", 
                          rf"\g<1>{metrics['daily_avg_xp']:.0f} XP/day", content)
            
            # Update XP weekly average
            content = re.sub(r"(\*\*XP Weekly Average\*\*:\s*)[\d,]+\s*XP/week", 
                          rf"\g<1>{metrics['weekly_avg_xp']:,.0f} XP/week", content)
            
            # Update current streak
            content = re.sub(r"(\*\*Current Streak\*\*:\s*)\d+\s*consecutive active days", 
                          rf"\g<1>{metrics['consecutive_days']} consecutive active days", content)
            
            # Update recent performance
            content = re.sub(r"(\*\*Recent Performance\*\*.*?:\s*)[\d.]+\s*lessons/day,\s*[\d,]+\s*XP/day", 
                          rf"\g<1>{metrics['recent_avg_sessions']:.1f} lessons/day, {metrics['recent_avg_xp']:.0f} XP/day", content)
        
        # Update goal progress metrics using recent unit analysis
        total_completed_units = state_data.get('total_completed_units', 3)
        remaining_units = TOTAL_UNITS_IN_COURSE - total_completed_units
        
        # Try to get lessons per unit from recent unit analysis
        recent_unit_analysis = json_data.get('recent_unit_analysis')
        if recent_unit_analysis and metrics:
            avg_lessons_per_unit = recent_unit_analysis['average_lessons_per_unit']
            completed_units_analyzed = recent_unit_analysis['completed_units_analyzed']
            
            # Calculate projections
            total_lessons_needed = remaining_units * avg_lessons_per_unit
            current_avg = metrics['daily_avg_sessions']
            daily_req = total_lessons_needed / 548  # 18 months
            pace_diff = current_avg - daily_req
            
            # Determine pace status
            if pace_diff >= 0:
                pace_status = f"✅ AHEAD by {pace_diff:.1f} lessons/day"
            else:
                pace_status = f"⚠️ BEHIND by {abs(pace_diff):.1f} lessons/day"
            
            # Calculate projected completion
            projected_days = total_lessons_needed / current_avg if current_avg > 0 else 0
            projected_months = projected_days / 30.44  # avg days per month
            
            # Update daily requirement
            content = re.sub(r"(\*\*Daily Requirement\*\*:\s*)[\d.]+\s*lessons/day.*", 
                          rf"\g<1>{daily_req:.1f} lessons/day (based on {completed_units_analyzed} recent completed units, {avg_lessons_per_unit:.1f} avg lessons/unit)", content)
            
            # Update pace status
            content = re.sub(r"(\*\*Pace Status\*\*:\s*).*lessons/day", 
                          rf"\g<1>{pace_status}", content)
            
            # Update projected completion
            content = re.sub(r"(\*\*Projected Completion\*\*:\s*)[\d.]+\s*months.*", 
                          rf"\g<1>{projected_months:.1f} months ({abs(projected_months - 18):.1f} months {'early' if projected_months < 18 else 'late'})", content)
            
            # Update total lessons needed
            content = re.sub(r"(\*\*Total Lessons Needed\*\*:\s*)[\d,]+\s*lessons.*", 
                          rf"\g<1>{total_lessons_needed:,.0f} lessons ({remaining_units} remaining units)", content)
    
    content = re.sub(r"(\*Last updated:\s*)[\w\s,]+", rf"\g<1>{datetime.now().strftime('%B %d, %Y')}", content)

    with open(MARKDOWN_FILE, 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully updated {MARKDOWN_FILE}.")
    if newly_completed_count > 0:
        print(f"   - Newly Completed Units: {newly_completed_count}")
    
    # Show detailed breakdown of lessons
    if core_lessons is not None and practice_sessions is not None:
        print(f"   - Total Sessions: {total_lessons_count} (Core: {core_lessons}, Practice: {practice_sessions})")
    else:
        print(f"   - Total Sessions: {total_lessons_count}")
    return True