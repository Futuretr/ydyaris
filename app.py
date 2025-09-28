from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import pandas as pd
import json
from datetime import datetime
import logging
# Import edilecek modüller çalışma zamanında import edilecek
import glob

# Flask uygulamasını oluştur
app = Flask(__name__)
app.config['SECRET_KEY'] = 'horse_racing_analysis_2025'

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mevcut track kodları - Güncel aktif pistler
TRACK_MAPPING = {
    'aqueduct': 'Aqueduct',
    'belmont-park': 'Belmont Park', 
    'churchill-downs': 'Churchill Downs',
    'del-mar': 'Del Mar',
    'delaware-park': 'Delaware Park',
    'gulfstream-park': 'Gulfstream Park',
    'keeneland': 'Keeneland',
    'laurel-park': 'Laurel Park',
    'oaklawn-park': 'Oaklawn Park',
    'pimlico': 'Pimlico',
    'remington-park': 'Remington Park',
    'santa-anita': 'Santa Anita',
    'saratoga': 'Saratoga',
    'woodbine': 'Woodbine',
    'will-rogers-downs': 'Will Rogers Downs',
    'camarero-race-track': 'Camarero Race Track',
    'lethbridge-rmtc': 'Lethbridge RMTC',
    'albuquerque-downs': 'Albuquerque Downs',
    'hawthorne-race-course': 'Hawthorne Race Course',
    'grants-pass-downs': 'Grants Pass Downs',
    'mountaineer': 'Mountaineer Casino Racetrack',
    'los-alamitos': 'Los Alamitos Race Course'
}

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/api/check_saved_data', methods=['POST'])
def check_saved_data():
    """Kaydedilmiş veri kontrolü"""
    try:
        data = request.get_json()
        track_code = data.get('city')
        
        if not track_code:
            return jsonify({'has_data': False, 'message': 'Track seçilmedi'})
        
        # Bugünün tarihini al
        today = datetime.now().strftime('%Y_%m_%d')
        
        # Essential dosya pattern
        essential_pattern = f"{track_code}_{today}_*_essential.csv"
        essential_files = glob.glob(essential_pattern)
        
        if not essential_files:
            return jsonify({
                'has_data': False, 
                'message': f'{TRACK_MAPPING.get(track_code, track_code)} için bugünkü veri bulunamadı'
            })
        
        # En son dosyayı al
        essential_file = sorted(essential_files)[-1]
        
        # Dosyayı analiz et
        try:
            df = pd.read_csv(essential_file)
            total_horses = len(df)
            valid_horses = len(df[df['latest_time'].notna() & df['latest_distance'].notna()])
            success_rate = round((valid_horses / total_horses * 100), 1) if total_horses > 0 else 0
            
            return jsonify({
                'has_data': True,
                'data': {
                    'city': TRACK_MAPPING.get(track_code, track_code),
                    'total_horses': total_horses,
                    'successful_horses': valid_horses,
                    'success_rate': success_rate,
                    'file_path': essential_file
                }
            })
            
        except Exception as e:
            logger.error(f"Dosya analiz hatası: {e}")
            return jsonify({'has_data': False, 'message': 'Veri dosyası okunamadı'})
            
    except Exception as e:
        logger.error(f"Veri kontrol hatası: {e}")
        return jsonify({'has_data': False, 'message': 'Veri kontrolü sırasında hata oluştu'})

