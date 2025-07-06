#!/usr/bin/env python3
"""
Markdown Updater
Handles all markdown file formatting and updates.
Extracted from daily_tracker.py for better organization and testability.
"""

import re
from datetime import datetime
from config import app_config as cfg
from .metrics_calculator import calculate_performance_metrics, get_tracked_unit_progress


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
        print(f"❌ Could not parse 'Completed Units' from {cfg.MARKDOWN_FILE}: {e}")
        return False

    # --- Calculate new values using centralized calculation throughout ---
    progress = get_tracked_unit_progress(state_data, json_data)
    new_completed_units = progress['completed_units']  # Use centralized calculation (tracking-only)
    new_remaining_units = progress['remaining_units']  # Use centralized calculation  
    total_lessons_remaining = progress['total_lessons_remaining']
    lessons_per_day_required = progress['required_lessons_per_day']
    time_per_day_required_mins = lessons_per_day_required * cfg.BASE_MINS_PER_LESSON
    
    hours = int(time_per_day_required_mins // 60)
    minutes = int(time_per_day_required_mins % 60)
    time_per_day_str = f"~{hours} hour {minutes} minutes"

    # --- Update content with new values ---
    # Update Total Units in Course to show trackable units (not full course)
    content = re.sub(r"(\*\*Total Units in Course\*\*:\s*)(\d+)", rf"\g<1>{cfg.TRACKABLE_TOTAL_UNITS}", content)
    content = re.sub(r"(Total Units in Course:\s*)(\d+)", rf"\g<1>{cfg.TRACKABLE_TOTAL_UNITS}", content)
    
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
        
    # Update goal progress metrics using centralized calculation (always run)
    progress = get_tracked_unit_progress(state_data, json_data)
    
    # Update daily requirement using centralized calculation
    content = re.sub(r"(\*\*Daily Requirement\*\*:\s*)[\d.]+\s*lessons/day.*", 
                  rf"\g<1>{progress['required_lessons_per_day']:.1f} lessons/day (based on {progress['completed_units']} tracked units, {progress['lessons_per_unit']:.1f} avg lessons/unit)", content)
    
    # Update pace status using centralized calculation
    content = re.sub(r"(\*\*Pace Status\*\*:\s*).*lessons/day", 
                  rf"\g<1>{progress['pace_status']}", content)
    
    # Calculate projected completion using centralized data
    projected_days = progress['total_lessons_remaining'] / progress['current_daily_avg'] if progress['current_daily_avg'] > 0 else 0
    projected_months = projected_days / 30.44  # avg days per month
    
    # Update projected completion
    content = re.sub(r"(\*\*Projected Completion\*\*:\s*)[\d.]+\s*months.*", 
                  rf"\g<1>{projected_months:.1f} months ({abs(projected_months - 18):.1f} months {'early' if projected_months < 18 else 'late'})", content)
    
    # Update total lessons needed using centralized calculation
    content = re.sub(r"(\*\*Total Lessons Needed\*\*:\s*)[\d,]+\s*lessons.*", 
                  rf"\g<1>{progress['total_lessons_remaining']:,.0f} lessons ({progress['remaining_units']} remaining units)", content)
    
    # Add or update 18-month goal progress section
    goal_section = f"""
### 18-Month Goal Progress (Started {progress['goal_start_date']})
- **Goal End Date**: {progress['goal_end_date']}
- **Days Elapsed**: {progress['days_elapsed']} of {cfg.GOAL_DAYS} days ({progress['completion_percentage']:.1f}% complete)
- **Historical Pace**: {progress['actual_units_per_day']:.3f} units/day, {progress['actual_lessons_per_day']:.1f} lessons/day  
- **Required Pace**: {progress['required_units_per_day']:.3f} units/day, {progress['required_lessons_per_day']:.1f} lessons/day
- **Status**: {progress['pace_status']}
- **Projected Completion**: {progress['projected_completion_date']} ({abs(progress['months_difference'] or 0):.1f} months {'early' if (progress['months_difference'] or 0) < 0 else 'late'})

*This section will be updated as more units are completed.*
"""
    
    # Check if 18-month goal section already exists and replace it, or add it
    if "### 18-Month Goal Progress" in content:
        # Replace existing section
        content = re.sub(r"### 18-Month Goal Progress.*?\*This section will be updated as more units are completed\.\*\s*", 
                      goal_section, content, flags=re.DOTALL)
    else:
        # Insert before "### Completion Goal: 18 Months"
        content = re.sub(r"(### Completion Goal: 18 Months)", 
                      goal_section + r"\1", content)
    
    content = re.sub(r"(\*Last updated:\s*)[\w\s,]+", rf"\g<1>{datetime.now().strftime('%B %d, %Y')}", content)

    with open(cfg.MARKDOWN_FILE, 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully updated {cfg.MARKDOWN_FILE}.")
    if newly_completed_count > 0:
        print(f"   - Newly Completed Units: {newly_completed_count}")
    
    # Show detailed breakdown of lessons
    if core_lessons is not None and practice_sessions is not None:
        print(f"   - Total Sessions: {total_lessons_count} (Core: {core_lessons}, Practice: {practice_sessions})")
    else:
        print(f"   - Total Sessions: {total_lessons_count}")
    return True