#!/usr/bin/env python3
"""
Debug HRN Scraper - 21 race problem
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'hrn_scraper'))

from hrn_scraper.hrn_scraper import HorseRacingNationScraper
import requests
from bs4 import BeautifulSoup
import re

def debug_scraper_races():
    """Scraper'ın neden 21 yarış bulduğunu debug et"""
    
    url = "https://entries.horseracingnation.com/entries-results/belmont-at-aqueduct/2025-09-28"
    
    scraper = HorseRacingNationScraper()
    
    print(f"Belmont Park scraper debug başlıyor: {url}")
    
    try:
        response = scraper.session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scraper'ın yaptığı gibi h2'leri bul
        h2_tags = soup.find_all('h2')
        print(f"\n=== {len(h2_tags)} H2 başlık bulundu ===")
        
        races_found = []
        
        for i, h2 in enumerate(h2_tags, 1):
            h2_text = h2.get_text()
            print(f"\n{i:2d}. H2: {repr(h2_text)}")
            
            if 'Race' in h2_text and '#' in h2_text:
                print(f"    → Race içeriyor, işleniyor...")
                
                # Yarış numarasını çıkar - scraper'ın yaptığı gibi
                race_num_match = re.search(r'Race\s*#?\s*(\d+)', h2_text)
                if race_num_match:
                    race_num = int(race_num_match.group(1))
                    print(f"    → Yarış numarası: {race_num}")
                    
                    # Saati çıkar
                    time_match = re.search(r'(\d+:\d+\s*[AP]M)', h2_text)
                    race_time = time_match.group(1) if time_match else "Unknown"
                    print(f"    → Yarış saati: {race_time}")
                    
                    races_found.append({
                        'number': race_num,
                        'time': race_time,
                        'header': h2_text.strip(),
                        'h2_index': i
                    })
                    
                    print(f"    ✅ Yarış {race_num} eklendi")
                else:
                    print(f"    ❌ Yarış numarası bulunamadı")
            else:
                print(f"    → Race/# içermiyor, atlanıyor")
        
        print(f"\n=== Toplam {len(races_found)} yarış bulundu ===")
        for race in races_found:
            print(f"  {race['number']:2d}. {race['time']:8s} | H2 #{race['h2_index']:2d} | {repr(race['header'][:50])}...")
        
        # Eğer 21 yarış bulunuyorsa, neyin yanlış olduğunu anla
        if len(races_found) > 9:
            print(f"\n❌ PROBLEM: {len(races_found)} yarış bulundu ama olması gereken 9!")
            print("Fazladan bulunanlar:")
            for race in races_found[9:]:
                print(f"  - Yarış {race['number']}: {repr(race['header'])}")
        
        # Şimdi scraper'ın gerçek metodunu çalıştır
        print(f"\n=== Gerçek scraper metodunu test et ===")
        track_data = scraper.scrape_track_data(url, "Belmont Park")
        
        if track_data:
            actual_races = track_data.get('races', [])
            print(f"Scraper {len(actual_races)} yarış buldu:")
            for i, race in enumerate(actual_races[:10], 1):  # İlk 10'unu göster
                print(f"  {i:2d}. Yarış {race.get('race_number')}: {race.get('post_time')} | {len(race.get('entries', []))} at")
        
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_scraper_races()