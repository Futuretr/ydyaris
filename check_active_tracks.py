#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ACTIVE TRACKS CHECKER
Bugün aktif olan pistleri listeler
"""

import sys
import os

# Add hrn_scraper to path
sys.path.append('hrn_scraper')

def check_active_tracks():
    """Bugün aktif olan pistleri kontrol et"""
    print("🏇 ACTIVE TRACKS TODAY")
    print("=" * 50)
    
    try:
        from hrn_scraper import HorseRacingNationScraper, get_american_date_string
        
        scraper = HorseRacingNationScraper()
        american_date = get_american_date_string()
        
        print(f"Date (American): {american_date}")
        print(f"Checking available tracks...")
        print()
        
        tracks = scraper.get_daily_tracks(american_date)
        
        if tracks:
            print(f"Found {len(tracks)} active tracks:")
            print("-" * 40)
            
            for i, track in enumerate(tracks, 1):
                track_name = track.get('name', 'Unknown')
                track_url = track.get('url', '')
                
                # Extract track code from URL
                track_code = 'unknown'
                if '/entries-results/' in track_url:
                    parts = track_url.split('/entries-results/')
                    if len(parts) > 1:
                        path_parts = parts[1].split('/')
                        if path_parts:
                            track_code = path_parts[0]
                
                print(f"{i:2d}. {track_name}")
                print(f"    Code: {track_code}")
                print(f"    URL:  {track_url}")
                print()
            
            # Check if common tracks are available
            common_tracks = ['santa-anita', 'gulfstream-park', 'laurel-park', 'belmont-park']
            available_codes = []
            
            for track in tracks:
                url = track.get('url', '')
                for code in common_tracks:
                    if code in url:
                        available_codes.append(code)
            
            print("🎯 POPULAR TRACKS STATUS:")
            print("-" * 30)
            for code in common_tracks:
                status = "✅ ACTIVE" if code in available_codes else "❌ INACTIVE"
                print(f"{code:20} {status}")
                
        else:
            print("❌ No active tracks found")
            
    except Exception as e:
        print(f"❌ Error checking tracks: {e}")

if __name__ == "__main__":
    check_active_tracks()