#!/usr/bin/env python3
"""
Debug script - Check Major Tom's race history parsing
"""

import requests
from bs4 import BeautifulSoup
import logging

# Logging ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_major_tom():
    """Major Tom'un yarış geçmişini debug et"""
    try:
        url = "https://www.horseracingnation.com/horse/Major_Tom"
        logger.info(f"Checking URL: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Race history tablosunu bul
        table = soup.find('table', {'class': 'table'})
        if not table:
            logger.error("Race history table not found")
            return
        
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            logger.info(f"Found {len(rows)} race history rows")
            
            # İlk 5 yarışı kontrol et
            for i, row in enumerate(rows[:5]):
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # Tarih
                    date_cell = cells[0]
                    date_text = date_cell.get_text().strip()
                    
                    # Track
                    track_cell = cells[2] if len(cells) > 2 else None
                    track_text = track_cell.get_text().strip() if track_cell else "N/A"
                    
                    # Finish
                    finish_cell = cells[1] if len(cells) > 1 else None
                    finish_text = finish_cell.get_text().strip() if finish_cell else "N/A"
                    
                    logger.info(f"Row {i+1}: Date='{date_text}', Track='{track_text}', Finish='{finish_text}'")
            
            # İlk satırı detaylı parse et
            if rows:
                first_row = rows[0]
                cells = first_row.find_all('td')
                logger.info(f"\nFirst row detailed analysis:")
                for j, cell in enumerate(cells):
                    text = cell.get_text().strip()
                    logger.info(f"  Cell {j}: '{text}'")
                    
                    # Time element var mı?
                    time_elem = cell.find('time')
                    if time_elem:
                        datetime_attr = time_elem.get('datetime')
                        logger.info(f"    Time element: datetime='{datetime_attr}'")
        
    except Exception as e:
        logger.error(f"Error debugging Major Tom: {e}")

if __name__ == "__main__":
    debug_major_tom()