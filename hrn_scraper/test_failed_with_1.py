#!/usr/bin/env python3
"""
Test failed horses that might have _1 variants
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from horse_profile_scraper import HorseProfileScraper

def test_failed_horses_with_1_variant():
    """Test horses that failed and might have _1 variants"""
    
    # Failed horses from the last run - excluding obvious name format issues
    failed_horses = [
        "Cashed",  # We know this works now
        "Sally's Wish", 
        "Billie Holiday",
        "Rio Grande",
        "Gold Phoenix",
        "Beyond Brilliant",
        "Express Train",
        "First Mission"
    ]
    
    scraper = HorseProfileScraper()
    
    print(f"Testing {len(failed_horses)} failed horses with _1 variant...")
    
    successful = 0
    
    for horse_name in failed_horses:
        print(f"\nTesting: {horse_name}")
        
        result = scraper.scrape_horse_profile(horse_name)
        
        if result and result.get('race_history'):
            successful += 1
            race_history = result.get('race_history', [])
            print(f"  ✅ SUCCESS - Found {len(race_history)} races")
            if race_history:
                latest_race = race_history[0]
                date = latest_race.get('race_date', latest_race.get('date', 'N/A'))
                track = latest_race.get('track', 'N/A')
                finish = latest_race.get('finish_position', 'N/A')
                print(f"      Latest: {date} at {track}, Finish: {finish}")
        else:
            print(f"  ❌ FAILED - No races found")
    
    print(f"\n=== SUMMARY ===")
    print(f"Successful: {successful}/{len(failed_horses)}")

if __name__ == "__main__":
    test_failed_horses_with_1_variant()