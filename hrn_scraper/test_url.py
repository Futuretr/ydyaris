#!/usr/bin/env python3
"""
Test URL'yi kontrol et
"""

import requests
from datetime import datetime

def test_url(url):
    """URL'yi test et"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        print(f"Testing URL: {url}")
        response = session.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ URL çalışıyor!")
            print(f"Content length: {len(response.text)} characters")
            
            # Santa Anita içeriği var mı kontrol et
            if "santa" in response.text.lower() or "anita" in response.text.lower():
                print("✅ Santa Anita içeriği bulundu!")
            else:
                print("❌ Santa Anita içeriği bulunamadı")
                
            # Race içeriği var mı kontrol et
            if "race" in response.text.lower():
                print("✅ Race içeriği bulundu!")
                race_count = response.text.lower().count("race")
                print(f"'race' kelimesi {race_count} kez geçiyor")
            else:
                print("❌ Race içeriği bulunamadı")
                
        else:
            print(f"❌ URL çalışmıyor! Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    # Test URLs
    test_urls = [
        "https://entries.horseracingnation.com/races/2024-12-27/santa-anita",
        "https://entries.horseracingnation.com/entries-results/2024-12-27",
        "https://entries.horseracingnation.com/entries-results/santa-anita/2024-12-27"
    ]
    
    for url in test_urls:
        test_url(url)
        print("-" * 60)