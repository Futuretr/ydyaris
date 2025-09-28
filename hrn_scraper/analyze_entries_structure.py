#!/usr/bin/env python3
"""
Entries sayfası HTML yapısını analiz et
"""

import requests
from bs4 import BeautifulSoup

def analyze_entries_page():
    """Entries sayfasının yapısını analiz et"""
    
    url = "https://entries.horseracingnation.com/entries-results/laurel-park/2025-09-27"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print(f"🔍 ENTRIES SAYFASI ANALİZİ")
    print(f"URL: {url}")
    print("="*50)
    
    try:
        response = session.get(url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Farklı race selector'ları dene
            race_selectors = [
                'div[id*="race"]',
                'section[id*="race"]', 
                '.race-card',
                '.race',
                'div.race-container',
                'div[data-race]',
                'h2, h3, h4'  # Yarış başlıkları
            ]
            
            print("\n📋 BULUNAN YAPILAR:")
            
            for selector in race_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"\n✅ {selector}: {len(elements)} element")
                    
                    for i, elem in enumerate(elements[:3], 1):
                        text = elem.get_text().strip()[:100]
                        print(f"   {i}. {text}...")
                        
                        # ID ve class bilgilerini göster
                        if elem.get('id'):
                            print(f"      ID: {elem.get('id')}")
                        if elem.get('class'):
                            print(f"      Class: {elem.get('class')}")
            
            # Tüm text'i kontrol et
            page_text = soup.get_text()
            if "Race #1" in page_text or "Race 1" in page_text:
                print("\n✅ Sayfada 'Race' kelimesi bulundu")
            
            if "Laurel Park" in page_text:
                print("✅ Sayfada 'Laurel Park' bulundu")
            
            # Title kontrol
            title = soup.find('title')
            if title:
                print(f"\n📄 Sayfa başlığı: {title.get_text().strip()}")
            
            # Script'leri kontrol et - dinamik içerik olabilir
            scripts = soup.find_all('script')
            print(f"\n📝 {len(scripts)} script elementi bulundu")
            
            for script in scripts[:3]:
                if script.string and len(script.string) > 50:
                    script_text = script.string[:200]
                    if "race" in script_text.lower():
                        print(f"   Script (race içeren): {script_text[:100]}...")
            
        else:
            print(f"❌ Sayfa yüklenemedi: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    analyze_entries_page()