#!/usr/bin/env python3
"""
Test URL formatting for special characters
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from horse_profile_scraper import HorseProfileScraper

def test_url_formatting():
    """Test URL formatting for horses with special characters"""
    scraper = HorseProfileScraper()
    
    test_horses = [
        "Cash's Candy",
        "Sparta F. C.",
        "Sally's Wish",
        "Lee's Baby Girl",
        "Nesso's Lastharrah",
        "Kale's Angel"
    ]
    
    print("Testing URL formatting:")
    for horse_name in test_horses:
        formatted = scraper._format_horse_name_for_url(horse_name)
        url = f"{scraper.base_url}/horse/{formatted}"
        print(f"  {horse_name} -> {formatted}")
        print(f"    URL: {url}")
        print()

def test_cashs_candy():
    """Test scraping Cash's Candy specifically"""
    scraper = HorseProfileScraper()
    
    print("Testing Cash's Candy scraping...")
    result = scraper.scrape_horse_profile("Cash's Candy")
    
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
        print("No result found for Cash's Candy")

if __name__ == "__main__":
    test_url_formatting()
    print("="*50)
    test_cashs_candy()