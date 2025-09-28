#!/usr/bin/env python3
"""
Test script for Horse Racing Nation Scraper
Bu script scraper'ın çalışıp çalışmadığını test eder
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hrn_scraper import HorseRacingNationScraper
from datetime import datetime
import json


def test_daily_tracks():
    """Günlük pistleri test eder"""
    print("=== Testing Daily Tracks ===")
    
    scraper = HorseRacingNationScraper()
    
    # Bugünün pistleri
    today = datetime.now().strftime('%Y-%m-%d')
    tracks = scraper.get_daily_tracks(today)
    
    print(f"Found {len(tracks)} tracks for {today}")
    
    for track in tracks[:5]:  # İlk 5'ini göster
        print(f"  {track['name']} - {track['slug']} ({track.get('time', 'N/A')})")
        print(f"    URL: {track['url']}")
    
    return tracks


def test_santa_anita():
    """Santa Anita örneğini test eder"""
    print("\n=== Testing Santa Anita ===")
    
    scraper = HorseRacingNationScraper()
    
    # Santa Anita URL'si
    url = "https://entries.horseracingnation.com/entries-results/santa-anita/2025-09-27"
    
    print(f"Scraping: {url}")
    
    data = scraper.scrape_track_data(url, "Santa Anita")
    
    if data:
        print(f"Success! Found {data['total_races']} races")
        
        # İlk yarışı detaylı göster
        if data['races']:
            race = data['races'][0]
            print(f"\nFirst Race Details:")
            print(f"  Race Number: {race.get('race_number')}")
            print(f"  Post Time: {race.get('post_time')}")
            print(f"  Distance: {race.get('race_info', {}).get('distance')}")
            print(f"  Surface: {race.get('race_info', {}).get('surface')}")
            print(f"  Entries: {len(race.get('entries', []))}")
            
            # İlk 3 atı göster
            entries = race.get('entries', [])[:3]
            print(f"  Top 3 Entries:")
            for entry in entries:
                horse_info = entry.get('horse_info', {})
                print(f"    {entry.get('post_position')}. {horse_info.get('horse_name')} "
                      f"({horse_info.get('speed_figure')}) - {entry.get('morning_line')}")
        
        return data
    else:
        print("Failed to scrape Santa Anita")
        return None


def test_simple_request():
    """Basit HTTP isteği test eder"""
    print("\n=== Testing Simple Request ===")
    
    scraper = HorseRacingNationScraper()
    
    try:
        response = scraper.session.get("https://entries.horseracingnation.com/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} characters")
        
        if "Horse Racing" in response.text:
            print("✓ Site is accessible and contains expected content")
            return True
        else:
            print("✗ Site accessible but content unexpected")
            return False
            
    except Exception as e:
        print(f"✗ Error accessing site: {e}")
        return False


def main():
    print("Horse Racing Nation Scraper Test Suite")
    print("=" * 50)
    
    # Test 1: Basit erişim
    if not test_simple_request():
        print("Basic connectivity test failed!")
        return
    
    # Test 2: Günlük pistler
    tracks = test_daily_tracks()
    
    # Test 3: Santa Anita örneği
    santa_anita_data = test_santa_anita()
    
    # Test sonucu
    print("\n" + "=" * 50)
    if tracks and santa_anita_data:
        print("✓ All tests passed!")
        
        # Test verilerini kaydet
        test_data = {
            'daily_tracks': tracks,
            'santa_anita_sample': santa_anita_data
        }
        
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        print("Test results saved to test_results.json")
        
    else:
        print("✗ Some tests failed!")


if __name__ == "__main__":
    main()