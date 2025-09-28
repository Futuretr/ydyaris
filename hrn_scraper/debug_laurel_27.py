#!/usr/bin/env python3
"""
Laurel Park 2025-09-27 verilerini kontrol et
"""

import requests
from bs4 import BeautifulSoup

def check_laurel_park_september_27():
    """27 Eylül Laurel Park verilerini kontrol et"""
    
    base_url = "https://www.horseracingnation.com"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # 27 Eylül için kontrol
    date_str = "2025-09-27"
    url = f"{base_url}/tracks/laurel-park/{date_str}"
    
    print(f"🏇 LAUREL PARK - 27 EYLÜL 2025")
    print("="*40)
    print(f"URL: {url}")
    
    try:
        response = session.get(url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Yarış kartlarını bul
            race_cards = soup.find_all('div', class_='race-card') or soup.find_all('section', class_='race')
            print(f"✅ {len(race_cards)} yarış bulundu!")
            
            # Her yarışın detayını göster
            for i, card in enumerate(race_cards, 1):
                print(f"\n📍 YARIŞ {i}:")
                
                # Yarış başlığını bul
                race_title = card.find('h3') or card.find('h2') or card.find('div', class_='race-title')
                if race_title:
                    print(f"   Başlık: {race_title.get_text().strip()}")
                
                # At sayısını kontrol et
                entries = card.find_all('div', class_='entry') or card.find_all('tr')
                print(f"   At sayısı: {len(entries)}")
                
                # İlk birkaç atı göster
                if entries:
                    print("   İlk atlar:")
                    for j, entry in enumerate(entries[:3], 1):
                        horse_name_elem = entry.find('a', class_='horse-name') or entry.find('td')
                        if horse_name_elem:
                            horse_name = horse_name_elem.get_text().strip()
                            print(f"     {j}. {horse_name}")
            
            return True
            
        else:
            print(f"❌ Sayfa erişilemez: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def check_entries_url():
    """Entries sayfasını kontrol et"""
    url = "https://entries.horseracingnation.com/entries-results/laurel-park/2025-09-27"
    
    print(f"\n🔍 ENTRIES SAYFASI KONTROLÜ")
    print("="*40)
    print(f"URL: {url}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Race 4'ü özel olarak bul
            race4_section = soup.find('div', id='race-4') or soup.find('section', id='race-4')
            if race4_section:
                print("✅ Race 4 bulundu!")
                
                # Race 4'teki atları listele
                horses = race4_section.find_all('tr') or race4_section.find_all('div', class_='entry')
                print(f"   Race 4 at sayısı: {len(horses)}")
                
                for i, horse in enumerate(horses[:5], 1):
                    horse_text = horse.get_text().strip()
                    if horse_text and len(horse_text) > 10:  # Boş satırları atla
                        print(f"     {i}. {horse_text[:50]}...")
            else:
                print("❌ Race 4 bulunamadı")
                
            return True
        else:
            print(f"❌ Entries sayfası erişilemez: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Entries hatası: {e}")
        return False

if __name__ == "__main__":
    check_laurel_park_september_27()
    check_entries_url()