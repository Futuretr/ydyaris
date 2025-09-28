#!/usr/bin/env python3
"""
Debug the _has_recent_races function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from horse_profile_scraper import HorseProfileScraper
from datetime import datetime, timedelta

def debug_has_recent_races():
    """Debug the _has_recent_races function"""
    scraper = HorseProfileScraper()
    
    print("Testing _has_recent_races function...")
    
    # Test Major Tom_2 directly
    horse_url = "https://www.horseracingnation.com/horse/Major_Tom_2"
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(horse_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Yarış geçmişini çek
        race_history = scraper._extract_race_history(soup)
        
        print(f"Found {len(race_history)} races")
        
        if race_history:
            print("\nFirst few races:")
            for i, race in enumerate(race_history[:3]):
                print(f"{i+1}. All keys: {list(race.keys())}")
                print(f"   Date: {race.get('date')}, Track: {race.get('track')}, Finish: {race.get('finish_position')}")
            
            # Test _has_recent_races
            has_recent = scraper._has_recent_races(race_history)
            print(f"\n_has_recent_races result: {has_recent}")
            
            # Debug date parsing
            current_date = datetime.now()
            two_years_ago = current_date - timedelta(days=730)
            print(f"Current date: {current_date.strftime('%Y-%m-%d')}")
            print(f"Two years ago: {two_years_ago.strftime('%Y-%m-%d')}")
            
            print("\nTesting date parsing for each race:")
            for i, race in enumerate(race_history[:5]):
                race_date_str = race.get('date', '')  # 'race_date' değil 'date' anahtarı
                print(f"Race {i+1}: Date string = '{race_date_str}'")
                
                if race_date_str and race_date_str != 'N/A':
                    for date_format in ['%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d']:
                        try:
                            race_date = datetime.strptime(race_date_str, date_format)
                            is_recent = race_date >= two_years_ago
                            print(f"  Format {date_format}: {race_date.strftime('%Y-%m-%d')} - Recent: {is_recent}")
                            break
                        except ValueError as e:
                            print(f"  Format {date_format}: Failed - {e}")
                            continue
                else:
                    print(f"  Empty or N/A date")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_has_recent_races()