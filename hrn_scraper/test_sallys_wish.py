#!/usr/bin/env python3
"""
Test Sally's Wish specifically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from horse_profile_scraper import HorseProfileScraper

def test_sallys_wish():
    """Test scraping Sally's Wish specifically"""
    scraper = HorseProfileScraper()
    
    print("Testing Sally's Wish scraping...")
    result = scraper.scrape_horse_profile("Sally's Wish")
    
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
            print("\nMost recent race:")
            race = race_history[0]
            print(f"Date: {race.get('race_date', race.get('date'))}")
            print(f"Track: {race.get('track')}")
            print(f"Distance: {race.get('distance')}")
            print(f"Surface: {race.get('surface')}")
            print(f"Time: {race.get('time')}")
            print(f"Finish: {race.get('finish_position')}")
    else:
        print("No result found for Sally's Wish")

if __name__ == "__main__":
    test_sallys_wish()