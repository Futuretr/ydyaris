#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NEW TRACKS TEST
Yeni eklenen pistleri test eder
"""

import sys
import os
import requests

# Add hrn_scraper to path
sys.path.append('hrn_scraper')

def test_new_tracks():
    """Test new tracks accessibility"""
    print("🏇 NEW TRACKS CONNECTIVITY TEST")
    print("=" * 50)
    
    new_tracks = [
        {
            'name': 'Horseshoe Indianapolis',
            'code': 'horseshoe-indianapolis',
            'url': 'https://entries.horseracingnation.com/entries-results/horseshoe-indianapolis/2025-09-29'
        },
        {
            'name': 'Finger Lakes',
            'code': 'finger-lakes', 
            'url': 'https://entries.horseracingnation.com/entries-results/finger-lakes/2025-09-29'
        }
    ]
    
    print(f"Testing {len(new_tracks)} new tracks...")
    print()
    
    for track in new_tracks:
        print(f"🎯 Testing {track['name']}:")
        print(f"   Code: {track['code']}")
        print(f"   URL: {track['url']}")
        
        try:
            response = requests.get(track['url'], timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code} - ACCESSIBLE")
                
                # Check if it has race content
                content = response.text.lower()
                if 'race' in content or 'entry' in content:
                    print(f"   🏇 Content: Race data detected")
                else:
                    print(f"   ⚠️  Content: No obvious race data")
                    
            else:
                print(f"   ❌ Status: {response.status_code} - NOT ACCESSIBLE")
                
        except requests.RequestException as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Test scraper integration
    print("🔧 SCRAPER INTEGRATION TEST:")
    try:
        from hrn_scraper import HorseRacingNationScraper, get_american_date_string
        
        scraper = HorseRacingNationScraper()
        american_date = get_american_date_string()
        
        print(f"   ✅ Scraper imported successfully")
        print(f"   📅 American date: {american_date}")
        print(f"   🎯 Ready to scrape new tracks!")
        
    except ImportError as e:
        print(f"   ❌ Scraper import failed: {e}")

if __name__ == "__main__":
    test_new_tracks()