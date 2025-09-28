#!/usr/bin/env python3
"""
Test script - Check Major Tom 2 profile
"""

import requests
from bs4 import BeautifulSoup
import logging

# Logging ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_major_tom_2():
    """Major Tom 2'nin profilini kontrol et"""
    try:
        url = "https://www.horseracingnation.com/horse/Major_Tom_2"
        logger.info(f"Checking URL: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trainer bilgisi
        trainer_elem = soup.find('td', string='Trainer:')
        if trainer_elem:
            trainer_value = trainer_elem.find_next_sibling('td')
            if trainer_value:
                trainer = trainer_value.get_text().strip()
                logger.info(f"Trainer: {trainer}")
        
        # Race history tablosunu bul
        table = soup.find('table', {'class': 'table'})
        if table:
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                logger.info(f"Found {len(rows)} race history rows")
                
                # İlk 3 yarışı kontrol et
                for i, row in enumerate(rows[:3]):
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        date = cells[0].get_text().strip()
                        finish = cells[1].get_text().strip()
                        track = cells[2].get_text().strip()
                        logger.info(f"  Race {i+1}: {date} at {track}, finish: {finish}")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    test_major_tom_2()