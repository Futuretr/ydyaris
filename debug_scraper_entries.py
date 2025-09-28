#!/usr/bin/env python3
"""
Debug scraper entry format
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'hrn_scraper'))

from hrn_scraper.hrn_scraper import HorseRacingNationScraper

def debug_scraper_entries():
    """Scraper'ın entry formatını debug et"""
    
    url = "https://entries.horseracingnation.com/entries-results/belmont-at-aqueduct/2025-09-28"
    
    scraper = HorseRacingNationScraper()
    track_data = scraper.scrape_track_data(url, "Belmont Park")
    
    if not track_data or not track_data.get('races'):
        print("Scraper veri çekemedi")
        return
    
    races = track_data['races']
    print(f"Bulunan yarış sayısı: {len(races)}")
    
    # İlk yarışın ilk entry'sini debug et
    first_race = races[0]
    print(f"\nİlk yarış bilgisi:")
    print(f"  race_number: {first_race.get('race_number')}")
    print(f"  entries sayısı: {len(first_race.get('entries', []))}")
    
    if first_race.get('entries'):
        first_entry = first_race['entries'][0]
        print(f"\nİlk entry'nin anahtarları:")
        for key, value in first_entry.items():
            print(f"  {key}: {repr(value)}")
    
    # İlk 3 entry'yi göster
    print(f"\nİlk 3 entry:")
    entries = first_race.get('entries', [])
    for i, entry in enumerate(entries[:3], 1):
        print(f"\n{i}. Entry:")
        print(f"  post_position: {repr(entry.get('post_position', 'YOK'))}")
        print(f"  horse_name: {repr(entry.get('horse_name', 'YOK'))}")
        print(f"  program_number: {repr(entry.get('program_number', 'YOK'))}")
        print(f"  trainer: {repr(entry.get('trainer', 'YOK'))}")
        print(f"  jockey: {repr(entry.get('jockey', 'YOK'))}")

if __name__ == "__main__":
    debug_scraper_entries()