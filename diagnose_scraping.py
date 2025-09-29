#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRAPING DIAGNOSTIC TOOL
Veri çekme problemlerini tespit eder
"""

import sys
import os
import requests
import json
import pytz
from datetime import datetime

# Add hrn_scraper to path
sys.path.append('hrn_scraper')

def check_timezone():
    """Amerika saat dilimi kontrolü"""
    print("🕐 TIMEZONE CHECK")
    print("-" * 30)
    
    try:
        from hrn_scraper import get_american_time, get_american_date_string
        
        turkey_time = datetime.now()
        american_time = get_american_time()
        american_date = get_american_date_string()
        
        print(f"Turkey Time:    {turkey_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"American Time:  {american_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"American Date:  {american_date}")
        print("✅ Timezone functions working")
        return american_date
    except Exception as e:
        print(f"❌ Timezone error: {e}")
        return None

def check_network():
    """Network bağlantısı kontrolü"""
    print("\n🌐 NETWORK CHECK")
    print("-" * 30)
    
    test_urls = [
        "https://entries.horseracingnation.com/",
        "https://www.horseracingnation.com/",
        "https://entries.horseracingnation.com/entries-results/santa-anita/2025-09-28",
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - Status: {response.status_code}")
            else:
                print(f"⚠️  {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")

def check_scraper_import():
    """Scraper import kontrolü"""
    print("\n🔧 SCRAPER IMPORT CHECK")
    print("-" * 30)
    
    try:
        from hrn_scraper import HorseRacingNationScraper
        scraper = HorseRacingNationScraper()
        print("✅ HorseRacingNationScraper imported successfully")
        return scraper
    except Exception as e:
        print(f"❌ Scraper import failed: {e}")
        return None

def check_horse_profile_scraper():
    """Horse Profile Scraper kontrolü"""
    print("\n🏇 HORSE PROFILE SCRAPER CHECK")
    print("-" * 30)
    
    try:
        from horse_profile_scraper import HorseProfileScraper
        scraper = HorseProfileScraper()
        print("✅ HorseProfileScraper imported successfully")
        return scraper
    except Exception as e:
        print(f"❌ Horse Profile Scraper import failed: {e}")
        return None

def test_single_track_scraping(american_date):
    """Tek pist scraping testi"""
    print("\n🎯 SINGLE TRACK SCRAPING TEST")
    print("-" * 30)
    
    try:
        from hrn_scraper import HorseRacingNationScraper
        scraper = HorseRacingNationScraper()
        
        # Test track: Santa Anita
        test_track = "santa-anita"
        print(f"Testing track: {test_track}")
        print(f"Date: {american_date}")
        
        # Get daily tracks first
        tracks = scraper.get_daily_tracks(american_date)
        print(f"Available tracks: {len(tracks) if tracks else 0}")
        
        if tracks:
            # Find our test track
            target_track = None
            for track in tracks:
                if test_track in track.get('url', '').lower():
                    target_track = track
                    break
            
            if target_track:
                print(f"✅ Found target track: {target_track['name']}")
                print(f"   URL: {target_track['url']}")
                
                # Try to scrape it
                track_data = scraper.scrape_track_data(target_track['url'], target_track['name'])
                if track_data:
                    print(f"✅ Scraped successfully")
                    print(f"   Total races: {track_data.get('total_races', 0)}")
                    return True
                else:
                    print(f"❌ Scraping failed")
            else:
                print(f"⚠️  Target track not found in daily tracks")
        else:
            print(f"❌ No tracks available for date {american_date}")
        
    except Exception as e:
        print(f"❌ Scraping test failed: {e}")
    
    return False

def check_file_access():
    """Dosya erişimi kontrolü"""
    print("\n📁 FILE ACCESS CHECK")
    print("-" * 30)
    
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check if we can write files
    try:
        test_file = "test_write_access.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ File write access OK")
    except Exception as e:
        print(f"❌ File write error: {e}")

def diagnose_scraping_issues():
    """Ana diagnostic fonksiyon"""
    print("🔍 SCRAPING DIAGNOSTIC TOOL")
    print("=" * 50)
    
    # 1. Timezone check
    american_date = check_timezone()
    
    # 2. Network check
    check_network()
    
    # 3. File access check
    check_file_access()
    
    # 4. Scraper imports
    hrn_scraper = check_scraper_import()
    horse_scraper = check_horse_profile_scraper()
    
    # 5. Single track test
    if american_date and hrn_scraper:
        test_single_track_scraping(american_date)
    
    print("\n🎯 DIAGNOSIS COMPLETE")
    print("=" * 50)
    
    if american_date and hrn_scraper and horse_scraper:
        print("✅ All components seem to be working")
        print("   If you're still having issues, please describe the specific problem")
    else:
        print("❌ Some components have issues - check the errors above")

if __name__ == "__main__":
    diagnose_scraping_issues()
