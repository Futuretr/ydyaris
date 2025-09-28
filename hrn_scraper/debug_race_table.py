#!/usr/bin/env python3
"""
Debug script - Check race table structure for horse numbers and race numbers
"""

import requests
from bs4 import BeautifulSoup
import logging

# Logging ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_race_table(horse_name):
    """Yarış tablosunun yapısını debug et"""
    try:
        # At profilini çek
        url = f"https://www.horseracingnation.com/horse/{horse_name.replace(' ', '_')}"
        logger.info(f"Checking URL: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Race history tablosunu bul
        table = soup.find('table', {'class': 'table'})
        if not table:
            logger.error("Race history table not found")
            return
        
        # Header'ları kontrol et
        header = table.find('thead')
        if header:
            header_cells = header.find_all('th')
            logger.info("Table headers:")
            for i, cell in enumerate(header_cells):
                logger.info(f"  Column {i}: '{cell.get_text().strip()}'")
        
        # İlk veri satırını kontrol et
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            if rows:
                first_row = rows[0]
                cells = first_row.find_all('td')
                logger.info(f"\nFirst row has {len(cells)} cells:")
                for i, cell in enumerate(cells):
                    text = cell.get_text().strip()
                    logger.info(f"  Cell {i}: '{text}'")
                    
                    # Check for links and other elements
                    links = cell.find_all('a')
                    if links:
                        for link in links:
                            logger.info(f"    Link: '{link.get_text().strip()}' -> {link.get('href', 'No href')}")
        
    except Exception as e:
        logger.error(f"Error debugging race table for {horse_name}: {e}")

if __name__ == "__main__":
    # Test with a known horse
    debug_race_table("Tiger of the Sea")