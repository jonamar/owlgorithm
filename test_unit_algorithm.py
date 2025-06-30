#!/usr/bin/env python3
"""
Test script for Algorithm 1: First Mention = Unit Start with Sub-unit Folding
Tests on the HTML debug data with constraints.
"""

import re
from datetime import datetime
from collections import defaultdict

def parse_html_sessions(html_file):
    """Parse sessions from HTML file"""
    with open(html_file, 'r') as f:
        lines = f.readlines()
    
    sessions = []
    skipped_lines = []
    
    for i, line in enumerate(lines, 1):
        # Skip non-lesson lines:
        # - dailyxp summaries: <li class="dailyxp">
        # - lines without · or XP (structural elements)  
        if 'class="dailyxp"' in line:
            skipped_lines.append(f'Line {i}: dailyxp summary')
            continue
        if not '·' in line or 'XP' not in line:
            if '<li>' in line:  # Only log li elements we're skipping
                skipped_lines.append(f'Line {i}: no datetime/XP pattern')
            continue
        
        # Extract datetime and XP
        datetime_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        xp_match = re.search(r'(\d+)XP', line)
        
        if not datetime_match or not xp_match:
            continue
        
        datetime_str = datetime_match.group(1)
        xp = int(xp_match.group(1))
        
        # Extract unit name from skill links
        unit = None
        skill_match = re.search(r'<a target="_blank" href="https://www\.duolingo\.com/skill/fr/([^"]+)">', line)
        if skill_match:
            unit = skill_match.group(1).replace('-', ' ')
        
        sessions.append({
            'line_num': i,
            'datetime': datetime_str,
            'xp': xp,
            'unit': unit,
            'raw_line': line.strip()
        })
    
    # Debug output
    print(f'DEBUG: Parsed {len(sessions)} lesson sessions')
    if skipped_lines:
        print(f'DEBUG: Skipped {len(skipped_lines)} non-lesson lines:')
        for skip in skipped_lines[:5]:  # Show first 5
            print(f'  {skip}')
        if len(skipped_lines) > 5:
            print(f'  ... and {len(skipped_lines) - 5} more')
    
    return sessions

