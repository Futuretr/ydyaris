#!/usr/bin/env python3
"""
Integration script - Entries CSV dosyasındaki tüm atların profil verilerini çeker
"""

import csv
import os
import sys
from horse_profile_scraper import HorseProfileScraper
import logging

# Logging ayarı
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_horses_from_csv(csv_file):
    """Entries CSV dosyasından at isimlerini ve numaralarını çıkarır"""
    horses_data = {}  # horse_name -> {race_number, program_number}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                horse_name = row.get('horse_name', '').strip()
                race_number = row.get('race_number', '').strip()
                program_number = row.get('program_number', '').strip()
                
                if horse_name:
                    horses_data[horse_name] = {
                        'race_number': race_number,
                        'program_number': program_number
                    }
        
        logger.info(f"Found {len(horses_data)} unique horses in {csv_file}")
        return horses_data
        
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_file}: {e}")
        return {}


def main():
    """Ana fonksiyon"""
    if len(sys.argv) != 2:
        print("Usage: python scrape_all_horse_profiles.py <entries_csv_file>")
        print("Example: python scrape_all_horse_profiles.py santa-anita_2024_12_27_santa-anita_entries.csv")
        sys.exit(1)
    
    entries_csv = sys.argv[1]
    
    # Dosya var mı kontrol et
    if not os.path.exists(entries_csv):
        logger.error(f"File not found: {entries_csv}")
        sys.exit(1)
    
    # At isimlerini ve numaralarını oku
    horses_data = read_horses_from_csv(entries_csv)
    if not horses_data:
        logger.error("No horses found in the CSV file")
        sys.exit(1)
    
    horse_names = list(horses_data.keys())
    print(f"Found {len(horse_names)} horses to scrape:")
    for i, horse in enumerate(horse_names[:10], 1):  # İlk 10'unu göster
        race_num = horses_data[horse]['race_number']
        prog_num = horses_data[horse]['program_number']
        print(f"  {i}. {horse} (R{race_num}, #{prog_num})")
    if len(horse_names) > 10:
        print(f"  ... and {len(horse_names) - 10} more")
    
    # Kullanıcıdan onay al
    response = input(f"\nContinue scraping profiles for {len(horse_names)} horses? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled")
        sys.exit(0)
    
    # Scraper'ı başlat
    scraper = HorseProfileScraper()
    
    print(f"\nStarting to scrape {len(horse_names)} horse profiles...")
    print("This may take a while due to rate limiting...")
    
    # Tüm atları scrape et (1 saniye delay ile - sadece son yarış)
    results = scraper.scrape_multiple_horses_with_data(horse_names, horses_data, delay=1)
    
    if results:
        # Dosya isimlerini belirle
        base_name = os.path.splitext(entries_csv)[0]
        profiles_csv = f"{base_name}_horse_profiles.csv"
        profiles_json = f"{base_name}_horse_profiles.json"
        
        # Sonuçları kaydet
        scraper.save_to_csv(results, profiles_csv)
        scraper.save_to_json(results, profiles_json)
        
        # Özet bilgi
        total_races = sum(len(data['race_history']) for data in results.values())
        successful_horses = len(results)
        failed_horses = len(horse_names) - successful_horses
        
        print(f"\n=== SCRAPING COMPLETED ===")
        print(f"Successful horses: {successful_horses}/{len(horse_names)}")
        print(f"Failed horses: {failed_horses}")
        print(f"Total race records: {total_races}")
        print(f"\nOutput files:")
        print(f"  📊 CSV: {profiles_csv}")
        print(f"  📄 JSON: {profiles_json}")
        
        if failed_horses > 0:
            failed_list = [h for h in horse_names if h not in results]
            print(f"\nFailed horses:")
            for horse in failed_list[:5]:  # İlk 5'ini göster
                print(f"  ❌ {horse}")
            if len(failed_list) > 5:
                print(f"  ... and {len(failed_list) - 5} more")
    
    else:
        print("❌ No results obtained")


if __name__ == "__main__":
    main()