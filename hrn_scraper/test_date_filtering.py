#!/usr/bin/env python3
"""
Test script - Test date filtering for Major Tom
"""

from horse_profile_scraper import HorseProfileScraper
import logging

# Logging ayarı
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Test Major Tom with date filtering"""
    # Test horses that had old dates
    test_horses = ["Major Tom", "Beyond Brilliant", "Johannes"]
    
    print(f"Testing date filtering for problem horses...")
    
    # Scraper'ı başlat
    scraper = HorseProfileScraper()
    
    for horse_name in test_horses:
        print(f"\n=== Testing {horse_name} ===")
        result = scraper.scrape_horse_profile(horse_name)
        
        if result and result['race_history']:
            race = result['race_history'][0]
            date = race.get('date', 'N/A')
            track = race.get('track', 'N/A') 
            time_val = race.get('time', 'N/A')
            print(f"  ✅ Found recent race: {date} at {track}, time: {time_val}")
        else:
            print(f"  ❌ No recent races found (all races too old)")

if __name__ == "__main__":
    main()