@app.route('/api/scrape_and_save', methods=['POST'])
def scrape_and_save():
    """Veri çekme ve kaydetme - Essential dosyası da güncellenir"""
    try:
        data = request.get_json()
        track_code = data.get('city')
        
        if not track_code:
            return jsonify({'success': False, 'message': 'Track seçilmedi'})
        
        track_name = TRACK_MAPPING.get(track_code)
        if not track_name:
            return jsonify({'success': False, 'message': 'Geçersiz track kodu'})
        
        # Bugünün tarihini al
        today = datetime.now().strftime('%Y-%m-%d')
        today_formatted = today.replace('-', '_')
        
        # Dosya adlarını belirle
        entries_file = f"{track_code}_{today_formatted}_{track_code}_entries.csv"
        essential_file = f"{track_code}_{today_formatted}_{track_code}_essential.csv"
        
        logger.info(f"Veri çekme işlemi başlatılıyor: {track_name}")
        
        # Entries dosyası kontrolü - yoksa scraping yap
        if not os.path.exists(entries_file):
            logger.info(f"Entries dosyası bulunamadı, scraping yapılıyor: {entries_file}")
            
            # Track scraper'ı çalıştır
            try:
                import subprocess
                import sys
                current_dir = os.path.dirname(os.path.abspath(__file__))
                hrn_scraper_path = os.path.join(current_dir, 'hrn_scraper')
                
                # Önce hrn_scraper.py ile entries'leri çek
                hrn_scraper_script = os.path.join(hrn_scraper_path, 'hrn_scraper.py')
                
                if os.path.exists(hrn_scraper_script):
                    logger.info(f"Entries scraping başlatılıyor: {track_code}")
                    
                    # Tek track için scraping yap
                    success = scrape_single_track_data(track_code, today)
                    
                    if not success:
                        return jsonify({
                            'success': False, 
                            'message': f'{track_name} için bugün yarış bulunamadı. Bu piste bugün yarış olmayabilir.'
                        })
                    
                    # Entries dosyasının oluşup oluşmadığını kontrol et
                    if not os.path.exists(entries_file):
                        return jsonify({
                            'success': False, 
                            'message': f'{track_name} için bugün yarış bulunamadı veya scraping başarısız oldu.'
                        })
                else:
                    return jsonify({
                        'success': False, 
                        'message': 'Scraper dosyası bulunamadı. Sistem konfigürasyonunu kontrol edin.'
                    })
                    
            except Exception as e:
                logger.error(f"Entries scraping hatası: {e}")
                return jsonify({
                    'success': False, 
                    'message': f'Entries scraping hatası: {str(e)}'
                })
        
        # Essential dosyasını güncelle/oluştur
        logger.info("Essential dosyası güncelleniyor...")
        success = regenerate_essential_file(entries_file)
        
        if not success:
            return jsonify({'success': False, 'message': 'Essential dosyası güncellenemedi'})
        
        # Sonuçları analiz et
        if not os.path.exists(essential_file):
            return jsonify({'success': False, 'message': 'Essential dosyası oluşturulamadı'})
        
        df = pd.read_csv(essential_file)
        total_horses = len(df)
        
        # latest_finish_position kontrolü yap
        valid_horses = len(df[
            df['latest_time'].notna() & 
            df['latest_distance'].notna() & 
            df['latest_finish_position'].notna() &
            (df['latest_finish_position'] != '')
        ])
        
        success_rate = round((valid_horses / total_horses * 100), 1) if total_horses > 0 else 0
        
        logger.info(f"Essential dosyası hazır: {valid_horses}/{total_horses} at için tam veri mevcut (%{success_rate})")
        
        return jsonify({
            'success': True,
            'data': {
                'city': track_name,
                'total_horses': total_horses,
                'successful_horses': valid_horses,
                'success_rate': success_rate,
                'raw_filename': essential_file,
                'raw_download_url': f"/download_raw/{essential_file}",
                'message': f"Essential dosyası güncellendi - {valid_horses}/{total_horses} at için finish position verisi mevcut"
            }
        })
            
    except Exception as e:
        logger.error(f"API hatası: {e}")
        return jsonify({'success': False, 'message': f'Sunucu hatası: {str(e)}'})

