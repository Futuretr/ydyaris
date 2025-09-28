#!/usr/bin/env python3
"""
Horse profile scraper - At profil sayfalarından yarış geçmişi verilerini çeker
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import logging
from datetime import datetime
import time
import re

# Logging ayarı
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('horse_profile_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HorseProfileScraper:
    def __init__(self):
        self.base_url = "https://www.horseracingnation.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _format_horse_name_for_url(self, horse_name):
        """At ismini URL formatına çevirir - özel karakterleri doğru handle eder"""
        
        # Özel durumlar için manuel mappings
        special_cases = {
            "Cash's Candy": "CashsCandy",  # Apostrofu kaldır ve birleştir
            "Full Serrano": "Full_Serrano_(ARG)"  # ARG ülke kodunu ekle
        }
        
        # Özel durum kontrolü
        if horse_name in special_cases:
            return special_cases[horse_name]
        
        # Genel formatlamalar
        # Apostrofleri kaldır: Cash's -> Cashs  
        formatted_name = horse_name.replace("'", "")
        
        # Noktaları kaldır: Sparta F. C. -> Sparta F C
        formatted_name = formatted_name.replace(".", "")
        
        # Boşlukları underscore ile değiştir: Cashs Candy -> Cashs_Candy
        formatted_name = formatted_name.replace(" ", "_")
        
        return formatted_name
        
    def scrape_horse_profile(self, horse_name):
        """Belirli bir atın profilini ve yarış geçmişini çeker - alternatif URL'leri dener"""
        # At ismini URL formatına çevir
        base_horse_slug = self._format_horse_name_for_url(horse_name)
        
        # Denenmesi gereken URL varyantları
        url_variants = [
            f"{self.base_url}/horse/{base_horse_slug}",
            f"{self.base_url}/horse/{base_horse_slug}_1",
            f"{self.base_url}/horse/{base_horse_slug}_2",
            f"{self.base_url}/horse/{base_horse_slug}_3",
            f"{self.base_url}/horse/{base_horse_slug}_4",
            f"{self.base_url}/horse/{base_horse_slug}_5"
        ]
        
        for variant_url in url_variants:
            try:
                logger.info(f"Trying URL for {horse_name}: {variant_url}")
                response = self.session.get(variant_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # At bilgilerini çek
                horse_info = self._extract_horse_info(soup, horse_name)
                
                # Yarış geçmişini çek
                race_history = self._extract_race_history(soup)
                
                # Eğer yarış geçmişi varsa ve son 2 yıl içinde yarış varsa, bu doğru attır
                if race_history and self._has_recent_races(race_history):
                    logger.info(f"Found valid horse profile at: {variant_url}")
                    
                    return {
                        'horse_info': horse_info,
                        'race_history': race_history
                    }
                else:
                    logger.info(f"No recent races at {variant_url}, trying next variant...")
                    continue
                    
            except Exception as e:
                logger.warning(f"Error fetching {variant_url}: {e}")
                continue
        
        # Hiçbir URL'de güncel yarış bulunamadı
        logger.error(f"No valid horse profile found for {horse_name} after trying all variants")
        return None
    
    def _extract_horse_info(self, soup, horse_name):
        """At bilgilerini çıkarır"""
        info = {
            'name': horse_name,
            'age': None,
            'sex': None,
            'status': None,
            'owner': None,
            'trainer': None,
            'breeder': None,
            'sire': None,
            'dam': None,
            'dam_sire': None
        }
        
        try:
            # At istatistiklerini bul
            stats_dl = soup.find('dl', class_='horse-stats')
            if stats_dl:
                dt_elements = stats_dl.find_all('dt')
                dd_elements = stats_dl.find_all('dd')
                
                for dt, dd in zip(dt_elements, dd_elements):
                    field = dt.get_text().strip().lower().rstrip(':')
                    value = dd.get_text().strip()
                    
                    if 'age' in field:
                        # "3 years old - Filly" formatından yaş ve cinsiyeti çıkar
                        age_match = re.search(r'(\d+)\s+years?\s+old.*?-\s*(\w+)', value)
                        if age_match:
                            info['age'] = age_match.group(1)
                            info['sex'] = age_match.group(2)
                    elif 'status' in field:
                        info['status'] = value
                    elif 'owner' in field:
                        info['owner'] = value
                    elif 'trainer' in field:
                        info['trainer'] = value
                    elif 'bred' in field:
                        # "Kentucky, US by Jeff Ganje" formatından breeder'ı çıkar
                        bred_match = re.search(r'by\s+(.+)$', value)
                        if bred_match:
                            info['breeder'] = bred_match.group(1).strip()
                    elif 'pedigree' in field:
                        # Pedigree linklerini çıkar
                        pedigree_links = dd.find_all('a', class_='horse-name')
                        if len(pedigree_links) >= 1:
                            info['sire'] = pedigree_links[0].get_text().strip()
                        if len(pedigree_links) >= 2:
                            info['dam'] = pedigree_links[1].get_text().strip()
                        if len(pedigree_links) >= 3:
                            info['dam_sire'] = pedigree_links[2].get_text().strip()
            
            logger.info(f"Extracted horse info for {horse_name}")
            return info
            
        except Exception as e:
            logger.error(f"Error extracting horse info: {e}")
            return info
    
    def _extract_race_history(self, soup):
        """Yarış geçmişini çıkarır - Sadece en son yarışı alır"""
        races = []
        
        try:
            # Race results tablosunu bul
            table = soup.find('table', class_='horse-table')
            if not table:
                logger.warning("Race history table not found")
                return races
            
            tbody = table.find('tbody')
            if not tbody:
                logger.warning("Race history tbody not found")
                return races
            
            rows = tbody.find_all('tr')
            logger.info(f"Found {len(rows)} race history rows")
            
            # En son yarışı al ama 2020'den eski olanları reddet
            if rows:
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 6:  # Minimum sütun sayısı
                        race_data = self._parse_race_row(cells)
                        if race_data:
                            # Tarih kontrolü - 2020'den eski yarışları reddet
                            race_date = race_data.get('date', '')
                            try:
                                # Yılı çıkar (2020'den küçükse reddet)
                                if race_date and ('T' in race_date or '-' in race_date):
                                    year_str = race_date[:4] if race_date[0:4].isdigit() else '0'
                                    year = int(year_str) if year_str.isdigit() else 0
                                    
                                    if year < 2020:
                                        logger.warning(f"Skipping old race from {race_date} (year: {year})")
                                        continue
                            except:
                                pass
                            
                            races.append(race_data)
                            logger.info(f"Extracted race from {race_date}")
                            break  # İlk geçerli yarışı bul ve dur
            
            logger.info(f"Extracted {len(races)} races from history (latest only)")
            return races
            
        except Exception as e:
            logger.error(f"Error extracting race history: {e}")
            return races
    
    def _parse_race_row(self, cells):
        """Tek bir yarış satırını parse eder"""
        try:
            race_data = {}
            
            # Tarih (1. sütun)
            date_cell = cells[0]
            time_elem = date_cell.find('time')
            if time_elem and time_elem.get('datetime'):
                race_data['date'] = time_elem.get('datetime')
                race_data['race_date'] = time_elem.get('datetime')  # Backward compatibility
            else:
                date_text = date_cell.get_text().strip()
                race_data['date'] = date_text
                race_data['race_date'] = date_text  # Backward compatibility
            
            # Finish ve speed figure (2. sütun)
            finish_cell = cells[1]
            finish_text = finish_cell.get_text().strip()
            
            # "3rd (61*)" formatından finish ve speed figure'ı çıkar
            finish_match = re.search(r'(\d+)(?:st|nd|rd|th)\s*\(([^)]+)\)', finish_text)
            if finish_match:
                race_data['finish_position'] = finish_match.group(1)
                race_data['speed_figure'] = finish_match.group(2).strip('*')
            else:
                race_data['finish_position'] = finish_text
                race_data['speed_figure'] = None
            
            # Track (3. sütun)
            track_cell = cells[2]
            track_link = track_cell.find('a')
            if track_link:
                race_data['track'] = track_link.get_text().strip()
            else:
                race_data['track'] = track_cell.get_text().strip()
            
            # Distance (4. sütun) - Desktop only
            if len(cells) > 3:
                race_data['distance'] = cells[3].get_text().strip() if cells[3].get_text().strip() else None
            
            # Surface (5. sütun) - Desktop only  
            if len(cells) > 4:
                surface_text = cells[4].get_text().strip()
                race_data['surface'] = surface_text if surface_text else None
            
            # Race info (6. sütun)
            if len(cells) > 5:
                race_info_cell = cells[5]
                race_data['race_type'] = race_info_cell.get_text().strip()
            
            # Time (son sütun)
            if len(cells) > 9:  # Desktop view
                time_cell = cells[9]
            elif len(cells) > 6:  # Mobile view fallback
                time_cell = cells[-1]
            else:
                time_cell = None
                
            if time_cell:
                time_elem = time_cell.find('time')
                if time_elem and time_elem.get('datetime'):
                    # PT1M8.61S formatını 1:08.61 formatına çevir
                    duration = time_elem.get('datetime')
                    time_match = re.search(r'PT(?:(\d+)M)?(\d+(?:\.\d+)?)S', duration)
                    if time_match:
                        minutes = time_match.group(1) or '0'
                        seconds = time_match.group(2)
                        race_data['time'] = f"{minutes}:{seconds.zfill(5)}"
                    else:
                        race_data['time'] = time_elem.get_text().strip()
                else:
                    race_data['time'] = time_cell.get_text().strip()
            
            return race_data
            
        except Exception as e:
            logger.error(f"Error parsing race row: {e}")
            return None
    
    def scrape_multiple_horses(self, horse_names, delay=1):
        """Birden fazla atın profilini çeker"""
        all_results = {}
        
        for i, horse_name in enumerate(horse_names, 1):
            logger.info(f"Processing horse {i}/{len(horse_names)}: {horse_name}")
            
            result = self.scrape_horse_profile(horse_name)
            if result:
                all_results[horse_name] = result
            
            # Rate limiting
            if i < len(horse_names):
                time.sleep(delay)
        
        return all_results
    
    def scrape_multiple_horses_with_data(self, horse_names, horses_data, delay=1):
        """Birden fazla atın profilini ekstra verilerle çeker"""
        all_results = {}
        
        for i, horse_name in enumerate(horse_names, 1):
            logger.info(f"Processing horse {i}/{len(horse_names)}: {horse_name}")
            
            result = self.scrape_horse_profile(horse_name)
            if result:
                # Yarış ve program numaralarını ekle
                race_number = horses_data[horse_name]['race_number']
                program_number = horses_data[horse_name]['program_number']
                
                # Her yarışa race_number ve program_number ekle
                for race in result['race_history']:
                    race['race_number'] = race_number
                    race['program_number'] = program_number
                
                all_results[horse_name] = result
            
            # Rate limiting
            if i < len(horse_names):
                time.sleep(delay)
        
        return all_results
    
    def save_to_csv(self, results, filename):
        """Sonuçları CSV dosyasına kaydet"""
        if not results:
            logger.warning("No results to save")
            return
        
        # Tüm yarışları flatten et
        all_races = []
        
        for horse_name, data in results.items():
            horse_info = data['horse_info']
            
            for race in data['race_history']:
                race_row = {
                    'horse_name': horse_name,
                    'race_number': race.get('race_number'),
                    'program_number': race.get('program_number'),
                    'race_date': race.get('race_date', race.get('date')),  # Backward compatibility
                    'track': race.get('track'),
                    'distance': race.get('distance'),
                    'surface': race.get('surface'),
                    'time': race.get('time'),
                    'finish_position': race.get('finish_position')
                }
                all_races.append(race_row)
        
        # CSV'ye kaydet
        if all_races:
            fieldnames = all_races[0].keys()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_races)
            
            logger.info(f"Saved {len(all_races)} race records to {filename}")
        
    def save_to_json(self, results, filename):
        """Sonuçları JSON dosyasına kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved horse profiles to {filename}")
    
    def _has_recent_races(self, race_history):
        """Son 2 yıl içinde yarış olup olmadığını kontrol eder"""
        from datetime import datetime, timedelta
        
        if not race_history:
            return False
        
        current_date = datetime.now()
        two_years_ago = current_date - timedelta(days=730)  # 2 yıl
        
        for race in race_history:
            try:
                # Tarih formatını parse et
                race_date_str = race.get('date', '')  # 'race_date' değil 'date' anahtarı
                if race_date_str and race_date_str != 'N/A':
                    # Farklı tarih formatlarını dene
                    for date_format in ['%Y-%m-%dT%H:%M:%SZ', '%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d']:
                        try:
                            race_date = datetime.strptime(race_date_str, date_format)
                            if race_date >= two_years_ago:
                                return True
                            break
                        except ValueError:
                            continue
            except Exception:
                continue
        
        return False

    def save_profiles_to_csv(self, output_file, horses_data):
        """Sonuçları CSV formatında kaydet - Multi-track scraper için"""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'race_number', 'program_number', 'horse_name', 'age', 'sex', 'status',
                    'owner', 'trainer', 'breeder', 'sire', 'dam', 'dam_sire',
                    'latest_race_date', 'latest_track', 'latest_distance', 'latest_surface',
                    'latest_time', 'latest_finish_position', 'latest_speed_figure', 'latest_race_type'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for horse_name, race_data in horses_data.items():
                    # At profilini çek
                    profile_result = self.scrape_horse_profile(horse_name)
                    
                    row = {
                        'race_number': race_data.get('race_number', ''),
                        'program_number': race_data.get('program_number', ''),
                        'horse_name': horse_name
                    }
                    
                    if profile_result:
                        # At bilgileri
                        horse_info = profile_result.get('horse_info', {})
                        row.update({
                            'age': horse_info.get('age'),
                            'sex': horse_info.get('sex'),
                            'status': horse_info.get('status'),
                            'owner': horse_info.get('owner'),
                            'trainer': horse_info.get('trainer'),
                            'breeder': horse_info.get('breeder'),
                            'sire': horse_info.get('sire'),
                            'dam': horse_info.get('dam'),
                            'dam_sire': horse_info.get('dam_sire')
                        })
                        
                        # En son yarış bilgileri
                        race_history = profile_result.get('race_history', [])
                        if race_history:
                            latest_race = race_history[0]
                            row.update({
                                'latest_race_date': latest_race.get('date'),
                                'latest_track': latest_race.get('track'),
                                'latest_distance': latest_race.get('distance'),
                                'latest_surface': latest_race.get('surface'),
                                'latest_time': latest_race.get('time'),
                                'latest_finish_position': latest_race.get('finish_position'),
                                'latest_speed_figure': latest_race.get('speed_figure'),
                                'latest_race_type': latest_race.get('race_type')
                            })
                    
                    writer.writerow(row)
                    
            logger.info(f"Saved {len(horses_data)} horse records to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")


if __name__ == "__main__":
    scraper = HorseProfileScraper()
    
    # Test için Tiger of the Sea
    test_horses = ["Tiger of the Sea"]
    
    print("Testing horse profile scraper...")
    results = scraper.scrape_multiple_horses(test_horses)
    
    if results:
        # Sonuçları kaydet
        scraper.save_to_csv(results, "horse_profiles.csv")
        scraper.save_to_json(results, "horse_profiles.json")
        
        print(f"\nResults for {len(results)} horses:")
        for horse_name, data in results.items():
            print(f"\n{horse_name}:")
            print(f"  Races: {len(data['race_history'])}")
            if data['race_history']:
                print("  Recent races:")
                for race in data['race_history'][:3]:
                    print(f"    {race.get('date')} - {race.get('track')} - {race.get('finish_position')} ({race.get('speed_figure')})")
    else:
        print("No results obtained")