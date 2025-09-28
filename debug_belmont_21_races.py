#!/usr/bin/env python3
"""
Debug Belmont Park HTML structure
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_belmont_page():
    """Belmont Park sayfasının yapısını incele"""
    
    url = "https://entries.horseracingnation.com/entries-results/belmont-at-aqueduct/2025-09-28"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"Belmont Park sayfası inceleniyor: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tüm h2 başlıklarını bul
        h2_tags = soup.find_all('h2')
        print(f"\n=== Bulunan {len(h2_tags)} H2 başlık ===")
        
        race_headers = []
        for i, h2 in enumerate(h2_tags, 1):
            h2_text = h2.get_text().strip()
            print(f"{i:2d}. {repr(h2_text)}")
            
            # Race içeren başlıkları ayrıca işaretle
            if 'Race' in h2_text and '#' in h2_text:
                race_num_match = re.search(r'Race\s*#?\s*(\d+)', h2_text)
                if race_num_match:
                    race_num = race_num_match.group(1)
                    race_headers.append((race_num, h2_text))
                    print(f"    → YAريŞ {race_num} olarak algılanacak!")
        
        print(f"\n=== Yarış olarak algılanacak başlıklar: {len(race_headers)} ===")
        for race_num, header in race_headers:
            print(f"  Yarış {race_num}: {repr(header)}")
        
        # Sayfa tarihini kontrol et
        print(f"\n=== Sayfa Tarihi Kontrolü ===")
        title_elem = soup.find('title')
        if title_elem:
            print(f"Title: {title_elem.get_text()}")
        
        # Tarih bilgisi içeren elementleri bul
        date_elements = soup.find_all(text=re.compile(r'2025-09-28|September 28|Sep 28'))
        print(f"Tarih içeren elementler: {len(date_elements)}")
        for elem in date_elements[:5]:  # İlk 5'ini göster
            print(f"  - {repr(str(elem).strip())}")
        
        # Güncel yarışları vs eski yarışları ayırt etmek için container'ları kontrol et
        print(f"\n=== Container Analizi ===")
        containers = soup.find_all(['div', 'section'], class_=re.compile(r'race|entry|result', re.I))
        print(f"Race/entry/result içeren {len(containers)} container bulundu")
        
        for i, container in enumerate(containers[:3]):  # İlk 3'ü incele
            print(f"Container {i+1}:")
            print(f"  Tag: {container.name}")
            print(f"  Class: {container.get('class')}")
            h2_in_container = container.find_all('h2')
            print(f"  H2 sayısı: {len(h2_in_container)}")
            if h2_in_container:
                for h2 in h2_in_container[:2]:
                    print(f"    - {repr(h2.get_text().strip())}")
        
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    debug_belmont_page()