def scrape_single_track_data(track_code, date_str):
    """Tek track için entries verilerini çek"""
    try:
        import requests
        from bs4 import BeautifulSoup
        import csv
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Track-specific URL mapping - Gerçek aktif URLler
        track_url_mapping = {
            'belmont-park': 'https://entries.horseracingnation.com/entries-results/belmont-at-aqueduct',
            'aqueduct': 'https://entries.horseracingnation.com/entries-results/belmont-at-aqueduct',
            'laurel-park': 'https://entries.horseracingnation.com/entries-results/laurel-park',
            'churchill-downs': 'https://entries.horseracingnation.com/entries-results/churchill-downs',
            'gulfstream-park': 'https://entries.horseracingnation.com/entries-results/gulfstream-park',
            'delaware-park': 'https://entries.horseracingnation.com/entries-results/delaware-park',
            'woodbine': 'https://entries.horseracingnation.com/entries-results/woodbine',
            'will-rogers-downs': 'https://entries.horseracingnation.com/entries-results/will-rogers-downs',
            'camarero-race-track': 'https://entries.horseracingnation.com/entries-results/camarero-race-track',
            'lethbridge-rmtc': 'https://entries.horseracingnation.com/entries-results/lethbridge-rmtc',
            'albuquerque-downs': 'https://entries.horseracingnation.com/entries-results/albuquerque-downs',
            'hawthorne-race-course': 'https://entries.horseracingnation.com/entries-results/hawthorne-race-course',
            'grants-pass-downs': 'https://entries.horseracingnation.com/entries-results/grants-pass-downs',
            'santa-anita': 'https://entries.horseracingnation.com/entries-results/santa-anita',
            'remington-park': 'https://entries.horseracingnation.com/entries-results/remington-park',
            'mountaineer': 'https://entries.horseracingnation.com/entries-results/mountaineer',
            'los-alamitos': 'https://entries.horseracingnation.com/entries-results/los-alamitos',
            # Diğer trackler için fallback
            'del-mar': 'https://entries.horseracingnation.com/entries-results/del-mar',
            'keeneland': 'https://entries.horseracingnation.com/entries-results/keeneland',
            'oaklawn-park': 'https://entries.horseracingnation.com/entries-results/oaklawn-park',
            'pimlico': 'https://entries.horseracingnation.com/entries-results/pimlico',
            'saratoga': 'https://entries.horseracingnation.com/entries-results/saratoga'
        }
        
        # URL'yi oluştur
        if track_code in track_url_mapping:
            url = f"{track_url_mapping[track_code]}/{date_str}"
        else:
            # Fallback - eski method
            url = f"https://www.horseracingnation.com/tracks/{track_code}/{date_str}"
        
        logger.info(f"Scraping URL: {url}")
        
        response = session.get(url, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code} hatası: {url}")
            return False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Yarış kartlarını bul - entries.horseracingnation.com için
        race_sections = soup.find_all('section', class_='race-summary') or \
                       soup.find_all('div', class_='race-card') or \
                       soup.find_all('section', class_='race') or \
                       soup.find_all('div', attrs={'data-race': True})
        
        if not race_sections:
            # Alternatif: H2 yarış başlıklarını kullan (scraper ile uyumlu)
            h2_headers = soup.find_all('h2')
            race_sections = []
            for h2 in h2_headers:
                h2_text = h2.get_text()
                if 'Race' in h2_text and '#' in h2_text:
                    # Bu bir yarış başlığı, sonraki elementi al
                    next_elem = h2.find_next_sibling()
                    if next_elem:
                        race_sections.append(next_elem)
                    else:
                        race_sections.append(h2)
            logger.info(f"H2 alternatif yöntemiyle {len(race_sections)} yarış başlığı bulundu")
        
        if not race_sections:
            logger.info(f"Bu piste bugün yarış yok: {track_code}")
            return False
        
        logger.info(f"Scraper kullanılarak veri çekiliyor...")
        
        # HRN Scraper'ı kullan - daha doğru veri için
        try:
            import sys
            current_dir = os.path.dirname(os.path.abspath(__file__))
            hrn_scraper_path = os.path.join(current_dir, 'hrn_scraper')
            if hrn_scraper_path not in sys.path:
                sys.path.insert(0, hrn_scraper_path)
            
            from hrn_scraper import HorseRacingNationScraper
            scraper = HorseRacingNationScraper()
            
            track_name = track_url_mapping.get(track_code, track_code)
            track_data = scraper.scrape_track_data(url, track_name)
            
            if not track_data or not track_data.get('races'):
                logger.error(f"Scraper ile veri çekilemedi: {track_code}")
                return False
            
            races = track_data['races']
            logger.info(f"{len(races)} yarış bulundu (scraper ile)")
            
            # Entries verilerini topla
            entries_data = []
            today_formatted = date_str.replace('-', '_')
            
            for race in races:
                race_number = race.get('race_number', 0)
                entries = race.get('entries', [])
                
                for entry in entries:
                    try:
                        # horse_info içinden bilgileri çıkar
                        horse_info = entry.get('horse_info', {})
                        horse_name = horse_info.get('horse_name', '')
                        sire = horse_info.get('sire', '')
                        speed_figure = horse_info.get('speed_figure', '')
                        
                        # trainer_jockey'yi parse et
                        trainer_jockey_raw = entry.get('trainer_jockey', '')
                        
                        entry_row = {
                            'track_name': track_code,
                            'race_number': str(race_number),
                            'post_position': str(entry.get('post_position', '')),
                            'program_number': str(entry.get('program_number', '')),
                            'horse_name': horse_name,
                            'speed_figure': str(speed_figure),
                            'sire': sire,
                            'trainer_jockey': trainer_jockey_raw,
                            'morning_line': entry.get('morning_line', '')
                        }
                        entries_data.append(entry_row)
                        
                    except Exception as e:
                        logger.debug(f"Entry verisi çekme hatası: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Scraper import/kullanım hatası: {e}")
            return False
        
        if not entries_data:
            logger.error("Hiç at verisi çekilemedi")
            return False
        
        # CSV dosyasını kaydet
        filename = f"{track_code}_{today_formatted}_{track_code}_entries.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['track_name', 'race_number', 'post_position', 'program_number',
                        'horse_name', 'speed_figure', 'sire', 'trainer_jockey', 'morning_line']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entries_data)
        
        logger.info(f"✅ {len(entries_data)} at verisi çekildi: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Scraping hatası: {e}")
        return False

