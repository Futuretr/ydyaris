#!/usr/bin/env python3
"""
Laurel Park slug kontrolü - Doğru pist adını bul
"""

import requests
from bs4 import BeautifulSoup

def check_laurel_park_slug():
    """Laurel Park için doğru slug'ı kontrol et"""
    
    # Farklı slug seçeneklerini dene
    possible_slugs = [
        'laurel-park',
        'laurel',
        'laurel-race-course',
        'laurel-park-maryland'
    ]
    
    base_url = "https://www.horseracingnation.com"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Bugünün tarihi
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Testing for date: {today}")
    
    for slug in possible_slugs:
        try:
            url = f"{base_url}/tracks/{slug}/{today}"
            print(f"\nTesting: {url}")
            
            response = session.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Track ismini bul
                track_title = soup.find('h1') or soup.find('title')
                if track_title:
                    print(f"✅ Found track: {track_title.get_text().strip()}")
                
                # Yarış sayısını kontrol et
                race_cards = soup.find_all('div', class_='race-card') or soup.find_all('section', class_='race')
                print(f"   Races found: {len(race_cards)}")
                
                # Eğer yarış varsa bu doğru slug'dır
                if len(race_cards) > 0:
                    print(f"✅ CORRECT SLUG: {slug}")
                    return slug
                else:
                    print("   No races found for today")
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n❌ No working slug found for Laurel Park!")
    return None

if __name__ == "__main__":
    check_laurel_park_slug()