#!/usr/bin/env python3
"""
Test script - Test scraping with race numbers and program numbers
"""

from horse_profile_scraper import HorseProfileScraper
import logging

# Logging ayarı
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Test with a few horses including race and program numbers"""
    # Test horses with their CORRECT data from entries CSV
    horses_data = {
        "Tiger of the Sea": {"race_number": "1", "program_number": "1"},
        "Miso Phansy": {"race_number": "10", "program_number": "13"},  # CORRECTED
        "Beyond Brilliant": {"race_number": "8", "program_number": "6"}  # CORRECTED
    }
    
    horse_names = list(horses_data.keys())
    print(f"Testing scraping with race/program numbers for {len(horse_names)} horses...")
    
    # Show test data
    for horse in horse_names:
        race_num = horses_data[horse]['race_number']
        prog_num = horses_data[horse]['program_number']
        print(f"  - {horse} (R{race_num}, #{prog_num})")
    
    # Scraper'ı başlat
    scraper = HorseProfileScraper()
    
    # Test horses'ları scrape et
    results = scraper.scrape_multiple_horses_with_data(horse_names, horses_data, delay=1)
    
    if results:
        # Enhanced CSV'ye kaydet
        scraper.save_to_csv(results, "test_enhanced_horse_profiles.csv")
        scraper.save_to_json(results, "test_enhanced_horse_profiles.json")
        
        print(f"\n✅ Scraping completed!")
        print(f"Results saved to:")
        print(f"  📊 test_enhanced_horse_profiles.csv")
        print(f"  📄 test_enhanced_horse_profiles.json")
        
        # Show summary
        total_races = sum(len(data['race_history']) for data in results.values())
        print(f"\nSummary:")
        print(f"  Horses processed: {len(results)}")
        print(f"  Total race records: {total_races}")
        
    else:
        print("❌ No results obtained")

if __name__ == "__main__":
    main()