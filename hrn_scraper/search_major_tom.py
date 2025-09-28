#!/usr/bin/env python3
"""
Search for all Major Tom horses
"""

import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import quote

# Logging ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_major_tom_variants():
    """Major Tom isimli farklı atları ara"""
    
    # Farklı URL formatları dene
    variants = [
        "Major_Tom",
        "Major Tom",
        "MajorTom", 
        "Major-Tom"
    ]
    
    for variant in variants:
        try:
            # URL encode
            encoded_name = quote(variant.replace(' ', '_'))
            url = f"https://www.horseracingnation.com/horse/{encoded_name}"
            logger.info(f"Trying URL: {url}")
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # At bilgilerini çıkar
                horse_info = {}
                
                # Trainer bilgisi
                trainer_elem = soup.find('td', string='Trainer:')
                if trainer_elem:
                    trainer_value = trainer_elem.find_next_sibling('td')
                    if trainer_value:
                        horse_info['trainer'] = trainer_value.get_text().strip()
                
                # Yaş bilgisi  
                age_elem = soup.find('td', string='Age:')
                if age_elem:
                    age_value = age_elem.find_next_sibling('td')
                    if age_value:
                        horse_info['age'] = age_value.get_text().strip()
                
                logger.info(f"Found horse at {url}:")
                logger.info(f"  Trainer: {horse_info.get('trainer', 'N/A')}")
                logger.info(f"  Age: {horse_info.get('age', 'N/A')}")
                
                # En son yarışa bak
                table = soup.find('table', {'class': 'table'})
                if table:
                    tbody = table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        if rows:
                            first_row = rows[0]
                            cells = first_row.find_all('td')
                            if len(cells) >= 3:
                                date = cells[0].get_text().strip()
                                track = cells[2].get_text().strip()
                                logger.info(f"  Latest race: {date} at {track}")
                
            else:
                logger.info(f"URL not found: {url} (Status: {response.status_code})")
                
        except Exception as e:
            logger.error(f"Error checking {variant}: {e}")

if __name__ == "__main__":
    search_major_tom_variants()