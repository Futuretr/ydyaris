#!/usr/bin/env python3
"""
Debug script - Extract race number and horse program number from race link
"""

import requests
from bs4 import BeautifulSoup
import logging
import re

# Logging ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_race_details(horse_name):
    """Yarış detaylarını debug et"""
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
        
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            if rows:
                first_row = rows[0]
                cells = first_row.find_all('td')
                
                if len(cells) > 5:
                    race_cell = cells[5]  # Race bilgisi
                    race_text = race_cell.get_text().strip()
                    logger.info(f"Race cell text: '{race_text}'")
                    
                    # R1, R2 gibi race numarasını çıkar
                    race_num_match = re.search(r'-R(\d+)', race_text)
                    if race_num_match:
                        race_number = race_num_match.group(1)
                        logger.info(f"Race Number: {race_number}")
                    
                    # Linke tıklayıp yarış detaylarına bakalım
                    race_link = race_cell.find('a')
                    if race_link:
                        race_url = race_link.get('href')
                        if race_url:
                            if not race_url.startswith('http'):
                                race_url = f"https://www.horseracingnation.com{race_url}"
                            
                            logger.info(f"Race URL: {race_url}")
                            
                            # Yarış sayfasını çek
                            race_response = requests.get(race_url, timeout=10)
                            race_response.raise_for_status()
                            
                            race_soup = BeautifulSoup(race_response.content, 'html.parser')
                            
                            # At numaralarını bul
                            entries_table = race_soup.find('table', {'id': 'entries-table'})
                            if entries_table:
                                logger.info("Found entries table")
                                tbody = entries_table.find('tbody')
                                if tbody:
                                    rows = tbody.find_all('tr')
                                    logger.info(f"Found {len(rows)} entries")
                                    
                                    for row in rows:
                                        cells = row.find_all('td')
                                        if len(cells) >= 2:
                                            # İlk hücre program numarası olabilir
                                            prog_num = cells[0].get_text().strip()
                                            horse_link = cells[1].find('a') if len(cells) > 1 else None
                                            if horse_link:
                                                horse_name_in_table = horse_link.get_text().strip()
                                                if horse_name.lower() in horse_name_in_table.lower():
                                                    logger.info(f"Found {horse_name} with program number: {prog_num}")
                                                    return prog_num, race_number
                                            
                            # Alternatif: PP tablolarına bak
                            pp_section = race_soup.find('div', {'id': 'pp'})
                            if pp_section:
                                logger.info("Found PP section")
                                # PP section içinde at numaralarını ara
                                horse_divs = pp_section.find_all('div', class_=re.compile(r'pp-horse'))
                                for div in horse_divs:
                                    horse_link = div.find('a')
                                    if horse_link and horse_name.lower() in horse_link.get_text().lower():
                                        # Program numarasını ara
                                        prog_num_elem = div.find('span', class_='prog-num') or div.find('div', class_='prog-num')
                                        if prog_num_elem:
                                            prog_num = prog_num_elem.get_text().strip()
                                            logger.info(f"Found {horse_name} with program number: {prog_num}")
                                            return prog_num, race_number
        
    except Exception as e:
        logger.error(f"Error debugging race details for {horse_name}: {e}")
        return None, None

if __name__ == "__main__":
    # Test with a known horse
    prog_num, race_num = debug_race_details("Tiger of the Sea")
    print(f"Program Number: {prog_num}, Race Number: {race_num}")