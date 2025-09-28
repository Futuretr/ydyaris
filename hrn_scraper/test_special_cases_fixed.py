#!/usr/bin/env python3
"""
Test script for special case horses: Cash's Candy and Full Serrano
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from horse_profile_scraper import HorseProfileScraper

def test_special_cases():
    """Test horses with special formatting requirements"""
    scraper = HorseProfileScraper()
    
    # Test cases
    test_horses = [
        "Cash's Candy",
        "Full Serrano"
    ]
    
    print("Testing special case horses...")
    
    for horse_name in test_horses:
        print(f"\nTesting: {horse_name}")
        
        # Test URL formatting first
        formatted_url_name = scraper._format_horse_name_for_url(horse_name)
        print(f"  Formatted URL: https://www.horseracingnation.com/horse/{formatted_url_name}")
        
        # Try scraping
        try:
            result = scraper.scrape_horse_profile(horse_name)
            if result and 'race_history' in result and result['race_history']:
                print(f"  ✅ SUCCESS - Found {len(result['race_history'])} races")
                latest_race = result['race_history'][0]
                print(f"      Latest: {latest_race.get('date')} at {latest_race.get('track')}")
                print(f"      Distance: {latest_race.get('distance')}, Surface: {latest_race.get('surface')}")
                print(f"      Time: {latest_race.get('time')}, Finish: {latest_race.get('finish_position')}")
            else:
                print(f"  ❌ FAILED - No races found or result empty")
        except Exception as e:
            print(f"  ❌ ERROR - {str(e)}")

if __name__ == "__main__":
    test_special_cases()