#!/usr/bin/env python3
"""
Debug single race entries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hrn_scraper import HorseRacingNationScraper

def debug_single_race():
    scraper = HorseRacingNationScraper()
    url = "https://entries.horseracingnation.com/entries-results/santa-anita/2025-09-27"
    
    print("Scraping single race for debugging...")
    data = scraper.scrape_track_data(url, "Santa Anita")
    
    if data and data['races']:
        race = data['races'][0]  # İlk yarış
        print(f"\nFirst Race Details:")
        print(f"Race Number: {race['race_number']}")
        print(f"Entries: {len(race['entries'])}")
        print(f"Results: {len(race.get('results', {}).get('finishing_order', []))}")
        
        if race['entries']:
            print(f"\nFirst few entries:")
            for entry in race['entries'][:3]:
                print(f"  {entry}")

if __name__ == "__main__":
    debug_single_race()