def ensure_essential_file_updated(track_code, today):
    """Essential dosyasının güncel olduğundan emin ol"""
    try:
        # Dosya yollarını oluştur
        today_formatted = today.replace('-', '_')
        entries_file = f"{track_code}_{today_formatted}_{track_code}_entries.csv"
        essential_file = f"{track_code}_{today_formatted}_{track_code}_essential.csv"
        
        logger.info(f"Kontrol ediliyor - Entries: {entries_file}, Essential: {essential_file}")
        
        # Entries file yoksa hata
        if not os.path.exists(entries_file):
            logger.error(f"Entries file bulunamadı: {entries_file}")
            return False
        
        # Essential file yoksa oluştur
        if not os.path.exists(essential_file):
            logger.info(f"Essential file bulunamadı, oluşturuluyor: {essential_file}")
            return regenerate_essential_file(entries_file)
        
        # Essential file'ın header'ını kontrol et
        try:
            df = pd.read_csv(essential_file, nrows=0)  # Sadece header oku
            logger.info(f"Essential file mevcut kolonlar: {list(df.columns)}")
            if 'latest_finish_position' not in df.columns:
                logger.info(f"Essential file güncel değil, yenileniyor: {essential_file}")
                return regenerate_essential_file(entries_file)
        except Exception as e:
            logger.warning(f"Essential file okunamadı, yenileniyor: {e}")
            return regenerate_essential_file(entries_file)
        
        logger.info("Essential file güncel, güncelleme gerekmiyor")
        return True
        
    except Exception as e:
        logger.error(f"Essential file kontrol hatası: {e}")
        return False

