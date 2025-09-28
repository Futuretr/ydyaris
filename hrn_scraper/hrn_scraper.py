#!/usr/bin/env python3
"""
Horse Racing Nation Scraper
Bu script https://entries.horseracingnation.com/ sitesinden at yarışı verilerini çeker
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hrn_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HorseRacingNationScraper:
    def __init__(self):
        self.base_url = "https://entries.horseracingnation.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_daily_tracks(self, date_str=None):
        """
        Belirli bir tarih için tüm pistleri getirir
        date_str format: 'YYYY-MM-DD' veya None (bugün için)
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
        url = f"{self.base_url}entries-results/{date_str}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            tracks = []
            
            # Tracks tablosunu bul
            tracks_table = soup.find('table')
            if not tracks_table:
                logger.warning(f"No tracks table found for date {date_str}")
                return tracks
                
            # Tablo satırlarını işle
            rows = tracks_table.find_all('tr')
            for row in rows[1:]:  # İlk satır başlık satırı
                cells = row.find_all('td')
                if len(cells) >= 3:
                    time_cell = cells[0].get_text(strip=True)
                    track_link = cells[1].find('a')
                    
                    if track_link:
                        track_name = track_link.get_text(strip=True)
                        track_url = track_link.get('href')
                        
                        if track_url:
                            full_url = urljoin(self.base_url, track_url)
                            
                            track_info = {
                                'date': date_str,
                                'time': time_cell,
                                'name': track_name,
                                'url': full_url,
                                'slug': self._extract_track_slug(track_url)
                            }
                            
                            # Ek bilgiler varsa ekle
                            if len(cells) >= 4:
                                track_info['purse'] = cells[2].get_text(strip=True)
                            if len(cells) >= 5:
                                track_info['avg_field_size'] = cells[3].get_text(strip=True)
                            
                            tracks.append(track_info)
                            
            logger.info(f"Found {len(tracks)} tracks for {date_str}")
            return tracks
            
        except requests.RequestException as e:
            logger.error(f"Error fetching daily tracks for {date_str}: {e}")
            return []
    
    def _extract_track_slug(self, url):
        """URL'den pist slug'ını çıkarır"""
        # /entries-results/santa-anita/2025-09-27 -> santa-anita
        parts = url.strip('/').split('/')
        if len(parts) >= 2:
            return parts[1]
        return None
    
    def scrape_track_data(self, track_url, track_name):
        """
        Belirli bir pist sayfasından yarış verilerini çeker
        """
        try:
            response = self.session.get(track_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Pist bilgilerini al
            track_info = self._extract_track_info(soup, track_name)
            
            # Yarışları al
            races = self._extract_races(soup, track_url)
            
            return {
                'track_info': track_info,
                'races': races,
                'total_races': len(races),
                'scraped_at': datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"Error scraping {track_url}: {e}")
            return None
    
    def _extract_track_info(self, soup, track_name):
        """Pist temel bilgilerini çıkarır"""
        track_info = {'name': track_name}
        
        # Tarih bilgisi
        date_elem = soup.find('div', class_='date') or soup.find('h1')
        if date_elem:
            date_text = date_elem.get_text()
            # "Santa Anita Entries & Results for Saturday, September 27, 2025" formatından tarihi çıkar
            date_match = re.search(r'(\w+day,\s+\w+\s+\d+,\s+\d{4})', date_text)
            if date_match:
                track_info['race_date'] = date_match.group(1)
        
        # Pist resmi ve açıklaması
        img_elem = soup.find('img', alt=re.compile(track_name, re.I))
        if img_elem:
            track_info['image_url'] = img_elem.get('src')
        
        # Pist açıklaması
        desc_elem = soup.find('p', string=re.compile(track_name))
        if desc_elem:
            track_info['description'] = desc_elem.get_text(strip=True)
        
        return track_info
    
    def _extract_races(self, soup, base_url):
        """Yarış verilerini çıkarır"""
        races = []
        
        # Debug için H2 başlıklarını yazdır
        h2_tags = soup.find_all('h2')
        
        for h2 in h2_tags:
            h2_text = h2.get_text()
            if 'Race' in h2_text and '#' in h2_text:
                logger.info(f"Found race header: {repr(h2_text)}")
                race_data = self._extract_single_race(h2, base_url)
                if race_data:
                    races.append(race_data)
                    logger.info(f"Successfully parsed race {race_data.get('race_number')}")
        
        return races
    
    def _extract_single_race(self, race_header, base_url):
        """Tek bir yarış verilerini çıkarır"""
        try:
            # Yarış numarasını çıkar
            header_text = race_header.get_text()
            logger.info(f"Processing header: {repr(header_text)}")
            
            # Yarış numarasını çıkar - "Race # 1, 1:00 PM" formatında
            race_num_match = re.search(r'Race\s*#?\s*(\d+)', header_text)
            if not race_num_match:
                logger.warning(f"No race number found in: {header_text}")
                return None
            
            race_num = int(race_num_match.group(1))
            
            # Saati çıkar - "\n1:00 PM" formatında olabilir
            time_match = re.search(r'(\d+:\d+\s*[AP]M)', header_text)
            race_time = time_match.group(1) if time_match else "Unknown"
            
            race_data = {
                'race_number': race_num,
                'post_time': race_time,
                'entries': [],
                'results': {},
                'race_info': {}
            }
            
            logger.info(f"Found race {race_num} at {race_time}")
            
            # Sonraki elementleri kontrol et - yarış bilgileri ve tabloları bul
            current_elem = race_header
            entries_table = None
            results_table = None
            
            # 20 elemana kadar arama yap
            for i in range(20):
                current_elem = current_elem.find_next_sibling()
                if current_elem is None:
                    break
                
                # Yarış bilgilerini al
                if i == 0:  # İlk sibling genellikle yarış bilgileri
                    race_info_text = current_elem.get_text(strip=True)
                    if race_info_text:
                        race_data['race_info'] = self._parse_race_info(race_info_text)
                
                # Tabloları ara
                if hasattr(current_elem, 'find'):
                    tables = current_elem.find_all('table')
                    for j, table in enumerate(tables):
                        # Debug: Tablo içeriğini yazdır
                        first_rows = table.find_all('tr')[:2]
                        table_preview = []
                        for row in first_rows:
                            cells = [cell.get_text(strip=True)[:15] for cell in row.find_all(['td', 'th'])[:3]]
                            table_preview.append(cells)
                        logger.info(f"Race {race_num}, Element {i}, Table {j}: {table_preview}")
                        
                        if self._is_entries_table(table) and not entries_table:
                            entries_table = table
                            logger.info(f"Found entries table for race {race_num}")
                        elif self._is_results_table(table) and not results_table:
                            results_table = table
                            logger.info(f"Found results table for race {race_num}")
            
            # Entries'leri parse et
            if entries_table:
                race_data['entries'] = self._extract_race_entries(entries_table)
                logger.info(f"Extracted {len(race_data['entries'])} entries for race {race_num}")
            else:
                logger.warning(f"No entries table found for race {race_num}")
            
            # Sonuçları parse et
            if results_table:
                race_data['results'] = self._extract_race_results(results_table)
                logger.info(f"Extracted results for race {race_num}")
            
            return race_data
            
        except Exception as e:
            logger.error(f"Error extracting race data: {e}")
            return None
    
    def _parse_race_info(self, info_text):
        """Yarış bilgilerini parse eder"""
        info = {}
        
        # Mesafe çıkar (6F, 1M, 1 1/4 m gibi)
        distance_match = re.search(r'(\d+(?:\s*\d+/\d+)?\s*[MFmf])', info_text)
        if distance_match:
            info['distance'] = distance_match.group(1)
        
        # Pist tipi (Dirt, Turf)
        surface_match = re.search(r'(Dirt|Turf|dirt|turf)', info_text)
        if surface_match:
            info['surface'] = surface_match.group(1).title()
        
        # Purse bilgisi
        purse_match = re.search(r'Purse:\s*\$?([\d,]+)', info_text)
        if purse_match:
            info['purse'] = purse_match.group(1)
        
        # Yarış tipi (Maiden, Allowance, Stakes vs.)
        info['race_type'] = info_text
        
        return info
    
    def _is_entries_table(self, table):
        """Tablonun entries tablosu olup olmadığını kontrol eder"""
        # İlk birkaç satırı kontrol et
        rows = table.find_all('tr')
        if len(rows) < 2:
            return False
        
        # İlk satır başlık olabilir, 2. satırı da kontrol et
        for row in rows[:3]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                # Bu sitede format: ['', '1', 'Tiger of the Sea'] şeklinde
                # İlk hücre boş, ikinci post position, üçüncü at ismi
                
                # Tüm hücreleri kontrol et
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    
                    # Post position arayalım (sayı)
                    if cell_text.isdigit() and 1 <= int(cell_text) <= 20:
                        # Post position bulundu, sonraki hücrede at ismi var mı?
                        if i + 1 < len(cells):
                            next_cell_text = cells[i + 1].get_text(strip=True)
                            
                            # At ismi kontrolü
                            if (len(next_cell_text) > 3 and 
                                any(char.isalpha() for char in next_cell_text) and
                                not next_cell_text.startswith('$') and
                                'Win' not in next_cell_text and
                                'Place' not in next_cell_text):
                                
                                logger.info(f"Entries table detected - Post: '{cell_text}', Horse: '{next_cell_text[:20]}'")
                                return True
        
        return False
    
    def _extract_race_entries(self, table):
        """Yarış katılımcılarını çıkarır"""
        entries = []
        
        rows = table.find_all('tr')
        logger.info(f"Processing {len(rows)} rows in entries table")
        
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            logger.info(f"Row {row_idx}: {[cell.get_text(strip=True)[:20] for cell in cells[:5]]}")
            
            if len(cells) >= 3:
                entry = {}
                
                # Bu sitede format: ['', '1', 'Tiger of the Sea(52) Smiling Tiger', 'trainer jokey', 'odds']
                # Post position'ı bul
                post_pos_found = False
                
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    
                    if cell_text.isdigit() and 1 <= int(cell_text) <= 20 and not post_pos_found:
                        entry['post_position'] = int(cell_text)
                        entry['program_number'] = int(cell_text)  # Genellikle aynı
                        post_pos_found = True
                        
                        # Sonraki hücrede at ismi olmalı
                        if i + 1 < len(cells):
                            horse_cell = cells[i + 1].get_text(strip=True)
                            entry['horse_info'] = self._parse_horse_info(horse_cell)
                        
                        # Trainer/Jockey (bir sonraki hücre)
                        if i + 2 < len(cells):
                            trainer_jockey = cells[i + 2].get_text(strip=True)
                            if trainer_jockey and len(trainer_jockey) > 3:
                                entry['trainer_jockey'] = trainer_jockey
                        
                        # Odds (son hücre veya bir önceki)
                        if len(cells) > i + 3:
                            odds_text = cells[-1].get_text(strip=True)
                            if odds_text and ('/' in odds_text or odds_text.replace('.', '').isdigit()):
                                entry['morning_line'] = odds_text
                        
                        break
                
                if post_pos_found and 'horse_info' in entry:
                    entries.append(entry)
                    logger.info(f"Added entry: Post {entry['post_position']} - {entry['horse_info'].get('horse_name', 'Unknown')}")
        
        logger.info(f"Total entries extracted: {len(entries)}")
        return entries
    
    def _parse_horse_info(self, horse_text):
        """At bilgisini parse eder (isim, speed figure, sire)"""
        info = {'raw_text': horse_text}
        
        # Speed figure'ı çıkar (parantez içindeki sayı)
        speed_match = re.search(r'\((\d+)\)', horse_text)
        if speed_match:
            info['speed_figure'] = int(speed_match.group(1))
        
        # At ismini çıkar (genellikle ilk kelime(ler))
        horse_match = re.search(r'^([^(]+)', horse_text)
        if horse_match:
            info['horse_name'] = horse_match.group(1).strip()
        
        # Sire ismini çıkar (genellikle speed figure'dan sonra)
        sire_match = re.search(r'\)\s*(.+)$', horse_text)
        if sire_match:
            info['sire'] = sire_match.group(1).strip()
        
        return info
    
    def _find_results_table(self, race_header):
        """Yarış sonuçları tablosunu bulur"""
        current_elem = race_header
        
        # Sonraki 15 elemana kadar arama yap
        for _ in range(15):
            current_elem = current_elem.find_next_sibling()
            if current_elem is None:
                break
                
            if hasattr(current_elem, 'find'):
                table = current_elem.find('table')
                if table and self._is_results_table(table):
                    return table
        
        return None
    
    def _is_results_table(self, table):
        """Tablonun sonuçlar tablosu olup olmadığını kontrol eder"""
        # Sonuç tablosu genellikle Win/Place/Show payoffs içerir
        table_text = table.get_text().lower()
        return any(keyword in table_text for keyword in ['win', 'place', 'show', 'exacta', 'trifecta'])
    
    def _extract_race_results(self, table):
        """Yarış sonuçlarını çıkarır"""
        results = {
            'finishing_order': [],
            'payouts': {}
        }
        
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            
            # Finishing order (at ismi, finish position, payoff)
            if len(cells) >= 3:
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Payout bilgisi varsa
                if '$' in ' '.join(cell_texts):
                    horse_name = cell_texts[0]
                    if horse_name and not horse_name.lower() in ['exacta', 'trifecta', 'superfecta', 'pick']:
                        payout_info = {
                            'horse': horse_name,
                            'payouts': {}
                        }
                        
                        # Win/Place/Show payoffs
                        for i, cell_text in enumerate(cell_texts[1:], 1):
                            if '$' in cell_text:
                                payout_type = ['win', 'place', 'show'][i-1] if i <= 3 else f'payout_{i}'
                                payout_info['payouts'][payout_type] = cell_text
                        
                        results['finishing_order'].append(payout_info)
                
                # Exotic wagers (Exacta, Trifecta, etc.)
                bet_type = cell_texts[0].lower()
                if bet_type in ['exacta', 'trifecta', 'superfecta', 'pick', 'daily double']:
                    if len(cell_texts) >= 3:
                        results['payouts'][bet_type] = {
                            'combination': cell_texts[1] if len(cell_texts) > 1 else '',
                            'payout': cell_texts[2] if len(cell_texts) > 2 else ''
                        }
        
        return results
    
    def scrape_all_tracks_for_date(self, date_str=None):
        """Belirli bir tarih için tüm pistleri scrape eder"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Starting scrape for all tracks on {date_str}")
        
        # Önce tüm pistleri al
        tracks = self.get_daily_tracks(date_str)
        
        if not tracks:
            logger.warning(f"No tracks found for {date_str}")
            return {}
        
        all_data = {}
        
        for track in tracks:
            track_name = track['name']
            track_url = track['url']
            
            logger.info(f"Scraping {track_name}...")
            
            # Rate limiting
            time.sleep(2)
            
            track_data = self.scrape_track_data(track_url, track_name)
            
            if track_data:
                all_data[track['slug'] or track_name] = track_data
                logger.info(f"Successfully scraped {track_name} - {track_data['total_races']} races")
            else:
                logger.error(f"Failed to scrape {track_name}")
        
        return all_data
    
    def save_data_to_json(self, data, filename):
        """Veriyi JSON dosyasına kaydeder"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to {filename}: {e}")
    
    def save_data_to_csv(self, data, base_filename):
        """Veriyi CSV dosyalarına kaydeder (her pist için ayrı dosya)"""
        try:
            import csv
            
            for track_slug, track_data in data.items():
                # Her yarış için bir satır
                races_data = []
                
                for race in track_data['races']:
                    race_row = {
                        'track_name': track_data['track_info']['name'],
                        'race_date': track_data['track_info'].get('race_date', ''),
                        'race_number': race.get('race_number'),
                        'post_time': race.get('post_time'),
                        'distance': race.get('race_info', {}).get('distance', ''),
                        'surface': race.get('race_info', {}).get('surface', ''),
                        'purse': race.get('race_info', {}).get('purse', ''),
                        'race_type': race.get('race_info', {}).get('race_type', ''),
                        'total_entries': len(race.get('entries', [])),
                        'has_results': bool(race.get('results', {}).get('finishing_order'))
                    }
                    races_data.append(race_row)
                
                if races_data:
                    filename = f"{base_filename}_{track_slug}.csv"
                    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                        fieldnames = ['track_name', 'race_date', 'race_number', 'post_time', 
                                    'distance', 'surface', 'purse', 'race_type', 
                                    'total_entries', 'has_results']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(races_data)
                    logger.info(f"Race data saved to {filename}")
                
                # Entries data
                entries_data = []
                for race in track_data['races']:
                    for entry in race.get('entries', []):
                        entry_row = {
                            'track_name': track_data['track_info']['name'],
                            'race_number': race.get('race_number'),
                            'post_position': entry.get('post_position'),
                            'program_number': entry.get('program_number'),
                            'horse_name': entry.get('horse_info', {}).get('horse_name', ''),
                            'speed_figure': entry.get('horse_info', {}).get('speed_figure'),
                            'sire': entry.get('horse_info', {}).get('sire', ''),
                            'trainer_jockey': entry.get('trainer_jockey', ''),
                            'morning_line': entry.get('morning_line', '')
                        }
                        entries_data.append(entry_row)
                
                if entries_data:
                    filename = f"{base_filename}_{track_slug}_entries.csv"
                    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                        fieldnames = ['track_name', 'race_number', 'post_position', 'program_number',
                                    'horse_name', 'speed_figure', 'sire', 'trainer_jockey', 'morning_line']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(entries_data)
                    logger.info(f"Entries data saved to {filename}")
                    
        except Exception as e:
            logger.error(f"Error saving CSV files: {e}")


def main():
    """Ana fonksiyon - örnek kullanım"""
    scraper = HorseRacingNationScraper()
    
    # Bugünün tarihini al
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Horse Racing Nation Scraper Starting...")
    print(f"Scraping data for {today}")
    
    # Tüm pistleri scrape et
    all_data = scraper.scrape_all_tracks_for_date(today)
    
    if all_data:
        # JSON olarak kaydet
        json_filename = f"hrn_data_{today}.json"
        scraper.save_data_to_json(all_data, json_filename)
        
        print(f"Scraping completed! Found {len(all_data)} tracks")
        for track, data in all_data.items():
            print(f"  {track}: {data['total_races']} races")
            
        print(f"\nData saved to: {json_filename}")
        print("You can also generate CSV files by uncommenting the CSV code in main()")
    else:
        print("No data found!")


if __name__ == "__main__":
    main()