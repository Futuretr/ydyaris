#!/usr/bin/env python3
"""
Belirli bir pist için Horse Racing Nation scraper
Kullanım: python single_track_scraper.py santa-anita 2025-09-27
"""

import sys
import argparse
from hrn_scraper import HorseRacingNationScraper
from datetime import datetime
import json


def scrape_single_track(url_or_slug, date_str=None):
    """Belirli bir pist için scraping yapar (URL ya da slug kabul eder)"""
    
    scraper = HorseRacingNationScraper()
    
    # URL mı slug mu kontrol et
    if url_or_slug.startswith('http'):
        # Eğer /races/ formatındaysa, doğru formata çevir
        if '/races/' in url_or_slug:
            # https://entries.horseracingnation.com/races/2024-12-27/santa-anita
            # -> https://entries.horseracingnation.com/entries-results/santa-anita/2024-12-27
            parts = url_or_slug.split('/')
            if len(parts) >= 6:
                date_part = parts[-2]  # 2024-12-27
                track_part = parts[-1]  # santa-anita
                track_url = f"{scraper.base_url}entries-results/{track_part}/{date_part}"
                track_slug = track_part
                if not date_str:
                    date_str = date_part
            else:
                track_url = url_or_slug
                track_slug = parts[-1] if parts[-1] else parts[-2]
        else:
            track_url = url_or_slug
            # URL'den track slug'ını çıkar
            parts = url_or_slug.split('/')
            track_slug = parts[-2] if parts[-1] == '' else parts[-1]  # santa-anita
            if not date_str:
                # URL'den tarihi çıkarmaya çalış
                for part in parts:
                    if '-' in part and len(part) == 10:  # YYYY-MM-DD formatı
                        date_str = part
                        break
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
    else:
        track_slug = url_or_slug
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        track_url = f"{scraper.base_url}entries-results/{track_slug}/{date_str}"
    
    print(f"Scraping {track_slug} for {date_str}")
    print(f"URL: {track_url}")
    
    # Track data'yı scrape et
    track_data = scraper.scrape_track_data(track_url, track_slug)
    
    if track_data:
        # Sonuçları göster
        print(f"\n=== {track_slug.upper()} - {date_str} ===")
        print(f"Total races: {track_data['total_races']}")
        
        for race in track_data['races']:
            print(f"\nRace {race.get('race_number', 'N/A')} - {race.get('post_time', 'N/A')}")
            race_info = race.get('race_info', {})
            print(f"  Distance: {race_info.get('distance', 'N/A')}")
            print(f"  Surface: {race_info.get('surface', 'N/A')}")
            print(f"  Purse: ${race_info.get('purse', 'N/A')}")
            print(f"  Entries: {len(race.get('entries', []))}")
            
            # İlk 3 atı göster
            entries = race.get('entries', [])[:3]
            for entry in entries:
                horse_info = entry.get('horse_info', {})
                print(f"    {entry.get('post_position', 'N/A')}. {horse_info.get('horse_name', 'N/A')} "
                      f"({horse_info.get('speed_figure', 'N/A')}) - {entry.get('morning_line', 'N/A')}")
            
            if len(race.get('entries', [])) > 3:
                print(f"    ... and {len(race.get('entries', [])) - 3} more")
        
        # Dosyalara kaydet
        base_filename = f"{track_slug}_{date_str.replace('-', '_')}"
        scraper.save_data_to_json({track_slug: track_data}, f"{base_filename}.json")
        scraper.save_data_to_csv({track_slug: track_data}, base_filename)
        
        print(f"\n✅ Data saved to:")
        print(f"   - {base_filename}.json")
        print(f"   - {base_filename}_entries.csv")
        print(f"   - {base_filename}_results.csv")
        
        return track_data
    else:
        print(f"Failed to scrape data for {track_slug}")
        return None


def get_available_tracks(date_str):
    """Belirli bir tarih için mevcut pistleri listeler"""
    scraper = HorseRacingNationScraper()
    tracks = scraper.get_daily_tracks(date_str)
    
    print(f"\nAvailable tracks for {date_str}:")
    print("-" * 50)
    
    for track in tracks:
        print(f"{track['slug']} - {track['name']} ({track['time']})")
        if 'purse' in track:
            print(f"  Purse: {track['purse']}")
    
    return tracks


def main():
    parser = argparse.ArgumentParser(description='Horse Racing Nation Single Track Scraper')
    parser.add_argument('url_or_slug', nargs='?', 
                       help='Full URL or track slug (e.g., santa-anita or full URL)')
    parser.add_argument('date', nargs='?', help='Date in YYYY-MM-DD format (optional if URL provided)')
    parser.add_argument('--list-tracks', '-l', action='store_true', 
                       help='List available tracks for the date')
    
    args = parser.parse_args()
    
    # Tarih kontrolü
    date_str = None
    if args.date:
        try:
            datetime.strptime(args.date, '%Y-%m-%d')
            date_str = args.date
        except ValueError:
            print("Error: Date must be in YYYY-MM-DD format")
            sys.exit(1)
    
    # Sadece track listesi isteniyorsa
    if args.list_tracks:
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        get_available_tracks(date_str)
        return
    
    # URL veya slug kontrolü
    if not args.url_or_slug:
        print("Error: URL or track slug required")
        print("Use --list-tracks to see available tracks")
        print("\nExample usage:")
        print("  python single_track_scraper.py santa-anita 2025-09-27")
        print("  python single_track_scraper.py https://entries.horseracingnation.com/races/2024-12-27/santa-anita")
        print("  python single_track_scraper.py --list-tracks 2025-09-27")
        sys.exit(1)
    
    # Scraping yap
    scrape_single_track(args.url_or_slug, date_str)


if __name__ == "__main__":
    main()