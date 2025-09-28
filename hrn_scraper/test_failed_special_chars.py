#!/usr/bin/env python3
"""
Test failed horses with special characters
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from horse_profile_scraper import HorseProfileScraper
import csv

def read_horses_from_csv(csv_file):
    """CSV'den at isimlerini ve numaralarını oku"""
    horses_data = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                horse_name = row['Horse'].strip()
                race_number = row['Race'].strip()
                program_number = row['Program Number'].strip()
                
                horses_data[horse_name] = {
                    'race_number': race_number,
                    'program_number': program_number
                }
        
        return horses_data
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {}

def test_failed_horses_with_special_chars():
    """Test horses that failed in the original scrape and contain special characters"""
    
    # Failed horses from the log that contain ' or .
    failed_horses_with_special_chars = [
        "Cash's Candy",
        "Sparta F. C.",
        "Sally's Wish", 
        "Nesso's Lastharrah",
        "Kale's Angel",
        "Lee's Baby Girl"
    ]
    
    scraper = HorseProfileScraper()
    
    print(f"Testing {len(failed_horses_with_special_chars)} failed horses with special characters...")
    
    successful = 0
    
    for horse_name in failed_horses_with_special_chars:
        print(f"\nTesting: {horse_name}")
        formatted = scraper._format_horse_name_for_url(horse_name)
        print(f"  URL slug: {formatted}")
        
        result = scraper.scrape_horse_profile(horse_name)
        
        if result and result.get('race_history'):
            successful += 1
            race_history = result.get('race_history', [])
            print(f"  ✅ SUCCESS - Found {len(race_history)} races")
            if race_history:
                latest_race = race_history[0]
                date = latest_race.get('race_date', latest_race.get('date', 'N/A'))
                track = latest_race.get('track', 'N/A')
                print(f"      Latest: {date} at {track}")
        else:
            print(f"  ❌ FAILED - No races found")
    
    print(f"\n=== SUMMARY ===")
    print(f"Successful: {successful}/{len(failed_horses_with_special_chars)}")

if __name__ == "__main__":
    test_failed_horses_with_special_chars()