#!/usr/bin/env python3
"""
Laurel Park yarış takvimi kontrolü - Hangi günlerde yarış var?
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def check_laurel_park_schedule():
    """Laurel Park yarış takvimini kontrol et"""
    
    base_url = "https://www.horseracingnation.com"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Gelecek 7 günü kontrol et
    today = datetime.now()
    
    print("🏇 LAUREL PARK YARIŞ TAKVİMİ KONTROLÜ")
    print("="*50)
    
    for i in range(7):
        check_date = today + timedelta(days=i)
        date_str = check_date.strftime("%Y-%m-%d")
        day_name = check_date.strftime("%A")
        
        print(f"\n📅 {day_name}, {date_str}")
        
        # Laurel slug'ı ile dene
        url = f"{base_url}/tracks/laurel-park/{date_str}"
        
        try:
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Yarış kartlarını bul
                race_cards = soup.find_all('div', class_='race-card') or soup.find_all('section', class_='race')
                
                if len(race_cards) > 0:
                    print(f"   ✅ {len(race_cards)} YARIŞ VAR!")
                    
                    # İlk birkaç yarışın detayını göster
                    for j, card in enumerate(race_cards[:3], 1):
                        race_title = card.find('h3') or card.find('h2')
                        if race_title:
                            print(f"      Yarış {j}: {race_title.get_text().strip()}")
                else:
                    print("   ❌ Yarış yok")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Hata: {e}")
    
    # Ayrıca ana track sayfasını kontrol et
    print(f"\n🔍 LAUREL PARK ANA SAYFA KONTROLÜ")
    try:
        main_url = f"{base_url}/tracks/laurel-park"
        response = session.get(main_url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            print("✅ Ana sayfa erişilebilir")
            
            # Track bilgilerini bul
            track_info = soup.find('div', class_='track-info') or soup.find('div', class_='track-header')
            if track_info:
                print(f"   Track info: {track_info.get_text().strip()[:100]}...")
        else:
            print(f"❌ Ana sayfa erişilemez: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ana sayfa hatası: {e}")

if __name__ == "__main__":
    check_laurel_park_schedule()