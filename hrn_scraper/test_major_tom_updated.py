#!/usr/bin/env python3
"""
Test updated horse profile scraper with Major Tom
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from horse_profile_scraper import HorseProfileScraper

def test_major_tom_updated():
    """Test the updated scraper with Major Tom"""
    scraper = HorseProfileScraper()
    
    print("Testing updated scraper with Major Tom...")
    result = scraper.scrape_horse_profile("Major Tom")
    
    if result:
        horse_info = result.get('horse_info', {})
        race_history = result.get('race_history', [])
        
        print(f"\n=== Horse Info ===")
        print(f"Name: {horse_info.get('name')}")
        print(f"Age: {horse_info.get('age')}")
        print(f"Sex: {horse_info.get('sex')}")
        print(f"Trainer: {horse_info.get('trainer')}")
        
        print(f"\n=== Race History ===")
        print(f"Total races found: {len(race_history)}")
        
        if race_history:
            print("\nMost recent 3 races:")
            for i, race in enumerate(race_history[:3]):
                print(f"{i+1}. Date: {race.get('race_date')}, Track: {race.get('track')}, Finish: {race.get('finish_position')}")
    else:
        print("No result found for Major Tom")

if __name__ == "__main__":
    test_major_tom_updated()