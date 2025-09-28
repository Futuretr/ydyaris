#!/usr/bin/env python3
"""
Test script - Simplified horse profile scraping (only essential fields)
"""

from horse_profile_scraper import HorseProfileScraper
import logging

# Logging ayarı
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Test with a few horses"""
    # Test horses
    test_horses = [
        "Tiger of the Sea",
        "Miso Phansy", 
        "Beyond Brilliant"
    ]
    
    print(f"Testing simplified scraping with {len(test_horses)} horses...")
    
    # Scraper'ı başlat
    scraper = HorseProfileScraper()
    
    # Test horses'ları scrape et
    results = scraper.scrape_multiple_horses(test_horses, delay=1)
    
    if results:
        # Simplified CSV'ye kaydet
        scraper.save_to_csv(results, "test_simplified_horse_profiles.csv")
        scraper.save_to_json(results, "test_simplified_horse_profiles.json")
        
        print(f"\n✅ Scraping completed!")
        print(f"Results saved to:")
        print(f"  📊 test_simplified_horse_profiles.csv")
        print(f"  📄 test_simplified_horse_profiles.json")
        
        # Show summary
        total_races = sum(len(data['race_history']) for data in results.values())
        print(f"\nSummary:")
        print(f"  Horses processed: {len(results)}")
        print(f"  Total race records: {total_races}")
        
    else:
        print("❌ No results obtained")

if __name__ == "__main__":
    main()