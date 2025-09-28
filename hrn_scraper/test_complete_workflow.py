#!/usr/bin/env python3
"""
Test the complete workflow with Major Tom
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from horse_profile_scraper import HorseProfileScraper

def test_complete_workflow():
    """Test the complete workflow with Major Tom"""
    scraper = HorseProfileScraper()
    
    # Test data
    horses_data = {
        'Major Tom': {
            'race_number': '7',
            'program_number': '2'
        }
    }
    
    print("Testing complete workflow with Major Tom...")
    results = scraper.scrape_multiple_horses_with_data(['Major Tom'], horses_data, delay=0)
    
    if results:
        print(f"\n=== Results ===")
        for horse_name, data in results.items():
            horse_info = data['horse_info']
            race_history = data['race_history']
            
            print(f"Horse: {horse_name}")
            print(f"Age: {horse_info.get('age')}, Sex: {horse_info.get('sex')}")
            print(f"Trainer: {horse_info.get('trainer')}")
            print(f"Race History ({len(race_history)} races):")
            
            for i, race in enumerate(race_history, 1):
                print(f"  {i}. Race #{race.get('race_number')}, Program #{race.get('program_number')}")
                print(f"     Date: {race.get('race_date')}, Track: {race.get('track')}")
                print(f"     Distance: {race.get('distance')}, Surface: {race.get('surface')}")
                print(f"     Finish: {race.get('finish_position')}, Time: {race.get('time')}")
        
        # Test CSV export
        print(f"\n=== Testing CSV Export ===")
        scraper.save_to_csv(results, "test_major_tom_complete.csv")
        
        # Test JSON export
        print(f"=== Testing JSON Export ===")
        scraper.save_to_json(results, "test_major_tom_complete.json")
        
        print("\nTest completed successfully!")
    else:
        print("No results found")

if __name__ == "__main__":
    test_complete_workflow()