def regenerate_essential_file(entries_file):
    """Essential file'ı yeniden oluştur"""
    try:
        if not os.path.exists(entries_file):
            logger.error(f"Entries file bulunamadı: {entries_file}")
            return False
        
        logger.info(f"Essential file oluşturuluyor: {entries_file}")
        
        # Mevcut essential dosyasını kopyalayalım ve sadece eksik kolonları ekleyelim
        base_name = entries_file.replace('_entries.csv', '')
        old_essential_file = f"{base_name}_essential.csv"
        new_essential_file = f"{base_name}_essential_new.csv"
        output_json = f"{base_name}_essential.json"
        
        # CSV modülünü import et
        import csv
        
        # Eğer eski essential file varsa onu okuyalım
        existing_data = {}
        if os.path.exists(old_essential_file):
            try:
                with open(old_essential_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        horse_name = row.get('horse_name', '').strip()
                        if horse_name:
                            existing_data[horse_name] = row
                logger.info(f"Mevcut essential dosyasından {len(existing_data)} at verisi okundu")
            except Exception as e:
                logger.warning(f"Eski essential dosyası okunamadı: {e}")
        
        # Entries dosyasını oku
        horses = []
        with open(entries_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                horses.append(row)
        
        if not horses:
            logger.error("Entries dosyası boş")
            return False
        
        # Sadece eksik verileri çek
        results = []
        need_scraping = []
        
        for horse_data in horses:
            horse_name = horse_data.get('horse_name', '').strip()
            if not horse_name:
                continue
            
            # Eğer mevcut veride varsa ve finish_position mevcutsa kullan
            if horse_name in existing_data:
                existing_row = existing_data[horse_name]
                if existing_row.get('latest_finish_position'):
                    # Mevcut veriyi kullan ama race_number ve program_number'ı güncelle
                    result = {
                        'race_number': horse_data.get('race_number', ''),
                        'program_number': horse_data.get('program_number', ''),
                        'horse_name': horse_name,
                        'latest_surface': existing_row.get('latest_surface', ''),
                        'latest_distance': existing_row.get('latest_distance', ''),
                        'latest_time': existing_row.get('latest_time', ''),
                        'latest_finish_position': existing_row.get('latest_finish_position', '')
                    }
                    results.append(result)
                    continue
            
            # Scraping gerekiyor
            need_scraping.append(horse_data)
        
        logger.info(f"Toplam {len(horses)} at - {len(results)} mevcut, {len(need_scraping)} yeni scraping gerekli")
        
        # Yeni scraping gerekenleri işle
        if need_scraping:
            import sys
            current_dir = os.path.dirname(os.path.abspath(__file__))
            hrn_scraper_path = os.path.join(current_dir, 'hrn_scraper')
            
            if hrn_scraper_path not in sys.path:
                sys.path.insert(0, hrn_scraper_path)
            
            from horse_profile_scraper import HorseProfileScraper
            scraper = HorseProfileScraper()
            
            for i, horse_data in enumerate(need_scraping, 1):
                horse_name = horse_data.get('horse_name', '').strip()
                
                logger.info(f"[{i}/{len(need_scraping)}] Scraping: {horse_name}")
                
                try:
                    horse_info = scraper.scrape_horse_profile(horse_name)
                    
                    if horse_info and horse_info.get('race_history'):
                        # En son yarış verilerini al
                        latest_race = horse_info['race_history'][0]
                        
                        latest_surface = latest_race.get('surface', '')
                        latest_distance = latest_race.get('distance', '')  
                        latest_time = latest_race.get('time', '')
                        latest_finish_position = latest_race.get('finish_position', '')
                        
                        logger.info(f"  Debug - surface: '{latest_surface}', distance: '{latest_distance}', time: '{latest_time}', position: '{latest_finish_position}'")
                        
                        result = {
                            'race_number': horse_data.get('race_number', ''),
                            'program_number': horse_data.get('program_number', ''),
                            'horse_name': horse_name,
                            'latest_surface': latest_surface,
                            'latest_distance': latest_distance,
                            'latest_time': latest_time,
                            'latest_finish_position': latest_finish_position
                        }
                        results.append(result)
                        
                        if latest_time and latest_finish_position:
                            logger.info(f"  ✅ {latest_surface} | {latest_distance} | {latest_time} | {latest_finish_position}. sıra")
                        else:
                            logger.info(f"  ⚠️ Eksik veri - time: '{latest_time}', position: '{latest_finish_position}'")
                    else:
                        logger.info("  ❌ horse_info None döndü")
                        results.append({
                            'race_number': horse_data.get('race_number', ''),
                            'program_number': horse_data.get('program_number', ''),
                            'horse_name': horse_name,
                            'latest_surface': '',
                            'latest_distance': '',
                            'latest_time': '',
                            'latest_finish_position': ''
                        })
                        
                except Exception as e:
                    logger.error(f"  ❌ Scraping hatası: {e}")
                    results.append({
                        'race_number': horse_data.get('race_number', ''),
                        'program_number': horse_data.get('program_number', ''),
                        'horse_name': horse_name,
                        'latest_surface': '',
                        'latest_distance': '',
                        'latest_time': '',
                        'latest_finish_position': ''
                    })
        
        # Sonuçları kaydet
        fieldnames = [
            'race_number', 
            'program_number', 
            'horse_name',
            'latest_surface',
            'latest_distance',
            'latest_time',
            'latest_finish_position'
        ]
        
        # CSV'ye kaydet
        with open(old_essential_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        # JSON'a kaydet
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        successful_count = len([r for r in results if r['latest_time']])
        logger.info(f"Essential file güncellendi: {successful_count}/{len(results)} başarılı")
        
        return True
            
    except Exception as e:
        logger.error(f"Essential file oluşturma hatası: {e}")
        return False

@app.route('/api/calculate_from_saved', methods=['POST'])
def calculate_from_saved():
    """Kaydedilmiş verilerden hesaplama yap"""
    try:
        data = request.get_json()
        track_code = data.get('city')
        
        if not track_code:
            return jsonify({'success': False, 'message': 'Track seçilmedi'})
        
        # Bugünün tarihini al
        today = datetime.now().strftime('%Y_%m_%d')
        
        # Essential dosyayı bul
        essential_pattern = f"{track_code}_{today}_*_essential.csv"
        essential_files = glob.glob(essential_pattern)
        
        if not essential_files:
            return jsonify({'success': False, 'message': 'Essential dosyası bulunamadı. Önce "Veri Çek" butonunu kullanarak verileri güncelleyin.'})
        
        essential_file = sorted(essential_files)[-1]
        
        # Essential file'da latest_finish_position kontrolü
        try:
            df_check = pd.read_csv(essential_file, nrows=0)
            if 'latest_finish_position' not in df_check.columns:
                return jsonify({'success': False, 'message': 'Essential dosyası güncel değil. "Veri Çek" butonunu kullanarak verileri güncelleyin.'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Essential dosyası okunamıyor: {str(e)}'})
        
        # Hesaplamaları yap
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        hrn_scraper_path = os.path.join(current_dir, 'hrn_scraper')
        sys.path.insert(0, hrn_scraper_path)
        
        # TURKISH STYLE CALCULATOR KULLAN - Sadece bu yöntem aktif!
        from american_horse_calculator_turkish_style import load_horses_from_csv, process_horses_data_turkish_style, group_by_race_and_sort
        
        horses_list = load_horses_from_csv(essential_file)
        logger.info(f"Loaded {len(horses_list) if horses_list else 0} horses from CSV - TURKISH STYLE CALCULATION")
        
        if not horses_list:
            return jsonify({'success': False, 'message': 'Veri okunamadı'})
        
        # Column mapping for Turkish Style
        for horse in horses_list:
            if 'latest_distance' in horse:
                horse['profile_distance'] = horse['latest_distance']
            if 'latest_time' in horse:
                horse['profile_time'] = horse['latest_time']
            if 'latest_surface' in horse:
                horse['profile_surface'] = horse['latest_surface']
            # latest_finish_position zaten doğru isimde, mapping gerekmez
        
        # TURKISH STYLE ile hesaplama yap
        logger.info("Starting Turkish Style horse data processing...")
        results = process_horses_data_turkish_style(horses_list)
        logger.info(f"Turkish Style processed {len(results)} horses")
        
        logger.info("Starting race grouping...")
        grouped_results = group_by_race_and_sort(results)
        logger.info(f"Grouped into {len(grouped_results)} races")
        
        # Web formatına çevir
        logger.info("Converting to web format...")
        web_data = convert_to_web_format(grouped_results, results)
        logger.info(f"Web data created with {len(web_data.get('races', []))} races")
        
        return jsonify(web_data)
        
    except Exception as e:
        logger.error(f"Hesaplama hatası: {e}")
        return jsonify({'success': False, 'message': f'Hesaplama hatası: {str(e)}'})

@app.route('/api/scrape_and_calculate', methods=['POST'])
def scrape_and_calculate():
    """Veri çek ve hesapla"""
    try:
        data = request.get_json()
        track_code = data.get('city')
        
        if not track_code:
            return jsonify({'success': False, 'message': 'Track seçilmedi'})
        
        # Bugünün tarihini al  
        today = datetime.now().strftime('%Y-%m-%d')
        track_name = TRACK_MAPPING.get(track_code, track_code)
        
        # Scraping ve hesaplama yap
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        hrn_scraper_path = os.path.join(current_dir, 'hrn_scraper')
        sys.path.insert(0, hrn_scraper_path)
        
        # Interactive calculator da Turkish Style kullanacak şekilde güncellenmiştir
        from american_interactive_calculator import scrape_and_calculate_track
        
        output_file = scrape_and_calculate_track(track_code, track_name, today)
        
        if not output_file:
            return jsonify({'success': False, 'message': 'İşlem başarısız'})
        
        # Sonuçları oku ve web formatına çevir
        df = pd.read_csv(output_file)
        results = df.to_dict('records')
        
        # Gruplama
        grouped_results = {}
        for result in results:
            race_key = f"{result['track']}_{result['date']}_R{result['race_number']}"
            if race_key not in grouped_results:
                grouped_results[race_key] = []
            grouped_results[race_key].append(result)
        
        # Web formatına çevir
        web_data = convert_to_web_format(grouped_results, results)
        
        return jsonify(web_data)
        
    except Exception as e:
        logger.error(f"Scrape ve calculate hatası: {e}")
        return jsonify({'success': False, 'message': f'İşlem hatası: {str(e)}'})

def convert_to_web_format(grouped_results, all_results):
    """Backend sonuçlarını web formatına çevir"""
    races = []
    total_horses = len(all_results)
    valid_horses = len([r for r in all_results if r['performance_score'] != 'Invalid'])
    success_rate = round((valid_horses / total_horses * 100), 1) if total_horses > 0 else 0
    
    # Yarışları sırala (race_number'a göre)
    race_keys = sorted(grouped_results.keys(), key=lambda x: int(x.split('_R')[1]))
    
    for race_key in race_keys:
        race_horses = grouped_results[race_key]
        
        # Atları performance score'a göre sırala (düşükten yükseğe)
        sorted_horses = sorted(race_horses, key=lambda x: float(x['performance_score']) if x['performance_score'] != 'Invalid' else 9999)
        
        web_horses = []
        for horse in sorted_horses:
            # NaN ve geçersiz değerleri temizle
            def clean_value(value, default='-'):
                if value is None:
                    return default
                if isinstance(value, float):
                    import math
                    if math.isnan(value) or math.isinf(value):
                        return default
                if value == '' or str(value).strip() == '':
                    return default
                return str(value)
            
            # Performance score için özel temizleme
            perf_score = horse.get('performance_score', 'Invalid')
            if perf_score != 'Invalid':
                try:
                    perf_score_float = float(perf_score)
                    import math
                    if math.isnan(perf_score_float) or math.isinf(perf_score_float):
                        perf_score = 'Invalid'
                        skor_value = None
                    else:
                        skor_value = perf_score_float
                except:
                    perf_score = 'Invalid'
                    skor_value = None
            else:
                skor_value = None
            
            # Win chance hesaplama - güvenli şekilde
            win_chance = 0
            if skor_value is not None and isinstance(skor_value, (int, float)):
                win_chance = min(max(skor_value * 10, 0), 100)  # 0-100 arasında sınırla
            
            web_horse = {
                'name': clean_value(horse.get('horse_name'), 'Bilinmiyor'),
                'number': clean_value(horse.get('program_number'), '0'),
                'jockey': clean_value(horse.get('jockey'), '-'),
                'trainer': clean_value(horse.get('trainer'), '-'),
                'form': clean_value(horse.get('form'), 'N/A'),
                'score': skor_value if skor_value is not None else 0,
                'win_chance': win_chance,
                'track': clean_value(horse.get('track'), '-'),
                'distance': clean_value(horse.get('profile_distance'), '-'),
                'surface': clean_value(horse.get('profile_surface'), '-'),
                'finish_position': clean_value(horse.get('latest_finish_position'), '-')
            }
            web_horses.append(web_horse)
        
        # Race number'ı çıkar
        race_number = race_key.split('_R')[1] if '_R' in race_key else (len(races) + 1)
        
        races.append({
            'race_number': race_number,
            'distance': 'N/A',  # Bu bilgi yoksa default
            'surface': 'N/A',   # Bu bilgi yoksa default
            'horses': web_horses
        })
    
    return {
        'success': True,
        'races': races,
        'summary_stats': {
            'total_races': len(races),
            'total_horses': total_horses,
            'avg_score': sum([h.get('score', 0) for r in races for h in r['horses'] if h.get('score') is not None]) / max(valid_horses, 1) if valid_horses > 0 else 0,
            'top_horses': len([h for r in races for h in r['horses'] if h.get('score') is not None and h.get('score') >= 8])
        }
    }

@app.route('/download_csv/<track_code>')
def download_csv(track_code):
    """CSV dosyası indir"""
    try:
        # En son hesaplanan dosyayı bul
        today = datetime.now().strftime('%Y_%m_%d')
        pattern = f"american_{track_code}_{today}_*.csv"
        files = glob.glob(pattern)
        
        if not files:
            return "Dosya bulunamadı", 404
        
        latest_file = sorted(files)[-1]
        return send_file(latest_file, as_attachment=True, download_name=f"{track_code}_analiz_sonuclari.csv")
        
    except Exception as e:
        logger.error(f"CSV download hatası: {e}")
        return "Dosya indirme hatası", 500

@app.route('/download_raw/<filename>')
def download_raw(filename):
    """Ham veri dosyası indir"""
    try:
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            return "Dosya bulunamadı", 404
    except Exception as e:
        logger.error(f"Raw download hatası: {e}")
        return "Dosya indirme hatası", 500

@app.route('/test_calculate')
def test_calculate():
    """Test endpoint to debug calculation issues"""
    try:
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        hrn_scraper_path = os.path.join(current_dir, 'hrn_scraper')
        sys.path.insert(0, hrn_scraper_path)
        
        from american_horse_calculator_turkish_style import load_horses_from_csv, process_horses_data_turkish_style, group_by_race_and_sort
        
        # Santa Anita essential dosyasını test et
        essential_file = "santa-anita_2025_09_28_santa-anita_essential.csv"
        horses_list = load_horses_from_csv(essential_file)
        
        if not horses_list:
            return f"❌ No horses loaded from {essential_file}"
        
        # Column mapping
        for horse in horses_list:
            if 'latest_distance' in horse:
                horse['profile_distance'] = horse['latest_distance']
            if 'latest_time' in horse:
                horse['profile_time'] = horse['latest_time']
            if 'latest_surface' in horse:
                horse['profile_surface'] = horse['latest_surface']
            # latest_finish_position zaten doğru isimde, mapping gerekmez
        
        # Hesaplamaları yap
        results = process_horses_data_turkish_style(horses_list)
        grouped_results = group_by_race_and_sort(results)
        
        # Web formatına çevir
        web_data = convert_to_web_format(grouped_results, results)
        
        return f"""
        <h2>🐎 Debug Results</h2>
        <p><strong>Loaded horses:</strong> {len(horses_list)}</p>
        <p><strong>Processed results:</strong> {len(results)}</p>
        <p><strong>Grouped races:</strong> {len(grouped_results)}</p>
        <p><strong>Web races:</strong> {len(web_data.get('races', []))}</p>
        <p><strong>Success rate:</strong> {web_data.get('success_rate', 0)}%</p>
        
        <h3>First 3 horses from results:</h3>
        <ul>
        {"".join([f"<li>{r.get('horse_name', 'Unknown')}: {r.get('performance_score', 'N/A')} ({r.get('calculation_status', 'N/A')})</li>" for r in results[:3]])}
        </ul>
        
        <h3>Race keys:</h3>
        <ul>
        {"".join([f"<li>{key}: {len(grouped_results[key])} horses</li>" for key in list(grouped_results.keys())[:5]])}
        </ul>
        
        <h3>Web data structure:</h3>
        <pre>{str(web_data)[:1000]}...</pre>
        """
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == '__main__':
    # Flask uygulamasını çalıştır - Stream için port 5010
    app.run(debug=True, host='0.0.0.0', port=5010)