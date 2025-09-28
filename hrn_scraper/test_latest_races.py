#!/usr/bin/env python3
"""
Test script - Sadece birkaç at için test yapalım
"""

import csv
from horse_profile_scraper import HorseProfileScraper
import logging

# Logging ayarı
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Test için sadece ilk 5 atı al
    test_horses = [
        "Tiger of the Sea",
        "Lawless World", 
        "Tammy Baby",
        "Zio Jo",
        "Gaming"
    ]
    
    print(f"Testing with {len(test_horses)} horses (latest race only):")
    for horse in test_horses:
        print(f"  - {horse}")
    
    # Scraper'ı başlat
    scraper = HorseProfileScraper()
    
    print(f"\nStarting to scrape latest races...")
    
    # Test atlarını scrape et (1 saniye delay ile)
    results = scraper.scrape_multiple_horses(test_horses, delay=1)
    
    if results:
        # Test sonuçlarını kaydet
        scraper.save_to_csv(results, "test_horse_latest_races.csv")
        scraper.save_to_json(results, "test_horse_latest_races.json")
        
        # Özet bilgi
        total_races = sum(len(data['race_history']) for data in results.values())
        
        print(f"\n=== TEST COMPLETED ===")
        print(f"Successful horses: {len(results)}/{len(test_horses)}")
        print(f"Total race records: {total_races} (should be {len(results)} for latest only)")
        
        print(f"\nLatest race details:")
        for horse_name, data in results.items():
            if data['race_history']:
                race = data['race_history'][0]
                print(f"  {horse_name}: {race.get('date')} - {race.get('track')} - {race.get('distance')} - {race.get('surface')} - Finish: {race.get('finish_position')}")
            else:
                print(f"  {horse_name}: No race data")
        
        print(f"\nOutput files:")
        print(f"  📊 test_horse_latest_races.csv")
        print(f"  📄 test_horse_latest_races.json")
    
    else:
        print("❌ No results obtained")


if __name__ == "__main__":
    main()