def apply_algorithm_1(sessions, exclude_current_unit=True):
    """Apply Algorithm 1: First Mention = Unit Start with Sub-unit Folding"""
    
    print('=== ALGORITHM 1: FIRST MENTION = UNIT START ===')
    
    # Apply constraints: lines 19-149 (exclude current unit and On Sale)
    first_protest_line = 19
    filtered_sessions = [s for s in sessions if first_protest_line <= s['line_num'] < 150]
    
    print(f'Filtered sessions (lines {first_protest_line}-149): {len(filtered_sessions)}')
    
    # Get chronological unit sequence from explicit unit mentions
    unit_sessions = [s for s in filtered_sessions if s['unit']]
    unit_sessions.sort(key=lambda x: x['datetime'])
    
    # Build unit sequence (first mention = start)
    unit_boundaries = []
    seen_units = set()
    for session in unit_sessions:
        if session['unit'] not in seen_units:
            unit_boundaries.append({
                'unit': session['unit'],
                'start_datetime': session['datetime']
            })
            seen_units.add(session['unit'])
            print(f'Unit start: {session["unit"]} at {session["datetime"]}')
    
    unit_sequence = [b['unit'] for b in unit_boundaries]
    print(f'Unit sequence: {unit_sequence}')
    
    # Sort all sessions chronologically
    all_sessions = sorted(filtered_sessions, key=lambda x: x['datetime'])
    
    # Assign ALL sessions (including practice) to units based on active unit
    unit_counts = defaultdict(int)
    current_unit = None
    
    print('\nAssigning sessions to units:')
    for session in all_sessions:
        # Update current unit if this session has an explicit unit
        if session['unit']:
            current_unit = session['unit']
        
        # Count ALL sessions as lessons for the current unit
        if current_unit and (not exclude_current_unit or current_unit != 'Protest'):
            unit_counts[current_unit] += 1
            if session.get('line_num', 0) % 20 == 0:  # Sample logging
                unit_type = 'explicit' if session['unit'] else 'practice'
                print(f'  Line {session.get("line_num", "?")}: {current_unit} +1 ({unit_type})')
    
    print(f'\nAssigned {sum(unit_counts.values())} total lessons to units')
    
    print('\nLesson counts (before folding):')
    for unit in unit_sequence:
        if not exclude_current_unit or unit != 'Protest':
            print(f'  {unit}: {unit_counts[unit]} lessons')
    
    # Apply sub-unit folding
    print('\n=== SUB-UNIT FOLDING ===')
    final_counts = {}
    folded_units = set()
    
    for i, unit in enumerate(unit_sequence):
        if exclude_current_unit and unit == 'Protest':
            print(f'  SKIP: {unit} (current unit)')
            continue
        
        if unit in folded_units:
            continue
            
        # Check for small units (<8 lessons) that should be folded
        if unit_counts[unit] < 8:
            # Check if surrounded by same unit
            prev_unit = unit_sequence[i-1] if i > 0 else None
            next_unit = unit_sequence[i+1] if i < len(unit_sequence)-1 else None
            
            # Special case: check if adjacent to a unit (not necessarily surrounded)
            target_unit = None
            if prev_unit and prev_unit in unit_counts:
                target_unit = prev_unit
            elif next_unit and next_unit in unit_counts:
                target_unit = next_unit
            
            if target_unit and target_unit != 'Protest':
                print(f'  FOLD: {unit} ({unit_counts[unit]} lessons) into {target_unit}')
                if target_unit not in final_counts:
                    final_counts[target_unit] = unit_counts[target_unit]
                final_counts[target_unit] += unit_counts[unit]
                folded_units.add(unit)
            else:
                print(f'  KEEP: {unit} ({unit_counts[unit]} lessons) - no fold target')
                final_counts[unit] = unit_counts[unit]
        else:
            print(f'  KEEP: {unit} ({unit_counts[unit]} lessons) - large enough')
            final_counts[unit] = unit_counts[unit]
    
    return final_counts

def main():
    html_file = '/Users/jonamar/Development/owlgorithm/test-data-temp-for-debuggin.html'
    
    # Parse sessions
    sessions = parse_html_sessions(html_file)
    print(f'Total sessions parsed: {len(sessions)}')
    
    # Debug: Check lines 41-54 specifically (your example range)
    print('\nDEBUG: Lines 41-54 analysis:')
    lines_41_54 = [s for s in sessions if 41 <= s['line_num'] <= 54]
    print(f'Found {len(lines_41_54)} lesson sessions in lines 41-54')
    for session in lines_41_54:
        unit_info = f"({session['unit']})" if session['unit'] else "(practice)"
        print(f"  Line {session['line_num']}: {session['datetime']} - {session['xp']}XP {unit_info}")
    
    expected_count = 13  # Your manual count
    actual_count = len(lines_41_54)
    print(f'Expected: {expected_count}, Actual: {actual_count}, Difference: {expected_count - actual_count}')
    
    # Apply Algorithm 1
    final_counts = apply_algorithm_1(sessions, exclude_current_unit=True)
    
    # Calculate results
    print('\n=== FINAL RESULTS ===')
    total_lessons = 0
    for unit, count in final_counts.items():
        print(f'{unit}: {count} lessons')
        total_lessons += count
    
    num_units = len(final_counts)
    average = total_lessons / num_units if num_units > 0 else 0
    
    print(f'\nSummary:')
    print(f'  Total lessons: {total_lessons}')
    print(f'  Number of completed units: {num_units}')
    print(f'  Average lessons per unit: {average:.1f}')

if __name__ == '__main__':
    main()