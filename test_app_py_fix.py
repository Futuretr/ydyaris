#!/usr/bin/env python3
"""
Test yeni app.py race_sections fix
"""

import requests
from bs4 import BeautifulSoup
import re

def test_app_py_fix():
    """Yeni app.py race_sections fix'ini test et"""
    
    url = "https://entries.horseracingnation.com/entries-results/belmont-at-aqueduct/2025-09-28"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"Yeni app.py fix test: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Eski yöntem (app.py fix öncesi)
        print("\n=== ESKİ YÖNTEMİN SONUCU ===")
        all_divs = soup.find_all('div')
        old_race_sections = []
        for div in all_divs:
            if div.get_text() and 'Race' in div.get_text():
                old_race_sections.append(div.parent if div.parent else div)
        old_race_sections = list(set(old_race_sections))
        print(f"Eski yöntem: {len(old_race_sections)} race_sections")
        
        # Yeni yöntem (app.py fix sonrası)
        print("\n=== YENİ YÖNTEMİN SONUCU ===")
        h2_headers = soup.find_all('h2')
        new_race_sections = []
        for h2 in h2_headers:
            h2_text = h2.get_text()
            if 'Race' in h2_text and '#' in h2_text:
                print(f"Yarış başlığı bulundu: {repr(h2_text.strip())}")
                # Bu bir yarış başlığı, sonraki elementi al
                next_elem = h2.find_next_sibling()
                if next_elem:
                    new_race_sections.append(next_elem)
                    print(f"  → Sonraki element: {next_elem.name}, class: {next_elem.get('class')}")
                else:
                    new_race_sections.append(h2)
                    print(f"  → H2'yi kendisi kullanıldı")
        
        print(f"\nYeni yöntem: {len(new_race_sections)} race_sections")
        
        # Sonuçları karşılaştır
        print(f"\n=== KARŞILAŞTIRMA ===")
        print(f"Eski yöntem: {len(old_race_sections)} → 21 (YANLIŞ)")
        print(f"Yeni yöntem: {len(new_race_sections)} → 9 olmalı (DOĞRU)")
        
        # Yeni yöntemin her biri için horse link kontrolü
        if new_race_sections:
            print(f"\n=== İLK RACE_SECTION'DAKİ AT LİNKLERİ ===")
            first_section = new_race_sections[0]
            horse_links = first_section.find_all('a', href=True)
            horse_count = 0
            for link in horse_links:
                href = link.get('href', '')
                if href and '/horse/' in str(href):
                    horse_name = link.get_text(strip=True)
                    if horse_name and len(horse_name) > 1:
                        horse_count += 1
                        if horse_count <= 5:
                            print(f"  Horse {horse_count}: {horse_name}")
            print(f"  Toplam horse link: {horse_count}")
        
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app_py_fix()