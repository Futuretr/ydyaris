#!/usr/bin/env python3
"""
Multi-track essential scraper tester
Entegre sistemi test eder
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Multi-track scraper'dan sadece gerekli fonksiyonu içe aktar
from multi_track_scraper import scrape_horse_profiles_for_track, TRACKS

def test_integrated_system():
    """Entegre sistemi test et"""
    print("🧪 Entegre Multi-Track Essential Scraper Testi")
    print("="*50)
    
    # Mevcut Woodbine entries dosyasını test et
    test_file = "woodbine_2025_09_28_woodbine_entries.csv"
    
    if not os.path.exists(test_file):
        print(f"❌ Test dosyası bulunamadı: {test_file}")
        return
        
    print(f"📂 Test dosyası: {test_file}")
    print(f"🎯 Woodbine track bilgisi: {TRACKS[2]}")
    
    print("\n🔄 Essential scraper fonksiyonu test ediliyor...")
    
    try:
        result = scrape_horse_profiles_for_track(test_file)
        print(f"\n✅ Test tamamlandı! {result} başarılı at profili çekildi.")
        
        # Çıktı dosyalarını kontrol et
        expected_csv = test_file.replace('_entries.csv', '_essential.csv')
        expected_json = test_file.replace('_entries.csv', '_essential.json')
        
        if os.path.exists(expected_csv):
            print(f"📄 CSV çıktısı oluşturuldu: {expected_csv}")
        
        if os.path.exists(expected_json):
            print(f"📄 JSON çıktısı oluşturuldu: {expected_json}")
            
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    test_integrated_system()