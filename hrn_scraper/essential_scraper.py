#!/usr/bin/env python3
"""
En basit scraper - Sadece gerekli verileri çeker ve düzgün çıktı verir
Simple essential scraper - Only extracts necessary data with clean output

Çekilen veriler / Extracted data:
- race_number (koşu numarası)
- program_number (koşu sırası)
- horse_name (atın ismi)  
- latest_surface (pistin türü)
- latest_distance (uzunluk)
- latest_time (yarış zamanı)
- latest_finish_position (derece)
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


def main():
    """Ana fonksiyon"""
    if len(sys.argv) != 2:
        print("Usage: python essential_scraper.py <entries_csv_file>")
        print("Example: python essential_scraper.py laurel-park_2025_09_28_laurel-park_entries.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"❌ Dosya bulunamadı: {csv_file}")
        sys.exit(1)
    
    # Çıktı dosya adlarını hazırla
    base_name = csv_file.replace('_entries.csv', '')
    output_csv = f"{base_name}_essential.csv"
    output_json = f"{base_name}_essential.json"
    
    print(f"🔄 Başlıyor: {csv_file}")
    print(f"📝 Çıktı: {output_csv}")
    
    # Horse profile scraper'ı başlat
    scraper = HorseProfileScraper()
    
    results = []
    successful = 0
    failed = 0
    
    # CSV dosyasını okuyup işle
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            horses = list(reader)
        
        total_horses = len(horses)
        print(f"\\n🏇 {total_horses} at bulundu, profil verileri çekiliyor...")
        
        for i, row in enumerate(horses, 1):
            horse_name = row.get('horse_name', '').strip()
            race_number = row.get('race_number', '').strip()
            program_number = row.get('program_number', '').strip()
            
            if not horse_name:
                print(f"[{i:3d}/{total_horses}] ⚠️ Boş at ismi atlanıyor")
                continue
                
            print(f"[{i:3d}/{total_horses}] {horse_name}", end=" ... ")
            
            try:
                # At profil verisini çek
                horse_data = scraper.scrape_horse_profile(horse_name)
                
                if horse_data and horse_data.get('race_history') and len(horse_data['race_history']) > 0:
                    # En son yarış verilerini al
                    latest_race = horse_data['race_history'][0]  # İlk eleman en son yarış
                    
                    # Sonucu hazırla
                    result = {
                        'race_number': race_number,
                        'program_number': program_number,
                        'horse_name': horse_name,
                        'latest_surface': latest_race.get('surface', ''),
                        'latest_distance': latest_race.get('distance', ''),
                        'latest_time': latest_race.get('time', ''),
                        'latest_finish_position': latest_race.get('finish_position', '')
                    }
                    
                    results.append(result)
                    successful += 1
                    print("✅")
                    
                    # İlerleme detayı göster
                    print(f"      → {result['latest_surface']} | {result['latest_distance']} | {result['latest_time']} | {result['latest_finish_position']}. sıra")
                    
                else:
                    failed += 1
                    print("❌ Veri bulunamadı")
                    
                    # Başarısız durumda da temel bilgileri ekle
                    result = {
                        'race_number': race_number,
                        'program_number': program_number,
                        'horse_name': horse_name,
                        'latest_surface': '',
                        'latest_distance': '',
                        'latest_time': '',
                        'latest_finish_position': ''
                    }
                    results.append(result)
                    
            except Exception as e:
                failed += 1
                print(f"❌ Hata: {str(e)[:50]}...")
                
                # Hata durumunda da temel bilgileri ekle
                result = {
                    'race_number': race_number,
                    'program_number': program_number,
                    'horse_name': horse_name,
                    'latest_surface': '',
                    'latest_distance': '',
                    'latest_time': '',
                    'latest_finish_position': ''
                }
                results.append(result)
    
    except Exception as e:
        print(f"❌ CSV dosyası okuma hatası: {e}")
        sys.exit(1)
    
    print(f"\\n📊 Sonuçlar:")
    print(f"   ✅ Başarılı: {successful}")
    print(f"   ❌ Başarısız: {failed}")
    print(f"   📋 Toplam: {len(results)}")
    
    if results:
        # CSV dosyasına kaydet
        fieldnames = [
            'race_number',
            'program_number', 
            'horse_name',
            'latest_surface',
            'latest_distance',
            'latest_time',
            'latest_finish_position'
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        # JSON dosyasına kaydet
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\\n💾 Veriler kaydedildi:")
        print(f"   📄 CSV: {output_csv}")
        print(f"   📄 JSON: {output_json}")
        
        # Başarılı örnekleri göster
        successful_examples = [r for r in results if r['latest_time']]
        if successful_examples:
            print(f"\\n📋 Başarılı örnekler (ilk 3):")
            for i, result in enumerate(successful_examples[:3], 1):
                print(f"   {i}. {result['horse_name']}: "
                      f"Koşu {result['race_number']}/{result['program_number']}, "
                      f"{result['latest_surface']}, "
                      f"{result['latest_distance']}, "
                      f"{result['latest_time']}, "
                      f"{result['latest_finish_position']}. sıra")
        
        print(f"\\n🎯 Özet: {len(successful_examples)}/{len(results)} kayıtta tam veri mevcut")
    
    else:
        print("❌ Hiç veri çekilemedi!")


if __name__ == "__main__":
    main()