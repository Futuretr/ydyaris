#!/usr/bin/env python3
"""
Debug script to check HTML structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from bs4 import BeautifulSoup
import re

def debug_santa_anita():
    """Santa Anita HTML yapısını analiz eder"""
    
    url = "https://entries.horseracingnation.com/entries-results/santa-anita/2025-09-27"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        
        # HTML'i parse et
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Title kontrolü
        title = soup.find('title')
        if title:
            print(f"Title: {title.get_text()}")
        
        # H1 ve H2 başlıklarını bul
        print("\n=== H1 Headers ===")
        h1_tags = soup.find_all('h1')
        for i, h1 in enumerate(h1_tags[:5]):
            print(f"H1 {i+1}: {h1.get_text().strip()}")
        
        print("\n=== H2 Headers ===")
        h2_tags = soup.find_all('h2')
        for i, h2 in enumerate(h2_tags[:10]):
            print(f"H2 {i+1}: {h2.get_text().strip()}")
        
        # Race pattern arama
        print("\n=== Race Pattern Search ===")
        race_patterns = [
            r'Race\s*#?\s*\d+',
            r'R\d+',
            r'Race\s+\d+',
            r'\d+:\d+\s*[AP]M'
        ]
        
        for pattern in race_patterns:
            matches = soup.find_all(string=re.compile(pattern, re.I))
            print(f"Pattern '{pattern}': {len(matches)} matches")
            for match in matches[:3]:
                print(f"  - {match.strip()}")
        
        # Table kontrolü
        print("\n=== Tables ===")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables[:3]):
            rows = table.find_all('tr')
            print(f"Table {i+1}: {len(rows)} rows")
            if rows:
                first_row = rows[0]
                cells = first_row.find_all(['td', 'th'])
                print(f"  First row cells: {[cell.get_text().strip()[:20] for cell in cells[:5]]}")
        
        # Div yapısını kontrol et
        print("\n=== Div Structure ===")
        race_divs = soup.find_all('div', class_=re.compile(r'race|entry', re.I))
        print(f"Race-related divs: {len(race_divs)}")
        
        # İlk 1000 karakteri yazdır
        print("\n=== First 1000 characters of HTML ===")
        print(response.text[:1000])
        
        # Son 1000 karakteri yazdır 
        print("\n=== Last 1000 characters of HTML ===")
        print(response.text[-1000:])
        
        return soup
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    debug_santa_anita()