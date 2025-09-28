#!/usr/bin/env python3
"""
Debug app.py race_sections problem
"""

import requests
from bs4 import BeautifulSoup

def debug_app_py_race_sections():
    """App.py'nin neden 21 race_section bulduğunu debug et"""
    
    url = "https://entries.horseracingnation.com/entries-results/belmont-at-aqueduct/2025-09-28"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"App.py race_sections debug başlıyor: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"\n=== App.py'nin yaptığı gibi race_sections araması ===")
        
        # App.py'deki sırayla elementleri ara
        
        print("1. 'section', class_='race-summary' arıyor...")
        race_sections_1 = soup.find_all('section', class_='race-summary')
        print(f"   → {len(race_sections_1)} element buldu")
        
        print("2. 'div', class_='race-card' arıyor...")
        race_sections_2 = soup.find_all('div', class_='race-card')
        print(f"   → {len(race_sections_2)} element buldu")
        
        print("3. 'section', class_='race' arıyor...")
        race_sections_3 = soup.find_all('section', class_='race')
        print(f"   → {len(race_sections_3)} element buldu")
        
        print("4. 'div', attrs={'data-race': True} arıyor...")
        race_sections_4 = soup.find_all('div', attrs={'data-race': True})
        print(f"   → {len(race_sections_4)} element buldu")
        
        # İlk sorgu sonucu
        race_sections = race_sections_1 or race_sections_2 or race_sections_3 or race_sections_4
        
        print(f"\nİlk sorgu sonucu: {len(race_sections) if race_sections else 0} element")
        
        # Eğer hiç bulunamadıysa alternatif yöntem
        if not race_sections:
            print("\n5. Alternatif yöntem: 'Race' içeren div'leri arıyor...")
            all_divs = soup.find_all('div')
            race_sections_alt = []
            for div in all_divs:
                div_text = div.get_text()
                if div_text and 'Race' in div_text:
                    parent = div.parent if div.parent else div
                    race_sections_alt.append(parent)
            
            print(f"   → {len(race_sections_alt)} 'Race' içeren div buldu")
            
            # Tekrarları kaldır
            race_sections = list(set(race_sections_alt))
            print(f"   → Tekrar kaldırıldıktan sonra: {len(race_sections)} element")
        
        print(f"\n=== Final sonuç: {len(race_sections)} race_sections ===")
        
        if race_sections:
            print("\nİlk 10 race_section'ın içeriği:")
            for i, section in enumerate(race_sections[:10], 1):
                section_text = section.get_text()[:100].replace('\n', ' ').strip()
                print(f"{i:2d}. Tag: {section.name}, Class: {section.get('class')}")
                print(f"    Text preview: {repr(section_text)}")
        
        # Horse link'lerini de kontrol et
        if race_sections:
            print(f"\n=== İlk race_section'daki horse link'leri ===")
            first_section = race_sections[0]
            horse_links = first_section.find_all('a', href=True)
            horse_count = 0
            for link in horse_links:
                href = link.get('href', '')
                if href and '/horse/' in str(href):
                    horse_name = link.get_text(strip=True)
                    if horse_name and len(horse_name) > 1:
                        horse_count += 1
                        if horse_count <= 5:  # İlk 5'ini göster
                            print(f"  Horse {horse_count}: {horse_name}")
            print(f"  Toplam horse link: {horse_count}")
        
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_app_py_race_sections()