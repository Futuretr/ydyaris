#!/usr/bin/env python3
"""
Test script to verify the updated multi-track scraper can detect races
from both entries-results and main track URLs for various tracks.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_track_scraper import check_if_races_exist
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_track_detection():
    """Test race detection for various tracks and dates"""
    
    # Test with today and yesterday
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    test_dates = [today, yesterday, '2025-01-27']
    
    # Test a selection of tracks
    test_tracks = [
        'laurel-park',        # Known to have entries-results format
        'gulfstream-park',    # Popular track
        'del-mar',           # Popular track
        'churchill-downs',    # Major track
        'santa-anita'        # Major track
    ]
    
    print("Testing race detection across multiple tracks and dates:")
    print("=" * 60)
    
    results = {}
    
    for track_slug in test_tracks:
        results[track_slug] = {}
        print(f"\n🏇 Testing {track_slug.upper()}:")
        
        for date_str in test_dates:
            print(f"  📅 {date_str}: ", end="")
            
            try:
                has_races = check_if_races_exist(track_slug, date_str)
                results[track_slug][date_str] = has_races
                
                if has_races:
                    print("✅ Races found")
                else:
                    print("❌ No races")
                    
            except Exception as e:
                print(f"⚠️ Error: {e}")
                results[track_slug][date_str] = f"Error: {e}"
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    for track_slug, dates in results.items():
        print(f"\n{track_slug.upper()}:")
        for date_str, result in dates.items():
            status = "✅" if result is True else "❌" if result is False else "⚠️"
            print(f"  {date_str}: {status} {result}")
    
    # Test specifically for Laurel Park on the known date
    print(f"\n🔍 SPECIFIC TEST: Laurel Park on 2025-01-27:")
    laurel_result = check_if_races_exist('laurel-park', '2025-01-27')
    print(f"   Result: {'✅ Found' if laurel_result else '❌ Not found'}")

if __name__ == "__main__":
    test_track_detection()