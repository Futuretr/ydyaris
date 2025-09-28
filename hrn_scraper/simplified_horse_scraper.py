#!/usr/bin/env python3
"""
Basitleştirilmiş at profil çekici - Sadece gerekli verileri çeker
Simplified horse profile scraper - Only extracts essential data

Çekilen veriler / Extracted data:
- Pistin türü (surface) 
- Uzunluğu (distance)
- Time (yarış zamanı)
- Atın ismi (horse name)
- Kaçıncı koşuda koşacağı (race number) 
- Koşu numarası (program number)
"""

import csv
import os
import sys
from horse_profile_scraper import HorseProfileScraper
import logging
import json

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


def extract_essential_data(horse_data):
    """Sadece gerekli verileri çıkarır"""
    if not horse_data:
        return None
        
    # Sadece gerekli alanları seç
    essential = {
        'horse_name': horse_data.get('horse_name', ''),
        'race_number': horse_data.get('race_number', ''),
        'program_number': horse_data.get('program_number', ''),
        'latest_surface': horse_data.get('latest_surface', ''),  # Pistin türü
        'latest_distance': horse_data.get('latest_distance', ''),  # Uzunluk
        'latest_time': horse_data.get('latest_time', '')  # Yarış zamanı
    }
    
    return essential


def main():
    """Ana fonksiyon"""
    if len(sys.argv) != 2:
        print("Usage: python simplified_horse_scraper.py <entries_csv_file>")
        print("Example: python simplified_horse_scraper.py laurel-park_2025_09_28_laurel-park_entries.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"❌ Dosya bulunamadı: {csv_file}")
        sys.exit(1)
    
    # Çıktı dosya adlarını hazırla
    base_name = csv_file.replace('_entries.csv', '')
    simplified_csv = f"{base_name}_simplified.csv"
    simplified_json = f"{base_name}_simplified.json"
    
    print(f"🔄 Başlıyor: {csv_file}")
    print(f"📝 Çıktı: {simplified_csv}")
    
    # At listesini oku
    horses_data = read_horses_from_csv(csv_file)
    if not horses_data:
        print("❌ CSV dosyasından at bulunamadı!")
        sys.exit(1)
    
    # Horse profile scraper'ı başlat
    scraper = HorseProfileScraper()
    
    results = []
    successful = 0
    failed = 0
    
    print(f"\n🏇 {len(horses_data)} at için profil verileri çekiliyor...")
    
    for i, (horse_name, race_info) in enumerate(horses_data.items(), 1):
        print(f"[{i:3d}/{len(horses_data)}] {horse_name}", end=" ... ")
        
        try:
            # At profil verisini çek
            horse_data = scraper.scrape_horse_profile(horse_name)
            
            if horse_data:
                # Race ve program numaralarını ekle
                horse_data['race_number'] = race_info['race_number']
                horse_data['program_number'] = race_info['program_number']
                
                # Sadece gerekli verileri çıkar
                essential_data = extract_essential_data(horse_data)
                
                if essential_data:
                    results.append(essential_data)
                    successful += 1
                    print("✅")
                else:
                    failed += 1
                    print("❌ Veri çıkarılamadı")
            else:
                failed += 1
                print("❌ Profil bulunamadı")
                
        except Exception as e:
            failed += 1
            print(f"❌ Hata: {e}")
    
    print(f"\n📊 Sonuçlar:")
    print(f"   ✅ Başarılı: {successful}")
    print(f"   ❌ Başarısız: {failed}")
    print(f"   📋 Toplam: {len(horses_data)}")
    
    if results:
        # CSV dosyasına kaydet
        fieldnames = [
            'race_number',
            'program_number', 
            'horse_name',
            'latest_surface',
            'latest_distance',
            'latest_time'
        ]
        
        with open(simplified_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        # JSON dosyasına kaydet
        with open(simplified_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Veriler kaydedildi:")
        print(f"   📄 CSV: {simplified_csv}")
        print(f"   📄 JSON: {simplified_json}")
        
        # Örnek veri göster
        print(f"\n📋 Örnek veriler (ilk 3 kayıt):")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. {result['horse_name']}: "
                  f"Koşu {result['race_number']}/{result['program_number']}, "
                  f"{result['latest_surface']}, "
                  f"{result['latest_distance']}, "
                  f"{result['latest_time']}")
        
        if len(results) > 3:
            print(f"   ... ve {len(results)-3} kayıt daha")
    
    else:
        print("❌ Hiç veri çekilemedi!")


if __name__ == "__main__":
    main()