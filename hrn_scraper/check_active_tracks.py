#!/usr/bin/env python3
"""
Test hangi pistlerde bugün yarış var
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def check_active_tracks_today():
    """Bugün yarış olan pistleri kontrol et"""
    
    tracks = {
        'santa-anita': 'Santa Anita Park',
        'woodbine': 'Woodbine Racetrack', 
        'churchill-downs': 'Churchill Downs',
        'gulfstream-park': 'Gulfstream Park',
        'delaware-park': 'Delaware Park',
        'charles-town': 'Charles Town',
        'fairmount-park': 'Fairmount Park',
        'los-alamitos': 'Los Alamitos'
    }
    
    base_url = "https://www.horseracingnation.com"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    today = datetime.now().strftime("%Y-%m-%d")
    active_tracks = []
    
    print(f"🗓️  Bugün ({today}) yarış olan pistler:")
    print("="*50)
    
    for slug, name in tracks.items():
        try:
            url = f"{base_url}/tracks/{slug}/{today}"
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                race_cards = soup.find_all('div', class_='race-card') or soup.find_all('section', class_='race')
                
                if len(race_cards) > 0:
                    active_tracks.append(slug)
                    print(f"✅ {name} - {len(race_cards)} yarış")
                else:
                    print(f"❌ {name} - Yarış yok")
            else:
                print(f"❌ {name} - Erişilemez ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {name} - Hata: {str(e)[:50]}")
    
    print(f"\n📊 Toplam aktif pist: {len(active_tracks)}")
    if active_tracks:
        print("Aktif pistler:", ", ".join(active_tracks))
    
    return active_tracks

if __name__ == "__main__":
    check_active_tracks_today()