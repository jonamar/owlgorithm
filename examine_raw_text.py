#!/usr/bin/env python3
"""
Script to examine the raw_text field in detail to see if granular unit names 
are being extracted but not used.
"""

import json
import os
from collections import defaultdict

def load_latest_data():
    """Load the most recent JSON data file."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    json_files = [f for f in os.listdir(data_dir) if f.startswith("duome_raw_") and f.endswith(".json")]
    json_files.sort(reverse=True)
    
    latest_file = os.path.join(data_dir, json_files[0])
    print(f"Loading data from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def analyze_raw_text_patterns(sessions):
    """Examine raw_text fields to see what granular information we're getting."""
    print("\n=== RAW TEXT ANALYSIS ===")
    
    # Look at recent sessions first (most recent 30)
    recent_sessions = sessions[:30]
    
    print(f"\nExamining {len(recent_sessions)} most recent sessions:\n")
    
    raw_text_examples = []
    unit_patterns = defaultdict(list)
    
    for i, session in enumerate(recent_sessions):
        raw_text = session.get('raw_text', '')
        unit = session.get('unit', 'None')
        assigned_unit = session.get('assigned_unit', 'None')
        session_type = session.get('session_type', 'unknown')
        
        print(f"{i+1:2d}. {session.get('datetime', 'No datetime')}")
        print(f"    Raw text: '{raw_text}'")
        print(f"    Parsed unit: '{unit}' | Assigned: '{assigned_unit}' | Type: {session_type}")
        print()
        
        # Collect patterns
        raw_text_examples.append(raw_text)
        unit_patterns[unit].append(raw_text)
    
    print("\n=== PATTERN ANALYSIS ===")
    print("\nUnique raw text patterns by parsed unit:")
    for unit, texts in unit_patterns.items():
        print(f"\nUnit '{unit}':")
        unique_texts = list(set(texts))
        for text in unique_texts[:5]:  # Show first 5 unique examples
            print(f"  - '{text}'")
        if len(unique_texts) > 5:
            print(f"  ... ({len(unique_texts) - 5} more unique patterns)")
    
    return raw_text_examples

def look_for_granular_info(raw_text_examples):
    """Look for patterns that might contain granular unit information."""
    print("\n=== SEARCHING FOR GRANULAR UNIT INFO ===")
    
    # Look for patterns that might indicate more detailed unit names
    colon_patterns = [text for text in raw_text_examples if ':' in text]
    dash_patterns = [text for text in raw_text_examples if '–' in text or '-' in text]
    longer_patterns = [text for text in raw_text_examples if len(text.split()) > 6]
    
    print(f"\nTexts with colons (might indicate granular units): {len(colon_patterns)}")
    for text in colon_patterns[:5]:
        print(f"  '{text}'")
    
    print(f"\nTexts with dashes (might indicate descriptions): {len(dash_patterns)}")
    for text in dash_patterns[:5]:
        print(f"  '{text}'")
    
    print(f"\nLonger texts (might contain more detail): {len(longer_patterns)}")
    for text in longer_patterns[:5]:
        print(f"  '{text}'")

def main():
    try:
        data = load_latest_data()
        sessions = data.get('sessions', [])
        
        if not sessions:
            print("No sessions found!")
            return
        
        raw_text_examples = analyze_raw_text_patterns(sessions)
        look_for_granular_info(raw_text_examples)
        
        print(f"\n" + "="*60)
        print("CONCLUSION:")
        print("- Check if raw_text contains granular unit names that aren't being parsed")
        print("- Look for patterns like 'bistro: talk about dietary preferences'")
        print("- May need to update scraper to extract more detailed unit information")
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
