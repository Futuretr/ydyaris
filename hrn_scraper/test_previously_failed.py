#!/usr/bin/env python3
"""
Test previously failed horses to see if our improvements help
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from horse_profile_scraper import HorseProfileScraper
import csv

def test_failed_horses():
    """Test horses that previously failed"""
    scraper = HorseProfileScraper()
    
    # Read the entries CSV to find horses that might have special characters
    entries_file = "santa-anita_2025_09_27_santa-anita_entries.csv"
    
    # Horses we suspect might have issues based on special characters or names
    test_horses = []
    
    try:
        with open(entries_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                horse_name = row['horse_name'].strip()
                # Look for horses with apostrophes, periods, or other special characters
                if "'" in horse_name or "." in horse_name or "(" in horse_name:
                    test_horses.append(horse_name)
    except FileNotFoundError:
        print(f"Could not find {entries_file}")
        return
    
    print(f"Testing {len(test_horses)} horses with special characters...")
    
    success_count = 0
    failed_horses = []
    
    for horse_name in test_horses[:10]:  # Test first 10 to not overwhelm
        print(f"\nTesting: {horse_name}")
        
        # Test URL formatting first
        formatted_url_name = scraper._format_horse_name_for_url(horse_name)
        print(f"  Formatted URL: https://www.horseracingnation.com/horse/{formatted_url_name}")
        
        # Try scraping
        try:
            result = scraper.scrape_horse_profile(horse_name)
            if result and 'race_history' in result and result['race_history']:
                success_count += 1
                print(f"  ✅ SUCCESS - Found {len(result['race_history'])} races")
                latest_race = result['race_history'][0]
                print(f"      Latest: {latest_race.get('date')} at {latest_race.get('track')}")
            else:
                failed_horses.append(horse_name)
                print(f"  ❌ FAILED - No races found or result empty")
        except Exception as e:
            failed_horses.append(horse_name)
            print(f"  ❌ ERROR - {str(e)}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Tested: {len(test_horses[:10])} horses")
    print(f"Success: {success_count}")
    print(f"Failed: {len(failed_horses)}")
    
    if failed_horses:
        print("\nFailed horses:")
        for horse in failed_horses:
            print(f"  - {horse}")

if __name__ == "__main__":
    test_failed_horses()